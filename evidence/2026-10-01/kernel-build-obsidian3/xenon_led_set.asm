
/input/vmlinux:     file format elf64-powerpc


Disassembly of section .head.text:

Disassembly of section .text:

c00000000063cfe0 <xenon_led_set>:
c00000000063cfe0:	3c 4c 00 7c 	addis   r2,r12,124
c00000000063cfe4:	38 42 5b 00 	addi    r2,r2,23296
c00000000063cfe8:	7c 08 02 a6 	mflr    r0
c00000000063cfec:	fb 61 ff d8 	std     r27,-40(r1)
c00000000063cff0:	fb 81 ff e0 	std     r28,-32(r1)
c00000000063cff4:	fb a1 ff e8 	std     r29,-24(r1)
c00000000063cff8:	fb c1 ff f0 	std     r30,-16(r1)
c00000000063cffc:	f8 21 ff a1 	stdu    r1,-96(r1)
c00000000063d000:	7c 7d 1b 78 	mr      r29,r3
c00000000063d004:	3c 62 00 33 	addis   r3,r2,51
c00000000063d008:	f8 01 00 70 	std     r0,112(r1)
c00000000063d00c:	7c 9e 23 78 	mr      r30,r4
c00000000063d010:	3b 83 eb 38 	addi    r28,r3,-5320
c00000000063d014:	7f 83 e3 78 	mr      r3,r28
c00000000063d018:	48 50 85 41 	bl      c000000000b45558 <_raw_spin_lock_irqsave+0x8>
c00000000063d01c:	60 00 00 00 	nop
c00000000063d020:	7c 7b 1b 78 	mr      r27,r3
c00000000063d024:	80 7d 01 d8 	lwz     r3,472(r29)
c00000000063d028:	3c 82 00 44 	addis   r4,r2,68
c00000000063d02c:	38 c0 00 01 	li      r6,1
c00000000063d030:	38 e0 ff fe 	li      r7,-2
c00000000063d034:	88 a4 ee d8 	lbz     r5,-4392(r4)
c00000000063d038:	28 1e 00 00 	cmplwi  r30,0
c00000000063d03c:	7c c6 18 30 	slw     r6,r6,r3
c00000000063d040:	5c e3 18 3e 	rotlw   r3,r7,r3
c00000000063d044:	7c a3 18 38 	and     r3,r5,r3
c00000000063d048:	7c a5 33 78 	or      r5,r5,r6
c00000000063d04c:	38 c0 00 00 	li      r6,0
c00000000063d050:	41 82 00 08 	beq     c00000000063d058 <xenon_led_set+0x78>
c00000000063d054:	48 00 00 08 	b       c00000000063d05c <xenon_led_set+0x7c>
c00000000063d058:	38 a3 00 00 	addi    r5,r3,0
c00000000063d05c:	38 61 00 28 	addi    r3,r1,40
c00000000063d060:	98 a4 ee d8 	stb     r5,-4392(r4)
c00000000063d064:	38 80 00 03 	li      r4,3
c00000000063d068:	98 a1 00 2a 	stb     r5,42(r1)
c00000000063d06c:	7c c3 21 2a 	stdx    r6,r3,r4
c00000000063d070:	38 80 99 01 	li      r4,-26367
c00000000063d074:	f8 c3 00 08 	std     r6,8(r3)
c00000000063d078:	b0 81 00 28 	sth     r4,40(r1)
c00000000063d07c:	48 26 bb 1d 	bl      c0000000008a8b98 <xenon_smc_message+0x8>
c00000000063d080:	60 00 00 00 	nop
c00000000063d084:	7f 83 e3 78 	mr      r3,r28
c00000000063d088:	7f 64 db 78 	mr      r4,r27
c00000000063d08c:	48 50 85 dd 	bl      c000000000b45668 <_raw_spin_unlock_irqrestore+0x8>
c00000000063d090:	60 00 00 00 	nop
c00000000063d094:	38 21 00 60 	addi    r1,r1,96
c00000000063d098:	e8 01 00 10 	ld      r0,16(r1)
c00000000063d09c:	eb c1 ff f0 	ld      r30,-16(r1)
c00000000063d0a0:	7c 08 03 a6 	mtlr    r0
c00000000063d0a4:	eb a1 ff e8 	ld      r29,-24(r1)
c00000000063d0a8:	eb 81 ff e0 	ld      r28,-32(r1)
c00000000063d0ac:	eb 61 ff d8 	ld      r27,-40(r1)
c00000000063d0b0:	4e 80 00 20 	blr
	...

Disassembly of section .init.text:

Disassembly of section .exit.text:
