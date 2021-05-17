import struct
class FloppyXferIO(object):
    FX_NOP = 0x00
    FX_EXIT = 0xff
    FX_SETBUFFER = 0x01
    FX_SETLENGTH = 0x02
    FX_SETIOREQ = 0x03
    FX_SETTRACK = 0x04
    FX_SETUSR = 0x05
    FX_SENDBUFFER = 0x20
    FX_RECVBUFFER = 0x21
    FX_CALLUSR = 0x25
    FX_TRACKREAD = 0x30
    FX_TRACKFORMAT = 0x31
    FX_TRACKSEEK = 0x32
    FX_MOTOROFF = 0x40
    TDERR_NotSpecified = 20
    TDERR_NoSecHdr = 21
    TDERR_BadSecPreamble = 22
    TDERR_BadSecID = 23
    TDERR_BadHdrSum = 24
    TDERR_BadSecSum = 25
    TDERR_TooFewSecs = 26
    TDERR_BadSecHdr = 27
    TDERR_WriteProt = 28
    TDERR_DiskChanged = 29
    TDERR_SeekError = 30
    TDERR_NoMem = 31
    TDERR_BadUnitNum = 32
    TDERR_BadDriveType = 33
    TDERR_DriveInUse = 34
    TDERR_PostReset = 35
    def __init__(self, snip):
        self.snip = snip
        self.floppyxfer = self.snip.getaddrfile("asm/floppyxfer.o")
        if not self.floppyxfer:
            raise BufferError()
        self.serial = self.snip.serial
        ser = self.serial
        serper = self.snip.serper | (self.snip.amiga.serper << 16)
        self.snip.amiga.callargs(addr=self.floppyxfer, d0=serper)
        #ser.stopbits = 1
        ser.baudrate = self.snip.baudrate
        ser.write(b"\0")
        ser.flush()
        self.sync()
        return
    def sync(self):
        while self.serial.read(1) != b'?':
            print("SYNC?!")
            pass
        return
    def exit(self):
        self.serial.write(struct.pack(">B", self.FX_EXIT))
        self.serial.flush()
        self.serial.baudrate = self.snip.amiga.baudrate
        self.serial.write(b"F")
        self.serial.flush()
        self.snip.amiga.sync()
        return
    def nop(self):
        self.serial.write(struct.pack(">B", self.FX_NOP))
        self.serial.flush()
        self.sync()
        return
    def sendlong(self, value):
        ser = self.serial
        value = struct.pack(">I", value)
        while ser.read(1) != b'H':
            pass
        ser.write(struct.pack(">B", value[0]))
        ser.flush()
        while ser.read(1) != b'h':
            pass
        ser.write(struct.pack(">B", value[1]))
        ser.flush()
        while ser.read(1) != b'L':
            pass
        ser.write(struct.pack(">B", value[2]))
        ser.flush()
        while ser.read(1) != b'l':
            pass
        ser.write(struct.pack(">B", value[3]))
        ser.flush()
        return
    def setbuffer(self, bufaddr):
        self.serial.write(struct.pack(">B", self.FX_SETBUFFER))
        self.serial.flush()
        self.sendlong(bufaddr)
        self.sync()
        return
    def setlength(self, length):
        self.serial.write(struct.pack(">B", self.FX_SETLENGTH))
        self.serial.flush()
        self.sendlong(length)
        self.sync()
        self.length = length
        return
    def setioreq(self, ioreq):
        self.serial.write(struct.pack(">B", self.FX_SETIOREQ))
        self.serial.flush()
        self.sendlong(ioreq)
        self.sync()
        return
    def setusr(self, usr):
        self.serial.write(struct.pack(">B", self.FX_SETUSR))
        self.serial.flush()
        self.sendlong(usr)
        self.sync()
        return
    def settrack(self, track):
        self.serial.write(struct.pack(">B", self.FX_SETTRACK))
        self.serial.flush()
        self.sendlong(track)
        self.sync()
        return
    def callusr(self):
        self.serial.write(struct.pack(">B", self.FX_CALLUSR))
        self.serial.flush()
        result = struct.unpack(">I",self.serial.read(4))[0]
        self.sync()
        return result
    def sendbuffer(self, buf):
        self.serial.write(struct.pack(">B", self.FX_RECVBUFFER))
        self.serial.flush()
        while self.serial.read(1) != b'S':
            pass
        self.serial.write(buf)
        self.serial.flush()
        self.sync()
        return
    def recvbuffer(self):
        self.serial.write(struct.pack(">B", self.FX_SENDBUFFER))
        self.serial.flush()
        data = self.serial.read(self.length)
        self.sync()
        return data
    def trackread(self):
        self.serial.write(struct.pack(">B", self.FX_TRACKREAD))
        self.serial.flush()
        ioerr = struct.unpack(">B", self.serial.read(1))[0]
        self.sync()
        return ioerr
    def trackformat(self):
        self.serial.write(struct.pack(">B", self.FX_TRACKFORMAT))
        self.serial.flush()
        ioerr = struct.unpack(">B", self.serial.read(1))[0]
        self.sync()
        return ioerr
    def motoroff(self):
        self.serial.write(struct.pack(">B", self.FX_MOTOROFF))
        self.serial.flush()
        ioerr = struct.unpack(">B", self.serial.read(1))[0]
        self.sync()
        return ioerr
    def seek(self):
        self.serial.write(struct.pack(">B", self.FX_TRACKSEEK))
        self.serial.flush()
        ioerr = struct.unpack(">B", self.serial.read(1))[0]
        self.sync()
        return ioerr
