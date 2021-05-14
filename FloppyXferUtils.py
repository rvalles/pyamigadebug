from FloppyXferIO import FloppyXferIO
class FloppyXferUtils(object):
    tracksize = 512*11
    def __init__(self, snip):
        self.snip = snip
        self.trackbuffer = self._getbuffer(self.tracksize)
        print(f"Trackbuffer: {hex(self.trackbuffer)}")
        self.drives = 4 #maximum we test for
        self.drives = self._initdrives(self.drives)
        self.fxio = FloppyXferIO(snip) #from here, floppyxfer is running exclusively.
        self.fxio.setbuffer(self.trackbuffer)
        self.fxio.setlength(self.tracksize)
        self.fxio.setioreq(self.getioreq(0))
        self.fxio.setusr(self.snip.amigacrc)
        return
    def _getbuffer(self, size):
        if self.snip.execlib.version >= 36:
            bufaddr = self.snip.execlib.AllocMem(self.tracksize, self.snip.execlib.MEMF_PUBLIC)
        else:
            bufaddr = self.snip.execlib.AllocMem(self.tracksize, self.snip.execlib.MEMF_CHIP|self.snip.execlib.MEMF_PUBLIC)
        return bufaddr
    def _getioreq(self, devname, unit):
        msgport = self.snip.execlib.createmsgport()
        print(f"msgport: {hex(msgport)}")
        ioaddr = self.snip.execlib.createiorequest(msgport)
        print(f"ioreq: {hex(ioaddr)}")
        devname = self.snip.getaddrstr("trackdisk.device")
        err = self.snip.execlib.OpenDevice(devname, unit, ioaddr, 0)
        if err:
            print(f"OpenDevice err: {hex(err)}")
            self.snip.execlib.deleteiorequest(ioaddr)
            self.snip.execlib.deletemsgport(msgport)
            return (None, None)
        return (ioaddr, msgport)
    def _initdrives(self, maxdrives):
        devname = self.snip.getaddrstr("trackdisk.device")
        self._ioreq = []
        founddrives = 0
        for unit in range(0, maxdrives):
            (ioreq, msgport) = self._getioreq(devname, unit)
            if ioreq:
                self._ioreq.append((ioreq, msgport))
                founddrives += 1
            else:
                break
        return founddrives
    def getioreq(self, unit):
        (ioreq, msgport) = self._ioreq[unit]
        return ioreq
    def close(self):
        self.fxio.exit()
        self.snip.amiga.sync()
        for (ioaddr, msgport) in self._ioreq:
            if not ioaddr:
                continue
            self.snip.execlib.CloseDevice(ioaddr)
            print(f"ioreq: {hex(ioaddr)}")
            self.snip.execlib.deleteiorequest(ioaddr)
            print("ioreq deleted")
            self.snip.execlib.deletemsgport(msgport)
            print("msgport deleted")
        self.snip.execlib.FreeMem(self.trackbuffer, self.tracksize)
        return
    def readfloppy(self):
        diskdump = bytearray()
        for track in range(0, 160):
            print(f'Reading Cyl:{track//2:02} Side:{track%2}', end='\r', flush=True)
            self.fxio.settrack(track)
            ioerr = self.fxio.trackread()
            if ioerr:
                print(f"DISK IO ERROR. {hex(ioerr)}")
                raise BufferError()
            trackdump = self.fxio.recvbuffer()
            if self.fxio.callusr() != self.snip.keysum(trackdump):
                print(f"XFER CHECKSUM ERROR.")
                raise BufferError()
            diskdump += trackdump
        print("Done    ")
        self.fxio.motoroff()
        return bytes(diskdump)
    #Verify 0:None/1:CRCxfer/2:CRCread/3:BothPointless.
    def writefloppy(self, diskdump, verify):
        if len(diskdump) != self.tracksize*160:
            print("Data isn't a standard DD floppy ADF image.")
            raise ValueError()
        for track in range(0, 160):
            print(f'Writing   Cyl:{track//2:02} Side:{track%2}', end='\r', flush=True)
            startpos = track*self.tracksize
            endpos = startpos+self.tracksize
            trackdump = diskdump[startpos:endpos]
            self.fxio.settrack(track)
            self.fxio.sendbuffer(trackdump)
            if verify%2:
                if self.fxio.callusr() != self.snip.keysum(trackdump):
                    print("VERIFY CRC ERROR.")
                    raise BufferError()
            ioerr = self.fxio.trackformat()
            if ioerr:
                print(f"WRITE IO ERROR. {hex(ioerr)}")
                raise BufferError()
        if verify&2:
            for track in range(0, 160):
                print(f'Verifying Cyl:{track//2:02} Side:{track%2}', end='\r', flush=True)
                startpos = track*self.tracksize
                endpos = startpos+self.tracksize
                trackdump = diskdump[startpos:endpos]
                self.fxio.settrack(track)
                ioerr = self.fxio.trackread()
                if ioerr:
                    print(f"VERIFY IO ERROR. {hex(ioerr)}")
                    raise BufferError()
                if self.fxio.callusr() != self.snip.keysum(trackdump):
                    print("VERIFY CRC ERROR.")
                    raise BufferError()
        print("Done     ")
        self.fxio.motoroff()
        return
