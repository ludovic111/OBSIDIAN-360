
/input/vmlinux-6.18.11-xenon:     file format elf64-powerpc


Disassembly of section .head.text:

Disassembly of section .text:

Disassembly of section .init.text:

c00000000102eac4 <xenon_led_init>:
c00000000102eac4:	3c 4c ff dc 	addis   r2,r12,-36
c00000000102eac8:	38 42 95 3c 	addi    r2,r2,-27332
c00000000102eacc:	fb e1 ff f8 	std     r31,-8(r1)
c00000000102ead0:	7c 08 02 a6 	mflr    r0
c00000000102ead4:	f8 01 00 10 	std     r0,16(r1)
c00000000102ead8:	38 a0 00 50 	li      r5,80
c00000000102eadc:	38 80 00 00 	li      r4,0
c00000000102eae0:	f8 21 ff 31 	stdu    r1,-208(r1)
c00000000102eae4:	38 61 00 68 	addi    r3,r1,104
c00000000102eae8:	e9 2d 0a f0 	ld      r9,2800(r13)
c00000000102eaec:	f9 21 00 b8 	std     r9,184(r1)
c00000000102eaf0:	39 20 00 00 	li      r9,0
c00000000102eaf4:	4b 02 34 55 	bl      c000000000051f48 <memset>
c00000000102eaf8:	60 00 00 00 	nop
c00000000102eafc:	3d 02 ff ec 	addis   r8,r2,-20
c00000000102eb00:	39 20 ff ff 	li      r9,-1
c00000000102eb04:	39 08 19 70 	addi    r8,r8,6512
c00000000102eb08:	39 40 00 00 	li      r10,0
c00000000102eb0c:	91 21 00 80 	stw     r9,128(r1)
c00000000102eb10:	38 61 00 60 	addi    r3,r1,96
c00000000102eb14:	f9 01 00 78 	std     r8,120(r1)
c00000000102eb18:	f9 41 00 60 	std     r10,96(r1)
c00000000102eb1c:	4b 72 ae 55 	bl      c000000000759970 <platform_device_register_full+0x8>
c00000000102eb20:	60 00 00 00 	nop
c00000000102eb24:	39 20 f0 00 	li      r9,-4096
c00000000102eb28:	7c 23 48 40 	cmpld   r3,r9
c00000000102eb2c:	40 81 00 1c 	ble     c00000000102eb48 <xenon_led_init+0x84>
c00000000102eb30:	7c 7f 1b 78 	mr      r31,r3
c00000000102eb34:	3c 62 00 34 	addis   r3,r2,52
c00000000102eb38:	38 63 97 d0 	addi    r3,r3,-26672
c00000000102eb3c:	4b 72 98 75 	bl      c0000000007583b0 <platform_driver_unregister+0x8>
c00000000102eb40:	60 00 00 00 	nop
c00000000102eb44:	48 00 00 18 	b       c00000000102eb5c <xenon_led_init+0x98>
c00000000102eb48:	3c 62 ff ec 	addis   r3,r2,-20
c00000000102eb4c:	3b e0 00 00 	li      r31,0
c00000000102eb50:	38 63 19 80 	addi    r3,r3,6528
c00000000102eb54:	4b 0a b3 31 	bl      c0000000000d9e84 <_printk+0x8>
c00000000102eb58:	60 00 00 00 	nop
c00000000102eb5c:	e9 41 00 b8 	ld      r10,184(r1)
c00000000102eb60:	e9 2d 0a f0 	ld      r9,2800(r13)
c00000000102eb64:	7d 4a 4a 79 	xor.    r10,r10,r9
c00000000102eb68:	39 20 00 00 	li      r9,0
c00000000102eb6c:	7f e3 07 b4 	extsw   r3,r31
c00000000102eb70:	41 82 00 0c 	beq     c00000000102eb7c <xenon_led_init+0xb8>
c00000000102eb74:	4b af 62 d5 	bl      c000000000b24e48 <__stack_chk_fail+0x8>
c00000000102eb78:	60 00 00 00 	nop
c00000000102eb7c:	38 21 00 d0 	addi    r1,r1,208
c00000000102eb80:	e8 01 00 10 	ld      r0,16(r1)
c00000000102eb84:	eb e1 ff f8 	ld      r31,-8(r1)
c00000000102eb88:	7c 08 03 a6 	mtlr    r0
c00000000102eb8c:	4e 80 00 20 	blr

Disassembly of section .exit.text:
