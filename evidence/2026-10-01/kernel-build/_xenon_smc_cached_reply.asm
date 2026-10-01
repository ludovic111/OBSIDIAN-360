
/input/vmlinux:     file format elf64-powerpc


Disassembly of section .head.text:

Disassembly of section .text:

c0000000008a9710 <_xenon_smc_cached_reply>:
c0000000008a9710:	3c 4c 00 56 	addis   r2,r12,86
c0000000008a9714:	38 42 93 d0 	addi    r2,r2,-27696
c0000000008a9718:	3c 82 00 34 	addis   r4,r2,52
c0000000008a971c:	88 a3 00 00 	lbz     r5,0(r3)
c0000000008a9720:	88 c4 3c b0 	lbz     r6,15536(r4)
c0000000008a9724:	7c 05 30 40 	cmplw   r5,r6
c0000000008a9728:	40 82 00 0c 	bne     c0000000008a9734 <_xenon_smc_cached_reply+0x24>
c0000000008a972c:	38 84 3c b0 	addi    r4,r4,15536
c0000000008a9730:	48 00 00 cc 	b       c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a9734:	38 c4 3c b0 	addi    r6,r4,15536
c0000000008a9738:	7c c4 33 78 	mr      r4,r6
c0000000008a973c:	8c e4 00 10 	lbzu    r7,16(r4)
c0000000008a9740:	7c 05 38 40 	cmplw   r5,r7
c0000000008a9744:	41 82 00 b8 	beq     c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a9748:	7c c4 33 78 	mr      r4,r6
c0000000008a974c:	8c e4 00 20 	lbzu    r7,32(r4)
c0000000008a9750:	7c 05 38 40 	cmplw   r5,r7
c0000000008a9754:	41 82 00 a8 	beq     c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a9758:	7c c4 33 78 	mr      r4,r6
c0000000008a975c:	8c e4 00 30 	lbzu    r7,48(r4)
c0000000008a9760:	7c 05 38 40 	cmplw   r5,r7
c0000000008a9764:	41 82 00 98 	beq     c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a9768:	7c c4 33 78 	mr      r4,r6
c0000000008a976c:	8c e4 00 40 	lbzu    r7,64(r4)
c0000000008a9770:	7c 05 38 40 	cmplw   r5,r7
c0000000008a9774:	41 82 00 88 	beq     c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a9778:	7c c4 33 78 	mr      r4,r6
c0000000008a977c:	8c e4 00 50 	lbzu    r7,80(r4)
c0000000008a9780:	7c 05 38 40 	cmplw   r5,r7
c0000000008a9784:	41 82 00 78 	beq     c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a9788:	7c c4 33 78 	mr      r4,r6
c0000000008a978c:	8c e4 00 60 	lbzu    r7,96(r4)
c0000000008a9790:	7c 05 38 40 	cmplw   r5,r7
c0000000008a9794:	41 82 00 68 	beq     c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a9798:	7c c4 33 78 	mr      r4,r6
c0000000008a979c:	8c e4 00 70 	lbzu    r7,112(r4)
c0000000008a97a0:	7c 05 38 40 	cmplw   r5,r7
c0000000008a97a4:	41 82 00 58 	beq     c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a97a8:	7c c4 33 78 	mr      r4,r6
c0000000008a97ac:	8c e4 00 80 	lbzu    r7,128(r4)
c0000000008a97b0:	7c 05 38 40 	cmplw   r5,r7
c0000000008a97b4:	41 82 00 48 	beq     c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a97b8:	7c c4 33 78 	mr      r4,r6
c0000000008a97bc:	8c e4 00 90 	lbzu    r7,144(r4)
c0000000008a97c0:	7c 05 38 40 	cmplw   r5,r7
c0000000008a97c4:	41 82 00 38 	beq     c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a97c8:	7c c4 33 78 	mr      r4,r6
c0000000008a97cc:	8c e4 00 a0 	lbzu    r7,160(r4)
c0000000008a97d0:	7c 05 38 40 	cmplw   r5,r7
c0000000008a97d4:	41 82 00 28 	beq     c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a97d8:	7c c4 33 78 	mr      r4,r6
c0000000008a97dc:	8c e4 00 b0 	lbzu    r7,176(r4)
c0000000008a97e0:	7c 05 38 40 	cmplw   r5,r7
c0000000008a97e4:	41 82 00 18 	beq     c0000000008a97fc <_xenon_smc_cached_reply+0xec>
c0000000008a97e8:	8c e6 00 c0 	lbzu    r7,192(r6)
c0000000008a97ec:	38 80 00 00 	li      r4,0
c0000000008a97f0:	7c 05 38 40 	cmplw   r5,r7
c0000000008a97f4:	40 82 00 20 	bne     c0000000008a9814 <_xenon_smc_cached_reply+0x104>
c0000000008a97f8:	7c c4 33 78 	mr      r4,r6
c0000000008a97fc:	38 a0 00 01 	li      r5,1
c0000000008a9800:	7c c4 28 2a 	ldx     r6,r4,r5
c0000000008a9804:	7c c3 29 2a 	stdx    r6,r3,r5
c0000000008a9808:	e8 84 00 08 	ld      r4,8(r4)
c0000000008a980c:	f8 83 00 08 	std     r4,8(r3)
c0000000008a9810:	38 80 00 01 	li      r4,1
c0000000008a9814:	7c 83 23 78 	mr      r3,r4
c0000000008a9818:	4e 80 00 20 	blr
	...

Disassembly of section .init.text:

Disassembly of section .exit.text:
