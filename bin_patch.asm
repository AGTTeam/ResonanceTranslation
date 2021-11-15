.psp
.open "data/repack/PSP_GAME/SYSDIR/BOOT.BIN",0x8803F8C

.org 0x08991104
  .area 0x49
  FONT_PATH:
  .asciiz "disc0:/PSP_GAME/USRDIR/OutGame/Ending/PS2_staff_role_ex.gmo"
  .endarea

;Jump before the sceFontOpen syscall and skip it
.org 0x0880e690
  j SCEFONT_HACK
  nop
  nop
  nop
  nop
  nop
  nop
  SCEFONT_HACK_RET:

;Replace some error codes
.org 0x089931d4
  .area 0x15f
  LORD_DEATH:
  .asciiz "Lord Death"
  LORD_DEATH_2P:
  .asciiz "2P Lord Death"
  .align

  ;Load the font path and call sceFontOpenUserFile
  SCEFONT_HACK:
  move a0,v0
  move a1,a0
  lw a0,-0xe90(s0)
  li a1,FONT_PATH
  li a2,0x1
  jal SCEFONT_SYSCALL
  move a3,sp
  j SCEFONT_HACK_RET
  nop

  ;Just an hardcoded sceFontOpenUserFile syscall
  SCEFONT_SYSCALL:
  jr ra
  .dw 0x0044028c

  ;Divide the font advancement by 64
  FONT_WIDTH:
  mfc1 a0,f14
  mtc1 a1,f14
  cvt.s.w f14,f14
  div.s f13,f13,f14
  j FONT_WIDTH_RET
  mtc1 a0,f14
  FONT_WIDTH_ADVENTURE:
  mfc1 a0,f14
  mtc1 a1,f14
  cvt.s.w f14,f14
  div.s f12,f12,f14
  mtc1 a0,f14
  j FONT_WIDTH_ADVENTURE_RET
  ;This is needed to avoid the popups crashing on weird values of f14
  li a0,1

  HARDCODED_SPACE:
  li v0,6
  jr ra
  mtc1 v0,f12

  HARDCODED_SPACE_ADVENTURE:
  li s1,5
  mtc1 s1,f12
  j HARDCODED_SPACE_ADVENTURE_RET
  cvt.s.w f12,f12

  TWEAK_ADVENTURE_TEXT:
  mtc1 a0,f12
  lw a0,0x38(sp)
  j TWEAK_ADVENTURE_TEXT_RET
  cvt.s.w f12,f12

  TWEAK_ADVENTURE_TEXT2:
  mtc1 a0,f12
  move a0,s0
  j TWEAK_ADVENTURE_TEXT2_RET
  cvt.s.w f12,f12

  SWAP_CIRCLE_CROSS:
  lbu a1,0x9(s0)
  srl a2,a1,5
  srl a3,a1,6
  xor a2,a2,a3
  andi a2,a2,0x1
  sll a3,a2,5
  sll a2,a2,6
  or a2,a2,a3
  xor a1,a1,a2
  sb a1,0x9(s0)
  li a1,0x0
  j SWAP_CIRCLE_CROSS_RET
  li a3,0x0
  .endarea

;Proper VWF using the advance setting of the PGF font
.org 0x0880f1e0
  ;Original code:
  ;lw a0,0xc(s3)  (left)
  ;lw a1,0x4(s3)  (width)
  ;addu a0,a0,a1
  ;mtc1 a0,f13
  ;cvt.s.w f13,f13
  lw a0,0x34(s3)
  mtc1 a0,f13
  cvt.s.w f13,f13
  j FONT_WIDTH
  li a1,64
  FONT_WIDTH_RET:
.org 0x0880f52c
  lw a0,0x34(a0)
  mtc1 a0,f12
  cvt.s.w f12,f12
  j FONT_WIDTH_ADVENTURE
  li a1,64
  FONT_WIDTH_ADVENTURE_RET:

;The space advancement is harcoded, for some reason
.org 0x0880ed80
  jal HARDCODED_SPACE
.org 0x0880edac
  jal HARDCODED_SPACE
.org 0x0880f3c8
  jal HARDCODED_SPACE
.org 0x0880f3f4
  jal HARDCODED_SPACE
;Keep the width always the same instead of multiplying it
.org 0x0880ed8c
  nop
  nop
.org 0x0880edB8
  nop
.org 0x0880f3d4
  nop
  nop
.org 0x0880f400
  nop
;More hardcoded space length
.org 0x088506b0
  j HARDCODED_SPACE_ADVENTURE
  nop
  HARDCODED_SPACE_ADVENTURE_RET:

;Write adventure difficulty as variable width instead of fixed width
.org 0x088f9798
  li a0,0x1
.org 0x088fe324
  li a0,0x1

;Tweak position of adventure mission text
.org 0x088f97f0
  li a0,0x68
.org 0x088fe358
  li a0,0x68
.org 0x088f9860
  j TWEAK_ADVENTURE_TEXT
  li a0,0xe2
  TWEAK_ADVENTURE_TEXT_RET:
.org 0x088fe3ec
  j TWEAK_ADVENTURE_TEXT2
  li a0,0x68
  TWEAK_ADVENTURE_TEXT2_RET:

;Hardcode Lord Death's name since it's too long to fit
BASEPTR equ 0x08804000
.org 0x08869d20
  lui v0,hi(LORD_DEATH - BASEPTR)
  addiu v0,v0,lo(LORD_DEATH - BASEPTR)
.org 0x08869eb4
  lui v0,hi(LORD_DEATH_2P - BASEPTR)
  addiu v0,v0,lo(LORD_DEATH_2P - BASEPTR)
.org 0x089a4214
  dw LORD_DEATH - BASEPTR

;Set the language to 1 (English) and buttonSwap to 1 (X) for syscalls
;sceImposeSetLanguageMode
.org 0x08804968
  li a0,0x1
.org 0x08804970
  li a1,0x1
;sceUtilityMsgDialogInitStart
.org 0x0880aa04
  sw s3,0x30(s0)
.org 0x0880aa0c
  sw s3,0x34(s0)
;sceUtilitySavedataInitStart
.org 0x089033e0
  sw s3,0x28(s0)
.org 0x089033e4
  sw s3,0x2c(s0)

;Swap Circle with Cross
;Call the code after the sceCtrlReadBufferPositive call
.org 0x08806ba0
  j SWAP_CIRCLE_CROSS
  li a3,0x0
  SWAP_CIRCLE_CROSS_RET:

;Make some room for custom code by redirecting some error strings
.org 0x0895a718
  addiu v0,v0,0x31c0
  .skip 8
  addiu v0,v0,0x31c0
  .skip 8
  addiu v0,v0,0x31c0
  .skip 8
  addiu v0,v0,0x31c0
  .skip 8
  addiu v0,v0,0x31c0
  .skip 8
  addiu v0,v0,0x31c0
  .skip 8
  addiu v0,v0,0x31c0

.close
