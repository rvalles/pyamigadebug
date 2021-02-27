**CRC-32/ISO-HDLC
*aka CRC-32, CRC-32/ADCCP, CRC-32/V-42, CRC-32/XZ, PKZIP
*a0 addr, d0 size. Returns crc32 in d0.
crc32:
  *a1 lut, d1 crc, d2 idx|value
  cmp.l #0,d0
  bne .prepare
  rts
.prepare:
  move.l d2,-(sp)
  lea.l .lut(pc),a1
  clr.l d1
  not.l d1 ;init = 0xFFFFFFFF
  sub.l #1,d0 ;for dbra
  bra .loop
.oloop
  swap d0
.loop:
  clr.w d2
  move.b (a0)+,d2
  eor.b d1,d2
  lsl.w #2,d2
  move.l (a1,d2.w),d2
  lsr.l #8,d1
  eor.l d2,d1
  dbra d0,.loop
  swap d0
  dbra d0,.oloop
  eor.l d1,d0 ;xorout = 0xFFFFFFFF
  move.l (sp)+,d2
  rts
*reciprocal lut
.lut:
  ifd crc32c
    echo "crc32c aka CRC-32/ISCSI lut selected."
    dc.l $00000000,$f26b8303,$e13b70f7,$1350f3f4,$c79a971f,$35f1141c
    dc.l $26a1e7e8,$d4ca64eb,$8ad958cf,$78b2dbcc,$6be22838,$9989ab3b
    dc.l $4d43cfd0,$bf284cd3,$ac78bf27,$5e133c24,$105ec76f,$e235446c
    dc.l $f165b798,$030e349b,$d7c45070,$25afd373,$36ff2087,$c494a384
    dc.l $9a879fa0,$68ec1ca3,$7bbcef57,$89d76c54,$5d1d08bf,$af768bbc
    dc.l $bc267848,$4e4dfb4b,$20bd8ede,$d2d60ddd,$c186fe29,$33ed7d2a
    dc.l $e72719c1,$154c9ac2,$061c6936,$f477ea35,$aa64d611,$580f5512
    dc.l $4b5fa6e6,$b93425e5,$6dfe410e,$9f95c20d,$8cc531f9,$7eaeb2fa
    dc.l $30e349b1,$c288cab2,$d1d83946,$23b3ba45,$f779deae,$05125dad
    dc.l $1642ae59,$e4292d5a,$ba3a117e,$4851927d,$5b016189,$a96ae28a
    dc.l $7da08661,$8fcb0562,$9c9bf696,$6ef07595,$417b1dbc,$b3109ebf
    dc.l $a0406d4b,$522bee48,$86e18aa3,$748a09a0,$67dafa54,$95b17957
    dc.l $cba24573,$39c9c670,$2a993584,$d8f2b687,$0c38d26c,$fe53516f
    dc.l $ed03a29b,$1f682198,$5125dad3,$a34e59d0,$b01eaa24,$42752927
    dc.l $96bf4dcc,$64d4cecf,$77843d3b,$85efbe38,$dbfc821c,$2997011f
    dc.l $3ac7f2eb,$c8ac71e8,$1c661503,$ee0d9600,$fd5d65f4,$0f36e6f7
    dc.l $61c69362,$93ad1061,$80fde395,$72966096,$a65c047d,$5437877e
    dc.l $4767748a,$b50cf789,$eb1fcbad,$197448ae,$0a24bb5a,$f84f3859
    dc.l $2c855cb2,$deeedfb1,$cdbe2c45,$3fd5af46,$7198540d,$83f3d70e
    dc.l $90a324fa,$62c8a7f9,$b602c312,$44694011,$5739b3e5,$a55230e6
    dc.l $fb410cc2,$092a8fc1,$1a7a7c35,$e811ff36,$3cdb9bdd,$ceb018de
    dc.l $dde0eb2a,$2f8b6829,$82f63b78,$709db87b,$63cd4b8f,$91a6c88c
    dc.l $456cac67,$b7072f64,$a457dc90,$563c5f93,$082f63b7,$fa44e0b4
    dc.l $e9141340,$1b7f9043,$cfb5f4a8,$3dde77ab,$2e8e845f,$dce5075c
    dc.l $92a8fc17,$60c37f14,$73938ce0,$81f80fe3,$55326b08,$a759e80b
    dc.l $b4091bff,$466298fc,$1871a4d8,$ea1a27db,$f94ad42f,$0b21572c
    dc.l $dfeb33c7,$2d80b0c4,$3ed04330,$ccbbc033,$a24bb5a6,$502036a5
    dc.l $4370c551,$b11b4652,$65d122b9,$97baa1ba,$84ea524e,$7681d14d
    dc.l $2892ed69,$daf96e6a,$c9a99d9e,$3bc21e9d,$ef087a76,$1d63f975
    dc.l $0e330a81,$fc588982,$b21572c9,$407ef1ca,$532e023e,$a145813d
    dc.l $758fe5d6,$87e466d5,$94b49521,$66df1622,$38cc2a06,$caa7a905
    dc.l $d9f75af1,$2b9cd9f2,$ff56bd19,$0d3d3e1a,$1e6dcdee,$ec064eed
    dc.l $c38d26c4,$31e6a5c7,$22b65633,$d0ddd530,$0417b1db,$f67c32d8
    dc.l $e52cc12c,$1747422f,$49547e0b,$bb3ffd08,$a86f0efc,$5a048dff
    dc.l $8ecee914,$7ca56a17,$6ff599e3,$9d9e1ae0,$d3d3e1ab,$21b862a8
    dc.l $32e8915c,$c083125f,$144976b4,$e622f5b7,$f5720643,$07198540
    dc.l $590ab964,$ab613a67,$b831c993,$4a5a4a90,$9e902e7b,$6cfbad78
    dc.l $7fab5e8c,$8dc0dd8f,$e330a81a,$115b2b19,$020bd8ed,$f0605bee
    dc.l $24aa3f05,$d6c1bc06,$c5914ff2,$37faccf1,$69e9f0d5,$9b8273d6
    dc.l $88d28022,$7ab90321,$ae7367ca,$5c18e4c9,$4f48173d,$bd23943e
    dc.l $f36e6f75,$0105ec76,$12551f82,$e03e9c81,$34f4f86a,$c69f7b69
    dc.l $d5cf889d,$27a40b9e,$79b737ba,$8bdcb4b9,$988c474d,$6ae7c44e
    dc.l $be2da0a5,$4c4623a6,$5f16d052,$ad7d5351
  else
    echo "crc32 aka CRC-32/ISO-HDLC lut selected."
    dc.l $00000000,$77073096,$ee0e612c,$990951ba,$076dc419,$706af48f
    dc.l $e963a535,$9e6495a3,$0edb8832,$79dcb8a4,$e0d5e91e,$97d2d988
    dc.l $09b64c2b,$7eb17cbd,$e7b82d07,$90bf1d91,$1db71064,$6ab020f2
    dc.l $f3b97148,$84be41de,$1adad47d,$6ddde4eb,$f4d4b551,$83d385c7
    dc.l $136c9856,$646ba8c0,$fd62f97a,$8a65c9ec,$14015c4f,$63066cd9
    dc.l $fa0f3d63,$8d080df5,$3b6e20c8,$4c69105e,$d56041e4,$a2677172
    dc.l $3c03e4d1,$4b04d447,$d20d85fd,$a50ab56b,$35b5a8fa,$42b2986c
    dc.l $dbbbc9d6,$acbcf940,$32d86ce3,$45df5c75,$dcd60dcf,$abd13d59
    dc.l $26d930ac,$51de003a,$c8d75180,$bfd06116,$21b4f4b5,$56b3c423
    dc.l $cfba9599,$b8bda50f,$2802b89e,$5f058808,$c60cd9b2,$b10be924
    dc.l $2f6f7c87,$58684c11,$c1611dab,$b6662d3d,$76dc4190,$01db7106
    dc.l $98d220bc,$efd5102a,$71b18589,$06b6b51f,$9fbfe4a5,$e8b8d433
    dc.l $7807c9a2,$0f00f934,$9609a88e,$e10e9818,$7f6a0dbb,$086d3d2d
    dc.l $91646c97,$e6635c01,$6b6b51f4,$1c6c6162,$856530d8,$f262004e
    dc.l $6c0695ed,$1b01a57b,$8208f4c1,$f50fc457,$65b0d9c6,$12b7e950
    dc.l $8bbeb8ea,$fcb9887c,$62dd1ddf,$15da2d49,$8cd37cf3,$fbd44c65
    dc.l $4db26158,$3ab551ce,$a3bc0074,$d4bb30e2,$4adfa541,$3dd895d7
    dc.l $a4d1c46d,$d3d6f4fb,$4369e96a,$346ed9fc,$ad678846,$da60b8d0
    dc.l $44042d73,$33031de5,$aa0a4c5f,$dd0d7cc9,$5005713c,$270241aa
    dc.l $be0b1010,$c90c2086,$5768b525,$206f85b3,$b966d409,$ce61e49f
    dc.l $5edef90e,$29d9c998,$b0d09822,$c7d7a8b4,$59b33d17,$2eb40d81
    dc.l $b7bd5c3b,$c0ba6cad,$edb88320,$9abfb3b6,$03b6e20c,$74b1d29a
    dc.l $ead54739,$9dd277af,$04db2615,$73dc1683,$e3630b12,$94643b84
    dc.l $0d6d6a3e,$7a6a5aa8,$e40ecf0b,$9309ff9d,$0a00ae27,$7d079eb1
    dc.l $f00f9344,$8708a3d2,$1e01f268,$6906c2fe,$f762575d,$806567cb
    dc.l $196c3671,$6e6b06e7,$fed41b76,$89d32be0,$10da7a5a,$67dd4acc
    dc.l $f9b9df6f,$8ebeeff9,$17b7be43,$60b08ed5,$d6d6a3e8,$a1d1937e
    dc.l $38d8c2c4,$4fdff252,$d1bb67f1,$a6bc5767,$3fb506dd,$48b2364b
    dc.l $d80d2bda,$af0a1b4c,$36034af6,$41047a60,$df60efc3,$a867df55
    dc.l $316e8eef,$4669be79,$cb61b38c,$bc66831a,$256fd2a0,$5268e236
    dc.l $cc0c7795,$bb0b4703,$220216b9,$5505262f,$c5ba3bbe,$b2bd0b28
    dc.l $2bb45a92,$5cb36a04,$c2d7ffa7,$b5d0cf31,$2cd99e8b,$5bdeae1d
    dc.l $9b64c2b0,$ec63f226,$756aa39c,$026d930a,$9c0906a9,$eb0e363f
    dc.l $72076785,$05005713,$95bf4a82,$e2b87a14,$7bb12bae,$0cb61b38
    dc.l $92d28e9b,$e5d5be0d,$7cdcefb7,$0bdbdf21,$86d3d2d4,$f1d4e242
    dc.l $68ddb3f8,$1fda836e,$81be16cd,$f6b9265b,$6fb077e1,$18b74777
    dc.l $88085ae6,$ff0f6a70,$66063bca,$11010b5c,$8f659eff,$f862ae69
    dc.l $616bffd3,$166ccf45,$a00ae278,$d70dd2ee,$4e048354,$3903b3c2
    dc.l $a7672661,$d06016f7,$4969474d,$3e6e77db,$aed16a4a,$d9d65adc
    dc.l $40df0b66,$37d83bf0,$a9bcae53,$debb9ec5,$47b2cf7f,$30b5ffe9
    dc.l $bdbdf21c,$cabac28a,$53b39330,$24b4a3a6,$bad03605,$cdd70693
    dc.l $54de5729,$23d967bf,$b3667a2e,$c4614ab8,$5d681b02,$2a6f2b94
    dc.l $b40bbe37,$c30c8ea1,$5a05df1b,$2d02ef8d
  endif
