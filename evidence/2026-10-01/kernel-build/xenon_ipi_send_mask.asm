
/input/vmlinux:     file format elf64-powerpc


Disassembly of section .head.text:

Disassembly of section .text:

c000000000052960 <xenon_ipi_send_mask>:
c000000000052960:	3c 4c 00 db 	addis   r2,r12,219
c000000000052964:	38 42 01 80 	addi    r2,r2,384
c000000000052968:	a8 ad 00 30 	lha     r5,48(r13)
c00000000005296c:	3c c2 00 3f 	addis   r6,r2,63
c000000000052970:	e8 63 00 08 	ld      r3,8(r3)
c000000000052974:	54 a5 60 26 	slwi    r5,r5,12
c000000000052978:	e8 c6 19 70 	ld      r6,6512(r6)
c00000000005297c:	e8 84 00 00 	ld      r4,0(r4)
c000000000052980:	70 63 00 7c 	andi.   r3,r3,124
c000000000052984:	7c a5 07 b4 	extsw   r5,r5
c000000000052988:	50 83 82 9e 	rlwimi  r3,r4,16,10,15
c00000000005298c:	7c a6 2a 14 	add     r5,r6,r5
c000000000052990:	38 a5 00 10 	addi    r5,r5,16
c000000000052994:	7c 00 04 ac 	hwsync
c000000000052998:	f8 65 00 00 	std     r3,0(r5)
c00000000005299c:	a0 6d 0a ea 	lhz     r3,2794(r13)
c0000000000529a0:	28 03 00 00 	cmplwi  r3,0
c0000000000529a4:	4d 82 00 20 	beqlr
c0000000000529a8:	b0 6d 0a ec 	sth     r3,2796(r13)
c0000000000529ac:	4e 80 00 20 	blr
	...

Disassembly of section .init.text:

Disassembly of section .exit.text:
