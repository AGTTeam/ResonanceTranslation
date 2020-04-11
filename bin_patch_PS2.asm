.ps2
.open "data/repack_PS2/SLPS_259.12;1",0x00122000

;Swap Circle with Cross
.org 0x002CC884
  j HACK         ;Original: li v1,0x70
  li a0,0x1C
  HACK_RETURN:
.org 0x002CC8EC
  j HACK2
;Made with PS2ControllerRemapper
.org 0x003127D8
  nop
  HACK:
  move t9,a2
  j HACK_RETURN
  HACK2:
  li v1,0x70
  lh a0,0x2(t9)
  andi a1,a0,0x9FFF
  lbu a2,0xE(t9)
  lbu a3,0xD(t9)
  andi at,a0,0x4000
  ori v1,a1,0x2000
  movn a1,v1,at
  sb a2,0xD(t9)
  andi at,a0,0x2000
  ori v1,a1,0x4000
  movn a1,v1,at
  sb a3,0xE(t9)
  jr ra
  sh a1,0x2(t9)

.close
