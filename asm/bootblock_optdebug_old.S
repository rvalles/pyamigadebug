_LVOFindResident equ -96
_LVODebug equ -114
rt_Init equ 22
header:
  dc.b "DOS"
  dc.b 0 ;fs flags
  dc.l 0 ;checksum
  dc.l 880 ;root block
;bootblock env
;a1 trackdisk ioreq
;a6 execbase
;a4,a5 something (do not clobber)
start:
  move.l a1,a3 ;ioreq backup
  move.w #$0FD8,$dff180 ;color to orange. It should never be seen.
  bset #1,$bfe001 ;filter off
  btst #6,$bfe001
  beq .normalboot ;left mouse button always boot normally
  btst #14,$dff018 ;SERDATR RBF
  bne .debug ;if serial input, debug
  btst #2,$dff016 ;POTINP DATLY
  beq .debug ;right mouse always debug
.normalboot
  lea.l .dosname(pc),a1
  jsr _LVOFindResident(a6)
  tst.l d0
  bne .good ;if d0 != 0 that's good
  move.w #$0F0F,$dff180 ;color for this odd situation
  sub.l #1,d0 ;return bad
  rts
.dosname
  dc.b "dos.library",0
.good
  move.l d0,a0 ;a0 = romtag for dos.library
  move.l rt_Init(a0),a0
  clr.l d0 ;return good
  move.w #$024D,$dff180 ;set color to show this custom bootblock is booting
  rts
.debug
  move.l #$bfd100,a0
  bclr #3,(a0) ;SEL0 select
  bset #7,(a0) ;DSKMOTOR off
  bset #3,(a0) ;SEL0 deselect
  bclr #4,(a0) ;SEL1 select
  bset #7,(a0) ;DSKMOTOR off
  bset #4,(a0) ;SEL1 deselect
  bclr #5,(a0) ;SEL2 select
  bset #7,(a0) ;DSKMOTOR off
  bset #5,(a0) ;SEL2 deselect
  bclr #6,(a0) ;SEL3 select
  bset #7,(a0) ;DSKMOTOR off
  bset #6,(a0) ;SEL3 deselect
  move.w #$00F0,$dff180 ;green screen before calling debug
  jsr _LVODebug(a6)
  move.w #$0F00,$dff180 ;red screen when returning from debug
  rts
.banner
  dc.b "bootblock_optdebug", 10
  dc.b "Exec->Debug() on serial input or right mouse button held.",10
  dc.b "Hold left mouse button to always boot normally.",10
  dc.b "Disables audio filter unless LMB held.",10
  dc.b "(C) Roc Valles Domenech",10
  dc.b "https://www.rvalles.net",0
