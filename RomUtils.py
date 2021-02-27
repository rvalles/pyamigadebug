class RomUtils(object):
    romsig = [0x11114ef9, 0x11144ef9]
    def __init__(self, **kwargs):
        amiga = kwargs["debugger"]
        self.amiga = amiga
        romaddr = 0xf80000
        romhdr = amiga.peek32(romaddr)
        romver = amiga.peek16(romaddr+12)
        romrev = amiga.peek16(romaddr+14)
        print(f"addr: {hex(romaddr)} romhdr: {hex(romhdr)} version: {romver}.{romrev}")
        if not romhdr in self.romsig:
            romhdr = amiga.peek32(romaddr)
            romaddr = 0xfc0000
            romver = amiga.peek16(romaddr+12)
            romrev = amiga.peek16(romaddr+14)
            print(f"addr: {hex(romaddr)} romhdr: {hex(romhdr)} version: {romver}.{romrev}")
        self.ver = romver
        self.rev = romrev
        if romver > 36:
            romsize = 512*1024
        elif romver < 36:
            romsize = 256*1024
        else:
            if romrev > 15:
                romsize = 512*1024
            else:
                romsize = 256*1024
        if romsize == 256*1024:
            romaddr = 0xfc0000
        self.addr = romaddr
        self.size = romsize
        return
    def getaddr(self):
        return self.addr
    def getsize(self):
        return self.size
    def getversion(self):
        return self.ver
    def getrevision(self):
        return self.rev
