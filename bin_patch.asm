.psp
.open "data/repack/PSP_GAME/SYSDIR/BOOT.BIN",0x8803F8C

;Set the language to 1 (English) and buttonSwap to 1 (X) for syscalls
;sceImposeSetLanguageMode
.org 0x08804968
  li a0,0x1
.org 0x08804970
  li a1,0x1
;sceUtilityMsgDialogInitStart
.org 0x0880AA04
  sw s3,0x30(s0)
.org 0x0880AA0C
  sw s3,0x34(s0)
;sceUtilitySavedataInitStart
.org 0x089033E0
  sw s3,0x28(s0)
.org 0x089033E4
  sw s3,0x2C(s0)

;Swap Circle with Cross
;Call the hack code after the sceCtrlReadBufferPositive call
.org 0x08806BA0
  j HACK         ;Original: li a1,0x0
  li a3,0x0
  HACK_RETURN:
;Replace a long internal error message and swap the buttons in ram
.org 0x08993244
  nop
  HACK:
  lbu a1,0x9(s0) ;a1 = *(s0+0x9)
  srl a2,a1,5    ;a2 = a1 >> 5
  srl a3,a1,6    ;a3 = a1 >> 6
  xor a2,a2,a3   ;a2 = a2 ^ a3
  andi a2,a2,0x1 ;a2 = a2 & 0x1
  sll a3,a2,5    ;a3 = a2 << 5
  sll a2,a2,6    ;a2 = a2 << 6
  or a2,a2,a3    ;a2 = a2 | a3
  xor a1,a1,a2   ;a1 = a1 ^ a2
  sb a1,0x9(s0)  ;*(s0+0x9) = a1
  li a1,0x0
  j HACK_RETURN
  li a3,0x0

.close
