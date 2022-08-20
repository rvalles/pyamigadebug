header:
    dc.b "DOS"
    dc.b 0 ;fs flags
    dc.l 0 ;checksum
    dc.l 880 ;root block
;bootblock env
;a1 trackdisk ioreq
;a6 execbase
;clobbering non-scratch regs is verified to be bad.
.banner
    dc.b "bootblock_noboot", 10
    dc.b "Checksum doesn't match, so AmigaOS won't boot from it.",10
    dc.b "*** Bundled with amigaXfer.",10
    dc.b "(C) 2022 Roc Valles Domenech",10
    dc.b "https://www.rvalles.net",0
.pad
    rorg 1024
