
/input/vmlinux-6.18.11-xenon:     file format elf64-powerpc


Disassembly of section .head.text:

Disassembly of section .text:

c0000000008879f8 <_xenon_smc_cached_reply>:
c0000000008879f8:	3c 4c 00 56 	addis   r2,r12,86
c0000000008879fc:	38 42 06 08 	addi    r2,r2,1544
c000000000887a00:	3d 22 00 35 	addis   r9,r2,53
c000000000887a04:	3d 42 00 35 	addis   r10,r2,53
c000000000887a08:	39 4a ed b0 	addi    r10,r10,-4688
c000000000887a0c:	89 29 ee d8 	lbz     r9,-4392(r9)
c000000000887a10:	2c 09 00 00 	cmpwi   r9,0
c000000000887a14:	41 82 00 64 	beq     c000000000887a78 <_xenon_smc_cached_reply+0x80>
c000000000887a18:	39 4a 01 28 	addi    r10,r10,296
c000000000887a1c:	89 03 00 00 	lbz     r8,0(r3)
c000000000887a20:	48 00 00 14 	b       c000000000887a34 <_xenon_smc_cached_reply+0x3c>
c000000000887a24:	60 00 00 00 	nop
c000000000887a28:	8d 2a 00 10 	lbzu    r9,16(r10)
c000000000887a2c:	2c 09 00 00 	cmpwi   r9,0
c000000000887a30:	41 82 00 48 	beq     c000000000887a78 <_xenon_smc_cached_reply+0x80>
c000000000887a34:	7c 08 48 00 	cmpw    r8,r9
c000000000887a38:	40 82 ff f0 	bne     c000000000887a28 <_xenon_smc_cached_reply+0x30>
c000000000887a3c:	2c 2a 00 00 	cmpdi   r10,0
c000000000887a40:	41 82 00 30 	beq     c000000000887a70 <_xenon_smc_cached_reply+0x78>
c000000000887a44:	39 0a 00 01 	addi    r8,r10,1
c000000000887a48:	80 c8 00 08 	lwz     r6,8(r8)
c000000000887a4c:	a0 e8 00 0c 	lhz     r7,12(r8)
c000000000887a50:	39 23 00 01 	addi    r9,r3,1
c000000000887a54:	39 40 00 01 	li      r10,1
c000000000887a58:	e8 a8 00 00 	ld      r5,0(r8)
c000000000887a5c:	89 08 00 0e 	lbz     r8,14(r8)
c000000000887a60:	f8 a9 00 00 	std     r5,0(r9)
c000000000887a64:	90 c3 00 09 	stw     r6,9(r3)
c000000000887a68:	b0 e3 00 0d 	sth     r7,13(r3)
c000000000887a6c:	99 03 00 0f 	stb     r8,15(r3)
c000000000887a70:	79 43 07 e0 	clrldi  r3,r10,63
c000000000887a74:	4e 80 00 20 	blr
c000000000887a78:	39 40 00 00 	li      r10,0
c000000000887a7c:	79 43 07 e0 	clrldi  r3,r10,63
c000000000887a80:	4e 80 00 20 	blr

Disassembly of section .init.text:

Disassembly of section .exit.text:
