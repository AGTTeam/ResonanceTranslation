.psp
.open "data/repack/PSP_GAME/SYSDIR/BOOT.BIN",0x8803F8C

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
.org 0x089931d7
  .db 0
  .area 0x68

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
  li a1,64
  mfc1 a0,f14
  mtc1 a1,f14
  cvt.s.w f14,f14
  div.s f13,f13,f14
  j FONT_WIDTH_RET
  mtc1 a0,f14

  HARDCODED_SPACE:
  li v0,4
  jr ra
  mtc1 v0,f12
  .endarea

.org 0x08991104
  .area 0x49
  FONT_PATH:
  .asciiz "disc0:/PSP_GAME/USRDIR/OutGame/Ending/PS2_staff_role_ex.gmo"
  .endarea

;Proper VWF using the advance setting of the PGF font
.org 0x880f1e0
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
  nop
  FONT_WIDTH_RET:

;The space advancement is harcoded, for some reason
.org 0x0880ed80
  jal HARDCODED_SPACE
.org 0x0880edac
  jal HARDCODED_SPACE
;Keep the width always the same instead of multiplying it
.org 0x0880ed8c
  nop
  nop
.org 0x0880edB8
  nop

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
;Call the hack code after the sceCtrlReadBufferPositive call
.org 0x08806ba0
  j HACK         ;Original: li a1,0x0
  li a3,0x0
  HACK_RETURN:
;Replace an error message and swap the buttons in ram
.org 0x08993244
  .area 0x60
  nop
  HACK:
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
  j HACK_RETURN
  li a3,0x0
  .endarea

.close
