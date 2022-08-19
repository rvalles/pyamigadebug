import struct
class FloppyUtils(object):
    def __init__(self, **kwargs):
        self.amiga = kwargs["debugger"]
        self.execlib = kwargs["execlib"]
        self.snip = kwargs["snippets"]
    def bootblocksum(self, data):
        cksum = 0
        mask = (1 << 32) - 1
        for i in struct.unpack('>256I', data):
            cksum += i
            if cksum > mask:
                cksum += 1
                cksum &= mask
        cksum = (~cksum) & mask
        return cksum
    def readfloppy(self, floppy):
        #read whole floppy
        size = 512 * 1760
        if self.execlib.version >= 36:
            bufaddr = self.execlib.AllocMem(size, self.execlib.MEMF_PUBLIC)
        else:
            bufaddr = self.execlib.AllocMem(size, self.execlib.MEMF_CHIP|self.execlib.MEMF_PUBLIC)
        print(f"buffer addr: {hex(bufaddr)}")
        ioerr = floppy.clear()
        print(f"clear ioerr: {ioerr}")
        ioerr = floppy.read(bufaddr, size, 0)
        print(f"read ioerr: {ioerr}")
        ioerr = floppy.motoroff()
        print(f"motor off ioerr: {ioerr}")
        blockdump = self.snip.verifiedreadmem(bufaddr, size)
        self.execlib.FreeMem(bufaddr, size)
        return blockdump
    def writefloppyonego(self, floppy, blockdump):
        #write whole floppy
        size = len(blockdump)
        if self.execlib.version >= 36:
            bufaddr = self.execlib.AllocMem(size, self.execlib.MEMF_PUBLIC)
        else:
            bufaddr = self.execlib.AllocMem(size, self.execlib.MEMF_CHIP|self.execlib.MEMF_PUBLIC)
        print(f"buffer addr: {hex(bufaddr)}")
        self.snip.verifiedwritemem(bufaddr, blockdump)
        ioerr = floppy.write(bufaddr, size, 0)
        print(f"write ioerr: {ioerr}")
        ioerr = floppy.motoroff()
        print(f"motor off ioerr: {ioerr}")
        self.execlib.FreeMem(bufaddr, size)
        return
    def writefloppy(self, floppy, blockdump):
        tracksize = 512*11
        disksize = tracksize * 80 * 2
        if len(blockdump)!=disksize:
            raise ValueError()
        if self.execlib.version >= 36:
            bufaddr = self.execlib.AllocMem(tracksize, self.execlib.MEMF_PUBLIC)
        else:
            bufaddr = self.execlib.AllocMem(tracksize, self.execlib.MEMF_CHIP|self.execlib.MEMF_PUBLIC)
        for track in range(0, 160):
            trackstart = track*tracksize
            trackend = trackstart+tracksize
            self.snip.verifiedwritemem(bufaddr, blockdump[trackstart:trackend])
            print(f'Writing   Cyl:{track//2:02} Side:{track%2}', end='\r', flush=True)
            ioerr = floppy.tdformat(bufaddr, tracksize, trackstart)
        for track in range(0, 160):
            trackstart = track*tracksize
            trackend = trackstart+tracksize
            print(f'Verifying Cyl:{track//2:02} Side:{track%2}', end='\r', flush=True)
            ioerr = floppy.clear()
            ioerr = floppy.read(bufaddr, tracksize, trackstart)
            readcrc = self.snip.amigakeysum(bufaddr, tracksize)
            localcrc = self.snip.keysum(blockdump[trackstart:trackend])
            if readcrc != localcrc:
                print(f"ERROR.")
                raise BufferError()
        print("Done     ")
        floppy.motoroff()
        return
    def writebootblockraw(self, floppy, bootblock):
        print(f"buffer addr: {hex(bootblock)}")
        ioerr = floppy.write(bootblock, 1024, 0)
        print(f"write ioerr: {ioerr}")
        ioerr = floppy.update()
        print(f"update ioerr: {ioerr}")
        ioerr = floppy.motoroff()
        print(f"motor off ioerr: {ioerr}")
        return
    def writebootblock(self, floppy, bootblock):
        if len(bootblock) > 1024:
            raise NotImplementedError("Passed bootblock is above 1024 bytes. Not supported.")
        bootblock = bytearray(bootblock)
        if len(bootblock) < 1024:
            bootblock += bytes(1024 - len(bootblock))
        bufaddr = self.execlib.AllocMem(1024, self.execlib.MEMF_CHIP)
        ioerr = floppy.read(bufaddr, 1024, 0)
        if ioerr:
            raise BufferError("bootblock on target can't be read. Is this floppy formatted?")
        bbhdr = self.amiga.readmem(bufaddr, 12)
        if bbhdr[0:3] != b"DOS":
            raise NotImplementedError("Floppy's current bootblock lacks DOS signature. Guessing flags/root block is not supported.")
        bootblock[3] = bbhdr[3]
        bootblock[4:8] = bytes(4)
        bootblock[8:12] = bbhdr[8:12]
        bootblock[4:8] = struct.pack(">I", self.bootblocksum(bootblock))
        self.snip.verifiedwritemem(bufaddr, bootblock)
        if ioerr := floppy.write(bufaddr, 1024, 0):
            raise BufferError("Couldn't write. Is the floppy write-protected?")
        if ioerr := floppy.update():
            raise BufferError("Couldn't update after write. Is the floppy write-protected?")
        if ioerr := floppy.motoroff():
            raise Exception("Couldn't stop motor. Why?!")
        self.execlib.FreeMem(bufaddr, 1024)
        return
    def readrawtrack(self, floppy, track, flags):
        #A track is 11968 (1088*11) + a 696 gap.
        size = 0x3200 #size of "PAULA track", or how much paula usually reads, as per ADF FAQ)
        bufaddr = self.execlib.AllocMem(size, self.execlib.MEMF_CHIP|self.execlib.MEMF_PUBLIC|self.execlib.MEMF_CLEAR) #on rawops, buf needs be chip.
        #print(f"buffer addr: {hex(bufaddr)}")
        ioerr = floppy.rawread(bufaddr, size, track, flags)
        #print(f"rawread ioerr: {ioerr}")
        #ioerr = floppy.motoroff()
        #print(f"motor off ioerr: {ioerr}")
        trackdump = self.snip.verifiedreadmem(bufaddr, size)
        self.execlib.FreeMem(bufaddr, size)
        return trackdump
    def writerawtrack(self, floppy, trackdata, track, flags):
        size = len(trackdata)
        bufaddr = self.execlib.AllocMem(size, self.execlib.MEMF_CHIP|self.execlib.MEMF_PUBLIC|self.execlib.MEMF_CLEAR)
        self.snip.verifiedwritemem(bufaddr, trackdata)
        ioerr = floppy.rawwrite(bufaddr, size, track, flags)
        print(f"rawwrite ioerr: {ioerr}")
        self.execlib.FreeMem(bufaddr, size)
        return
    def decodeamigamfm(self, odd, even):
        mask = 0x55555555
        if len(odd) != len(even):
            raise ValueError()
        if len(odd)%4:
            raise ValueError()
        data = bytearray()
        for i in range(0, len(odd), 4):
            oddlong = struct.unpack(">I", odd[i:i+4])[0]
            evenlong = struct.unpack(">I", even[i:i+4])[0]
            datalong = (evenlong&mask)|((oddlong&mask)<<1);
            data += struct.pack(">I", datalong)
        return bytes(data)
    def splitamigatrack(self, trackdata):
        found = trackdata.split(b"\xAA\xAA\x44\x89\x44\x89")
        print(f"sectors found: {len(found)}")
        for sector in found:
            yield bytes(b"\xAA\xAA\xAA\xAA" + b"\x44\x89\x44\x89" + sector[:-2])
        return None
