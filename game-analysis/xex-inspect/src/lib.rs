#![forbid(unsafe_code)]
//! Structural inspection, not authentication, decryption or execution.
use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::io::{Read, Seek, SeekFrom};

pub const MAX_HEADERS: u32 = 4096;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Error(pub &'static str);

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Storage {
    Value(u32),
    InlineWord(u32),
    External { offset: u32, size: u32 },
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OptionalHeader {
    pub key: u32,
    pub storage: Storage,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExecutionInfo {
    pub media_id: u32,
    pub version: u32,
    pub base_version: u32,
    pub title_id: u32,
    pub platform: u8,
    pub executable_table: u8,
    pub disc_number: u8,
    pub disc_count: u8,
    pub savegame_id: u32,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Report {
    pub file_size: u64,
    pub module_flags: u32,
    pub image_offset: u32,
    pub reserved: u32,
    pub security_offset: u32,
    pub security_size: u32,
    pub image_size: u32,
    pub optional_headers: Vec<OptionalHeader>,
    pub file_format: Option<(u16, u16)>,
    pub execution: Option<ExecutionInfo>,
}

fn read_at<const N: usize>(r: &mut (impl Read + Seek), offset: u64) -> Result<[u8; N], Error> {
    r.seek(SeekFrom::Start(offset))
        .map_err(|_| Error("seek failed"))?;
    let mut bytes = [0; N];
    r.read_exact(&mut bytes)
        .map_err(|_| Error("truncated or unreadable input"))?;
    Ok(bytes)
}

fn word(r: &mut (impl Read + Seek), offset: u64) -> Result<u32, Error> {
    Ok(u32::from_be_bytes(read_at(r, offset)?))
}

fn within(offset: u64, size: u64, lower: u64, upper: u64) -> Result<(), Error> {
    let end = offset.checked_add(size).ok_or(Error("range overflow"))?;
    if offset < lower || end > upper {
        return Err(Error("range outside declared headers"));
    }
    Ok(())
}

/// Caller supplies the length of the same seekable object. Reads are bounded by
/// header count, and external payloads are never allocated or dumped.
pub fn inspect(r: &mut (impl Read + Seek), file_size: u64) -> Result<Report, Error> {
    if file_size < 24 {
        return Err(Error("file shorter than XEX2 header"));
    }
    if read_at::<4>(r, 0)? != *b"XEX2" {
        return Err(Error("unsupported magic (expected XEX2)"));
    }
    let module_flags = word(r, 4)?;
    let image_offset = word(r, 8)?;
    let reserved = word(r, 12)?;
    let security_offset = word(r, 16)?;
    let count = word(r, 20)?;
    if count > MAX_HEADERS {
        return Err(Error("optional header count exceeds inspection budget"));
    }
    let table_end = 24 + u64::from(count) * 8;
    within(0, table_end, 0, u64::from(image_offset))?;
    if u64::from(image_offset) > file_size {
        return Err(Error("image offset beyond file"));
    }
    within(
        u64::from(security_offset),
        0x184,
        table_end,
        u64::from(image_offset),
    )?;
    let security_size = word(r, u64::from(security_offset))?;
    let image_size = word(r, u64::from(security_offset) + 4)?;
    if security_size < 0x184 {
        return Err(Error("security block shorter than XEX2 fixed fields"));
    }
    within(
        u64::from(security_offset),
        u64::from(security_size),
        table_end,
        u64::from(image_offset),
    )?;
    let descriptors = word(r, u64::from(security_offset) + 0x180)?;
    if 0x184 + u64::from(descriptors) * 24 > u64::from(security_size) {
        return Err(Error("page descriptors exceed security block"));
    }
    let security_end = u64::from(security_offset) + u64::from(security_size);
    let mut keys = BTreeSet::new();
    let mut ranges: BTreeMap<u64, u64> = BTreeMap::new();
    let mut optional_headers = Vec::with_capacity(count as usize);
    let mut file_format = None;
    let mut execution = None;
    for i in 0..count {
        let table_pos = 24 + u64::from(i) * 8;
        let key = word(r, table_pos)?;
        let value = word(r, table_pos + 4)?;
        if !keys.insert(key) {
            return Err(Error("duplicate optional header key"));
        }
        let storage = match key & 255 {
            0 => Storage::Value(value),
            1 => Storage::InlineWord(value),
            size_code => {
                let offset = u64::from(value);
                within(offset, 4, table_end, u64::from(image_offset))?;
                // No field may alias security data, even under a forged key.
                if offset < security_end && offset + 4 > u64::from(security_offset) {
                    return Err(Error("optional header overlaps security data"));
                }
                let size = if size_code == 255 {
                    word(r, offset)?
                } else {
                    size_code * 4
                };
                if size < 4 {
                    return Err(Error("variable header shorter than its length field"));
                }
                within(offset, u64::from(size), table_end, u64::from(image_offset))?;
                if offset < security_end && offset + u64::from(size) > u64::from(security_offset) {
                    return Err(Error("optional header overlaps security data"));
                }
                let end = offset + u64::from(size);
                if ranges
                    .range(..=offset)
                    .next_back()
                    .is_some_and(|(_, e)| *e > offset)
                    || ranges.range(offset..).next().is_some_and(|(s, _)| *s < end)
                {
                    return Err(Error("overlapping optional header payloads"));
                }
                ranges.insert(offset, end);
                if key == 0x000003ff {
                    if size < 8 {
                        return Err(Error("file format header is truncated"));
                    }
                    let b = read_at::<4>(r, offset + 4)?;
                    file_format = Some((
                        u16::from_be_bytes([b[0], b[1]]),
                        u16::from_be_bytes([b[2], b[3]]),
                    ));
                } else if key == 0x00040006 {
                    let b = read_at::<24>(r, offset)?;
                    let w = |n| u32::from_be_bytes([b[n], b[n + 1], b[n + 2], b[n + 3]]);
                    execution = Some(ExecutionInfo {
                        media_id: w(0),
                        version: w(4),
                        base_version: w(8),
                        title_id: w(12),
                        platform: b[16],
                        executable_table: b[17],
                        disc_number: b[18],
                        disc_count: b[19],
                        savegame_id: w(20),
                    });
                }
                Storage::External {
                    offset: value,
                    size,
                }
            }
        };
        optional_headers.push(OptionalHeader { key, storage });
    }
    Ok(Report {
        file_size,
        module_flags,
        image_offset,
        reserved,
        security_offset,
        security_size,
        image_size,
        optional_headers,
        file_format,
        execution,
    })
}

impl Report {
    /// Output contains only numbers and static strings, never raw blobs or paths.
    pub fn json(&self) -> String {
        let mut s = format!("{{\"format\":\"XEX2\",\"structural_check\":\"passed\",\"signature_verified\":false,\"file_size\":{},\"module_flags\":{},\"image_offset\":{},\"reserved\":{},\"security_offset\":{},\"security_size\":{},\"image_size\":{},\"optional_headers\":[",
            self.file_size, self.module_flags, self.image_offset, self.reserved, self.security_offset, self.security_size, self.image_size);
        for (n, h) in self.optional_headers.iter().enumerate() {
            if n != 0 {
                s.push(',');
            }
            write!(s, "{{\"key\":\"0x{:08x}\",", h.key).unwrap();
            match h.storage {
                Storage::Value(v) => write!(s,"\"storage\":\"value\",\"value\":{v}").unwrap(),
                Storage::InlineWord(v) => write!(s,"\"storage\":\"inline_word\",\"value\":{v}").unwrap(),
                Storage::External {offset,size} => write!(s,"\"storage\":\"external\",\"offset\":{offset},\"size\":{size},\"raw_data_omitted\":true").unwrap(),
            }
            s.push('}');
        }
        s.push(']');
        if let Some((enc, comp)) = self.file_format {
            write!(
                s,
                ",\"file_format\":{{\"encryption_type\":{enc},\"compression_type\":{comp}}}"
            )
            .unwrap();
        }
        if let Some(e) = &self.execution {
            write!(s,",\"execution\":{{\"media_id\":{},\"version\":{},\"base_version\":{},\"title_id\":{},\"platform\":{},\"executable_table\":{},\"disc_number\":{},\"disc_count\":{},\"savegame_id\":{}}}",
                e.media_id,e.version,e.base_version,e.title_id,e.platform,e.executable_table,e.disc_number,e.disc_count,e.savegame_id).unwrap();
        }
        s.push_str(",\"limitations\":[\"No authentication, image extraction or execution\",\"Unknown headers are range-checked only\",\"No genuine game sample validated yet\"]}");
        s
    }
}
