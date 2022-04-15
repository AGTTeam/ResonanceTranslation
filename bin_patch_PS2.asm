.ps2
.open "data/repack_PS2/SLPS_259.12;1",0x00122000

;Replace some error code
.org 0x004903d8
  .area 0x9c
  ;Load the font advance
  LOAD_FONT_PARAMETER:
  sw zero,0xc(s0)
  lbu t6,0x7(s1)
  j LOAD_FONT_PARAMETER_RET
  sw t6,0x10(s0)

  ;Return an hardcoded length for the space
  HARDCODED_SPACE:
  jr ra
  li v0,6

  TWEAK_ADVENTURE_TEXT:
  li t7,0x90
  mtc1 t7,f12
  jr ra
  cvt.s.w f12,f12

  SWAP_CROSS_CIRCLE_PRE:
  move t9,a2
  j SWAP_CROSS_CIRCLE_PRE_RET
  SWAP_CROSS_CIRCLE:
  li v1,0x70
  lh a0,0x2(t9)
  andi a1,a0,0x9fff
  lbu a2,0xe(t9)
  lbu a3,0xd(t9)
  andi at,a0,0x4000
  ori v1,a1,0x2000
  movn a1,v1,at
  sb a2,0xd(t9)
  andi at,a0,0x2000
  ori v1,a1,0x4000
  movn a1,v1,at
  sb a3,0xe(t9)
  jr ra
  sh a1,0x2(t9)

  LORD_DEATH:
  .asciiz "Lord Death"
  LORD_DEATH_2P:
  .asciiz "2P Lord Death"
  .endarea

;The space advancement is harcoded, for some reason
.org 0x0018a4f8
  jal HARDCODED_SPACE
.org 0x0018a5a0
  jal HARDCODED_SPACE
.org 0x0018ac18
  jal HARDCODED_SPACE
.org 0x0018ac88
  jal HARDCODED_SPACE
;Keep the width always the same instead of multiplying it
.org 0x0018a51c
  nop
.org 0x0018ac3c
  nop
;More hardcoded space length
.org 0x001c3378
  li s5,5
  mtc1 s5,f0
  addiu s4,s4,0x1
  cvt.s.w f2,f2
  cvt.s.w f0,f0

;Write adventure difficulty as variable width instead of fixed width
.org 0x00240d18
  li a0,0x1
.org 0x00244ab0
  li a0,0x1

;Tweak position of adventure mission text
.org 0x00240d70
  li a0,0x90
.org 0x00244af8
  li a0,0x90
.org 0x00240e08
  jal TWEAK_ADVENTURE_TEXT
.org 0x00244b90
  jal TWEAK_ADVENTURE_TEXT

;Load the actual advancement from the font
.org 0x0018a8ac
  lw t5,0x14(t7)
  li t6,0x0
.org 0x0018add8
  lw t5,0x14(t7)
  li t6,0x0

;Load all font parameters
.org 0x0029e228
  j LOAD_FONT_PARAMETER
  .skip 4
  LOAD_FONT_PARAMETER_RET:

;Hardcode Lord Death's name since it's too long to fit
.org 0x001d4614
  lui t7,hi(LORD_DEATH)
  .skip 4
  addiu v0,t7,lo(LORD_DEATH)
.org 0x001d46f4
  lui t7,hi(LORD_DEATH_2P)
  .skip 4
  addiu v0,t7,lo(LORD_DEATH_2P)
.org 0x0048c35c
  dw LORD_DEATH

;Fix Memory Card format message being off-center
.org 0x002a5d04
  li a1,0x0

;Swap Circle with Cross
.org 0x002cc884
  ;Original: li v1,0x70
  j SWAP_CROSS_CIRCLE_PRE
  li a0,0x1c
  SWAP_CROSS_CIRCLE_PRE_RET:
.org 0x002cc8Ec
  j SWAP_CROSS_CIRCLE

;Redirect the errors we replaced to another one
.org 0x0026fadc
  addiu a1,0x3b8
.org 0x0026fb40
  addiu a1,0x3b8
.org 0x0026fbd8
  addiu a1,0x3b8

.close
