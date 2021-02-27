class TrackdiskDevice(object):
    #1760x 512 byte blocks
    #11x blocks per sector
    #0-10 s0, 11-22 s1, etc.
    #ioreq: 0x20
    #iostdreq: +0x10 = 0x30
    io_Message = 0x0
    io_Command = 0x1c
    io_Flags = 0x1e
    io_Error = 0x1f
    io_Actual = 0x20
    io_Length = 0x24
    io_Data = 0x28
    io_Offset = 0x2c
    CMD_INVALID = 0
    CMD_RESET = 1
    CMD_READ = 2
    CMD_WRITE = 3
    CMD_UPDATE = 4
    CMD_CLEAR = 5
    CMD_STOP = 6
    CMD_START = 7
    CMD_FLUSH = 8
    CMD_NONSTD = 9
    TD_MOTOR = 9
    TD_SEEK = 10
    TD_FORMAT = 11
    TD_REMOVE = 12
    TD_CHANGENUM = 13
    TD_CHANGESTATE = 14
    TD_PROTSTATUS = 15
    TD_RAWREAD = 16
    TD_RAWWRITE = 17
    TD_GETDRIVETYPE = 18
    TD_GETNUMTRACKS = 19
    TD_ADDCHANGEINT = 20
    TD_REMCHANGEINT = 21
    TD_GETGEOMETRY = 22
    TD_EJECT = 23
    TD_LASTCOMM = 24
    IOTDB_WORDSYNC = 1<<4
    IOTDB_INDEXSYNC = 1<<5
    def __init__(self, **kwargs):
        if (not "execlib" in kwargs) or (not "debugger" in kwargs) or (not "ioreqaddr" in kwargs):
            raise ValueError()
        self.debug = False
        if "debug" in kwargs:
            self.debug = kwargs["debug"]
        self.amiga = kwargs["debugger"]
        self.execlib = kwargs["execlib"]
        self.ioreqaddr = kwargs["ioreqaddr"]
        return
    def read(self, addr, length, offset):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, offset)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.CMD_READ)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def write(self, addr, length, offset):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, offset)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.CMD_WRITE)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def tdformat(self, addr, length, offset):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, offset)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.TD_FORMAT)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def update(self):
        self.amiga.poke8(self.ioreqaddr + self.io_Flags, 0)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.CMD_UPDATE)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def clear(self):
        self.amiga.poke8(self.ioreqaddr + self.io_Flags, 0)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.CMD_CLEAR)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def motoroff(self):
        self.amiga.poke32(self.ioreqaddr + self.io_Length, 0)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.TD_MOTOR)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def rawread(self, addr, length, track, flags):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, track)
        self.amiga.poke8(self.ioreqaddr + self.io_Flags, flags)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.TD_RAWREAD)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def rawwrite(self, addr, length, track, flags):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, track)
        self.amiga.poke8(self.ioreqaddr + self.io_Flags, flags)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.TD_RAWWRITE)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
