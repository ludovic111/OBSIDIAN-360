
/input/vmlinux-6.18.11-xenon:     file format elf64-powerpc


Disassembly of section .head.text:

Disassembly of section .text:

c000000000052b68 <xenon_ipi_send_mask>:
c000000000052b68:	3c 4c 00 d9 	addis   r2,r12,217
c000000000052b6c:	38 42 54 98 	addi    r2,r2,21656
c000000000052b70:	3d 22 00 40 	addis   r9,r2,64
c000000000052b74:	e9 03 00 08 	ld      r8,8(r3)
c000000000052b78:	55 08 06 7a 	rlwinm  r8,r8,0,25,29
c000000000052b7c:	e9 49 c4 30 	ld      r10,-15312(r9)
c000000000052b80:	a9 2d 00 30 	lha     r9,48(r13)
c000000000052b84:	55 29 60 26 	slwi    r9,r9,12
c000000000052b88:	39 29 00 10 	addi    r9,r9,16
c000000000052b8c:	7d 29 07 b4 	extsw   r9,r9
c000000000052b90:	7d 4a 4a 14 	add     r10,r10,r9
c000000000052b94:	7c 00 04 ac 	hwsync
c000000000052b98:	f9 0a 00 00 	std     r8,0(r10)
c000000000052b9c:	a1 2d 0a f8 	lhz     r9,2808(r13)
c000000000052ba0:	55 2a 04 3e 	clrlwi  r10,r9,16
c000000000052ba4:	2c 0a 00 00 	cmpwi   r10,0
c000000000052ba8:	4d 82 00 20 	beqlr
c000000000052bac:	b1 2d 0a fa 	sth     r9,2810(r13)
c000000000052bb0:	4e 80 00 20 	blr

Disassembly of section .init.text:

Disassembly of section .exit.text:
