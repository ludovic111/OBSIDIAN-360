
/input/vmlinux-6.18.11-xenon:     file format elf64-powerpc


Disassembly of section .head.text:

Disassembly of section .text:

Disassembly of section .init.text:

c00000000102ea8c <xenon_led_driver_init>:
c00000000102ea8c:	3c 4c ff dc 	addis   r2,r12,-36
c00000000102ea90:	38 42 95 74 	addi    r2,r2,-27276
c00000000102ea94:	3c 62 00 34 	addis   r3,r2,52
c00000000102ea98:	7c 08 02 a6 	mflr    r0
c00000000102ea9c:	38 80 00 00 	li      r4,0
c00000000102eaa0:	f8 01 00 10 	std     r0,16(r1)
c00000000102eaa4:	38 63 97 d0 	addi    r3,r3,-26672
c00000000102eaa8:	f8 21 ff e1 	stdu    r1,-32(r1)
c00000000102eaac:	4b 72 98 bd 	bl      c000000000758368 <__platform_driver_register+0x8>
c00000000102eab0:	60 00 00 00 	nop
c00000000102eab4:	38 21 00 20 	addi    r1,r1,32
c00000000102eab8:	e8 01 00 10 	ld      r0,16(r1)
c00000000102eabc:	7c 08 03 a6 	mtlr    r0
c00000000102eac0:	4e 80 00 20 	blr

Disassembly of section .exit.text:
