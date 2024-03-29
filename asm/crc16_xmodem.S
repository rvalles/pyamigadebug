;CRC-16/XMODEM
;aka CRC-16/ACORN, CRC-16/LTE, CRC-16/V-41-MSB, XMODEM, ZMODEM
;a0 addr, d0 size. Returns crc16 in d0.
crc16:
    ;a1 lut, d1w crc, d2 lutidx d3 lutvalue
    cmp.l #0,d0
    bne .prepare
    rts
.prepare:
    move.l d2,-(sp)
    lea.l .lut(pc),a1
    clr.l d1
    sub.l #1,d0 ;for dbra
    clr.w d2
    bra .loop
.oloop
    swap d0
.loop:
    clr.w d2
    move.b (a0)+,d2
    lsl.w #8,d2
    eor.w d2,d1
    move.w d1,d2
    lsr.w #8,d2
    lsl.w #1,d2 ;16bit lut entry size
    move.w (a1,d2.w),d2
    lsl.w #8,d1
    eor.w d2,d1
    dbra d0,.loop
    swap d0
    dbra d0,.oloop
    move.l d1,d0
    move.l (sp)+,d2
    rts
;non-reciprocal lut
.lut:
    dc.w $0000,$1021,$2042,$3063,$4084,$50a5,$60c6,$70e7
    dc.w $8108,$9129,$a14a,$b16b,$c18c,$d1ad,$e1ce,$f1ef
    dc.w $1231,$0210,$3273,$2252,$52b5,$4294,$72f7,$62d6
    dc.w $9339,$8318,$b37b,$a35a,$d3bd,$c39c,$f3ff,$e3de
    dc.w $2462,$3443,$0420,$1401,$64e6,$74c7,$44a4,$5485
    dc.w $a56a,$b54b,$8528,$9509,$e5ee,$f5cf,$c5ac,$d58d
    dc.w $3653,$2672,$1611,$0630,$76d7,$66f6,$5695,$46b4
    dc.w $b75b,$a77a,$9719,$8738,$f7df,$e7fe,$d79d,$c7bc
    dc.w $48c4,$58e5,$6886,$78a7,$0840,$1861,$2802,$3823
    dc.w $c9cc,$d9ed,$e98e,$f9af,$8948,$9969,$a90a,$b92b
    dc.w $5af5,$4ad4,$7ab7,$6a96,$1a71,$0a50,$3a33,$2a12
    dc.w $dbfd,$cbdc,$fbbf,$eb9e,$9b79,$8b58,$bb3b,$ab1a
    dc.w $6ca6,$7c87,$4ce4,$5cc5,$2c22,$3c03,$0c60,$1c41
    dc.w $edae,$fd8f,$cdec,$ddcd,$ad2a,$bd0b,$8d68,$9d49
    dc.w $7e97,$6eb6,$5ed5,$4ef4,$3e13,$2e32,$1e51,$0e70
    dc.w $ff9f,$efbe,$dfdd,$cffc,$bf1b,$af3a,$9f59,$8f78
    dc.w $9188,$81a9,$b1ca,$a1eb,$d10c,$c12d,$f14e,$e16f
    dc.w $1080,$00a1,$30c2,$20e3,$5004,$4025,$7046,$6067
    dc.w $83b9,$9398,$a3fb,$b3da,$c33d,$d31c,$e37f,$f35e
    dc.w $02b1,$1290,$22f3,$32d2,$4235,$5214,$6277,$7256
    dc.w $b5ea,$a5cb,$95a8,$8589,$f56e,$e54f,$d52c,$c50d
    dc.w $34e2,$24c3,$14a0,$0481,$7466,$6447,$5424,$4405
    dc.w $a7db,$b7fa,$8799,$97b8,$e75f,$f77e,$c71d,$d73c
    dc.w $26d3,$36f2,$0691,$16b0,$6657,$7676,$4615,$5634
    dc.w $d94c,$c96d,$f90e,$e92f,$99c8,$89e9,$b98a,$a9ab
    dc.w $5844,$4865,$7806,$6827,$18c0,$08e1,$3882,$28a3
    dc.w $cb7d,$db5c,$eb3f,$fb1e,$8bf9,$9bd8,$abbb,$bb9a
    dc.w $4a75,$5a54,$6a37,$7a16,$0af1,$1ad0,$2ab3,$3a92
    dc.w $fd2e,$ed0f,$dd6c,$cd4d,$bdaa,$ad8b,$9de8,$8dc9
    dc.w $7c26,$6c07,$5c64,$4c45,$3ca2,$2c83,$1ce0,$0cc1
    dc.w $ef1f,$ff3e,$cf5d,$df7c,$af9b,$bfba,$8fd9,$9ff8
    dc.w $6e17,$7e36,$4e55,$5e74,$2e93,$3eb2,$0ed1,$1ef0
