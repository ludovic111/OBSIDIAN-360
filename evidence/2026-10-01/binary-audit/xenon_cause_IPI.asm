
/input/vmlinux-6.18.11-xenon:     file format elf64-powerpc


Disassembly of section .head.text:

Disassembly of section .text:

c000000000052e90 <xenon_cause_IPI>:
c000000000052e90:	3c 4c 00 d9 	addis   r2,r12,217
c000000000052e94:	38 42 51 70 	addi    r2,r2,20848
c000000000052e98:	28 04 00 03 	cmplwi  r4,3
c000000000052e9c:	a9 4d 00 30 	lha     r10,48(r13)
c000000000052ea0:	41 81 00 60 	bgt     c000000000052f00 <xenon_cause_IPI+0x70>
c000000000052ea4:	3c e2 ff d6 	addis   r7,r2,-42
c000000000052ea8:	3d 22 00 40 	addis   r9,r2,64
c000000000052eac:	78 84 17 88 	rldic   r4,r4,2,30
c000000000052eb0:	38 e7 a8 00 	addi    r7,r7,-22528
c000000000052eb4:	55 4a 60 26 	slwi    r10,r10,12
c000000000052eb8:	7c e7 22 14 	add     r7,r7,r4
c000000000052ebc:	e9 09 c4 30 	ld      r8,-15312(r9)
c000000000052ec0:	3d 20 00 01 	lis     r9,1
c000000000052ec4:	39 4a 00 10 	addi    r10,r10,16
c000000000052ec8:	7d 29 18 30 	slw     r9,r9,r3
c000000000052ecc:	7d 4a 07 b4 	extsw   r10,r10
c000000000052ed0:	80 e7 00 20 	lwz     r7,32(r7)
c000000000052ed4:	7d 48 52 14 	add     r10,r8,r10
c000000000052ed8:	7d 29 3b 78 	or      r9,r9,r7
c000000000052edc:	7d 29 07 b4 	extsw   r9,r9
c000000000052ee0:	7c 00 04 ac 	hwsync
c000000000052ee4:	f9 2a 00 00 	std     r9,0(r10)
c000000000052ee8:	a1 4d 0a f8 	lhz     r10,2808(r13)
c000000000052eec:	55 48 04 3e 	clrlwi  r8,r10,16
c000000000052ef0:	2c 08 00 00 	cmpwi   r8,0
c000000000052ef4:	4d 82 00 20 	beqlr
c000000000052ef8:	b1 4d 0a fa 	sth     r10,2810(r13)
c000000000052efc:	4e 80 00 20 	blr
c000000000052f00:	7c 83 23 78 	mr      r3,r4
c000000000052f04:	7c 08 02 a6 	mflr    r0
c000000000052f08:	f8 01 00 10 	std     r0,16(r1)
c000000000052f0c:	f8 21 ff e1 	stdu    r1,-32(r1)
c000000000052f10:	48 00 00 ed 	bl      c000000000052ffc <ipi_to_prio.part.0+0x8>

Disassembly of section .init.text:

Disassembly of section .exit.text:
