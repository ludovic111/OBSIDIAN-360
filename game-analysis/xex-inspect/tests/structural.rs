use obsidian_xex_inspect::{inspect, Storage};
use std::io::{Cursor, Read, Seek, SeekFrom};

fn put(b: &mut [u8], offset: usize, value: u32) {
    b[offset..offset + 4].copy_from_slice(&value.to_be_bytes());
}

fn fixture() -> Vec<u8> {
    let mut b = vec![0; 0x410];
    b[..4].copy_from_slice(b"XEX2");
    put(&mut b, 4, 1);
    put(&mut b, 8, 0x400);
    put(&mut b, 16, 0x100);
    put(&mut b, 20, 5);
    for (i, (key, val)) in [
        (0x10100, 0x82001000),
        (0x10201, 0x82000000),
        (0x3ff, 0x80),
        (0x40006, 0x90),
        (0x40404, 0xb0),
    ]
    .into_iter()
    .enumerate()
    {
        put(&mut b, 24 + i * 8, key);
        put(&mut b, 28 + i * 8, val);
    }
    put(&mut b, 0x80, 8);
    b[0x84..0x88].copy_from_slice(&[0, 1, 0, 2]);
    put(&mut b, 0x9c, 0x12345678); // Arbitrary synthetic title, not an acquired game.
    b[0xa2..0xa4].copy_from_slice(&[1, 2]);
    b[0xb0..0xc0].fill(0xa5); // Synthetic sensitive payload must not be read.
    put(&mut b, 0x100, 0x184);
    put(&mut b, 0x104, 0x2000);
    b[0x108..0x280].fill(0xa5); // Synthetic opaque security data.
    b[0x400..].fill(0xcc); // Image body must not be read.
    b
}

fn parse(b: &[u8]) -> Result<obsidian_xex_inspect::Report, obsidian_xex_inspect::Error> {
    inspect(&mut Cursor::new(b), b.len() as u64)
}

#[test]
fn decodes_inline_fixed_and_variable_headers() {
    let r = parse(&fixture()).unwrap();
    assert_eq!(r.optional_headers[0].storage, Storage::Value(0x82001000));
    assert_eq!(
        r.optional_headers[1].storage,
        Storage::InlineWord(0x82000000)
    );
    assert_eq!(
        r.optional_headers[2].storage,
        Storage::External {
            offset: 0x80,
            size: 8
        }
    );
    assert_eq!(r.file_format, Some((1, 2)));
    assert_eq!(r.execution.as_ref().unwrap().title_id, 0x12345678);
    assert_eq!(r.execution.as_ref().unwrap().disc_count, 2);
    assert!(!r.json().contains("a5a5a5a5"));
}

#[test]
fn rejects_every_truncation_before_declared_image() {
    let b = fixture();
    for n in 0..0x400 {
        assert!(parse(&b[..n]).is_err(), "length {n}");
    }
}

#[test]
fn distinguishes_xex1_and_other_input() {
    let mut b = fixture();
    b[3] = b'1';
    assert_eq!(
        parse(&b).unwrap_err().0,
        "unsupported magic (expected XEX2)"
    );
}

#[test]
fn rejects_excessive_count_before_allocation() {
    let mut b = fixture();
    put(&mut b, 20, u32::MAX);
    assert_eq!(
        parse(&b).unwrap_err().0,
        "optional header count exceeds inspection budget"
    );
}

#[test]
fn rejects_duplicates_and_overlapping_payloads() {
    let mut b = fixture();
    put(&mut b, 32, 0x10100);
    assert_eq!(parse(&b).unwrap_err().0, "duplicate optional header key");
    let mut b = fixture();
    put(&mut b, 52, 0xb0);
    assert_eq!(
        parse(&b).unwrap_err().0,
        "overlapping optional header payloads"
    );
}

#[test]
fn rejects_forged_security_alias() {
    let mut b = fixture();
    put(&mut b, 52, 0x250);
    assert_eq!(
        parse(&b).unwrap_err().0,
        "optional header overlaps security data"
    );
}

#[test]
fn rejects_bad_variable_lengths_and_offsets() {
    for size in [0, 3, u32::MAX] {
        let mut b = fixture();
        put(&mut b, 0x80, size);
        assert!(parse(&b).is_err());
    }
    for offset in [0, 4, 24, 0x3ff, u32::MAX] {
        let mut b = fixture();
        put(&mut b, 44, offset);
        assert!(parse(&b).is_err());
    }
}

#[test]
fn rejects_security_lengths_and_descriptor_overflow() {
    let mut b = fixture();
    put(&mut b, 0x100, 0x183);
    assert!(parse(&b).is_err());
    let mut b = fixture();
    put(&mut b, 0x100, u32::MAX);
    assert!(parse(&b).is_err());
    let mut b = fixture();
    put(&mut b, 0x280, u32::MAX);
    assert!(parse(&b).is_err());
}

struct Guarded {
    inner: Cursor<Vec<u8>>,
    bytes: usize,
}
impl Read for Guarded {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        let start = self.inner.position();
        let end = start + buf.len() as u64;
        for (a, b) in [(0xb0, 0xc0), (0x108, 0x280), (0x400, 0x410)] {
            assert!(start >= b || end <= a, "read of omitted payload");
        }
        self.bytes += buf.len();
        self.inner.read(buf)
    }
}
impl Seek for Guarded {
    fn seek(&mut self, p: SeekFrom) -> std::io::Result<u64> {
        self.inner.seek(p)
    }
}

#[test]
fn never_reads_opaque_security_lan_or_image_bytes() {
    let mut r = Guarded {
        inner: Cursor::new(fixture()),
        bytes: 0,
    };
    inspect(&mut r, 0x410).unwrap();
    assert_eq!(r.bytes, 108);
}

#[test]
fn malformed_mutations_never_panic() {
    let source = fixture();
    let mut state = 0x12345678_u32;
    for _ in 0..10000 {
        let mut b = source.clone();
        for _ in 0..4 {
            state ^= state << 13;
            state ^= state >> 17;
            state ^= state << 5;
            let at = 4 + (state as usize % (b.len() - 4));
            b[at] ^= (state >> 24) as u8;
        }
        let _ = parse(&b);
    }
}
