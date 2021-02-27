;CRC-16/KERMIT
;aka CRC-16/CCITT, CRC-16/CCITT-TRUE, CRC-16/V-41-LSB, CRC-CCITT, KERMIT
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
    eor.b d1,d2
    lsl.w #1,d2 ;16bit lut entry size
    move.w (a1,d2.w),d2
    lsr.w #8,d1
    eor.w d2,d1
    dbra d0,.loop
    swap d0
    dbra d0,.oloop
    move.l d1,d0
    move.l (sp)+,d2
    rts
;reciprocal lut
.lut:
    dc.w $0000,$1189,$2312,$329b,$4624,$57ad,$6536,$74bf
    dc.w $8c48,$9dc1,$af5a,$bed3,$ca6c,$dbe5,$e97e,$f8f7
    dc.w $1081,$0108,$3393,$221a,$56a5,$472c,$75b7,$643e
    dc.w $9cc9,$8d40,$bfdb,$ae52,$daed,$cb64,$f9ff,$e876
    dc.w $2102,$308b,$0210,$1399,$6726,$76af,$4434,$55bd
    dc.w $ad4a,$bcc3,$8e58,$9fd1,$eb6e,$fae7,$c87c,$d9f5
    dc.w $3183,$200a,$1291,$0318,$77a7,$662e,$54b5,$453c
    dc.w $bdcb,$ac42,$9ed9,$8f50,$fbef,$ea66,$d8fd,$c974
    dc.w $4204,$538d,$6116,$709f,$0420,$15a9,$2732,$36bb
    dc.w $ce4c,$dfc5,$ed5e,$fcd7,$8868,$99e1,$ab7a,$baf3
    dc.w $5285,$430c,$7197,$601e,$14a1,$0528,$37b3,$263a
    dc.w $decd,$cf44,$fddf,$ec56,$98e9,$8960,$bbfb,$aa72
    dc.w $6306,$728f,$4014,$519d,$2522,$34ab,$0630,$17b9
    dc.w $ef4e,$fec7,$cc5c,$ddd5,$a96a,$b8e3,$8a78,$9bf1
    dc.w $7387,$620e,$5095,$411c,$35a3,$242a,$16b1,$0738
    dc.w $ffcf,$ee46,$dcdd,$cd54,$b9eb,$a862,$9af9,$8b70
    dc.w $8408,$9581,$a71a,$b693,$c22c,$d3a5,$e13e,$f0b7
    dc.w $0840,$19c9,$2b52,$3adb,$4e64,$5fed,$6d76,$7cff
    dc.w $9489,$8500,$b79b,$a612,$d2ad,$c324,$f1bf,$e036
    dc.w $18c1,$0948,$3bd3,$2a5a,$5ee5,$4f6c,$7df7,$6c7e
    dc.w $a50a,$b483,$8618,$9791,$e32e,$f2a7,$c03c,$d1b5
    dc.w $2942,$38cb,$0a50,$1bd9,$6f66,$7eef,$4c74,$5dfd
    dc.w $b58b,$a402,$9699,$8710,$f3af,$e226,$d0bd,$c134
    dc.w $39c3,$284a,$1ad1,$0b58,$7fe7,$6e6e,$5cf5,$4d7c
    dc.w $c60c,$d785,$e51e,$f497,$8028,$91a1,$a33a,$b2b3
    dc.w $4a44,$5bcd,$6956,$78df,$0c60,$1de9,$2f72,$3efb
    dc.w $d68d,$c704,$f59f,$e416,$90a9,$8120,$b3bb,$a232
    dc.w $5ac5,$4b4c,$79d7,$685e,$1ce1,$0d68,$3ff3,$2e7a
    dc.w $e70e,$f687,$c41c,$d595,$a12a,$b0a3,$8238,$93b1
    dc.w $6b46,$7acf,$4854,$59dd,$2d62,$3ceb,$0e70,$1ff9
    dc.w $f78f,$e606,$d49d,$c514,$b1ab,$a022,$92b9,$8330
    dc.w $7bc7,$6a4e,$58d5,$495c,$3de3,$2c6a,$1ef1,$0f78
