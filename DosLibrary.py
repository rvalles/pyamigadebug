from Library import Library
class DosLibrary(Library):
    LVOOpen = -30
    LVOClose = -36
    LVORead = -42
    LVOWrite = -48
    LVODelay = -198
    LVOLock = -84
    LVOUnLock = -90
    LVOExamine = -102
    LVOInfo = -114
    LVODeviceProc = -174
    #v36+
    LVOInhibit = -726
    #insanity
    DOSTRUE = 0xFFFFFFFF #aka -1
    DOSFALSE = 0
    #lock accessModes
    SHARED_LOCK = -2
    ACCESS_READ = -2
    EXCLUSIVE_LOCK = -1
    ACCESS_WRITE = -1
    #file modes
    MODE_READWRITE = 1004 #old file, shared lock, creates
    MODE_OLDFILE = 1005 #old file, opens at start
    MODE_NEWFILE = 1006 #overwrites if exists
    #dos packet
    dp_Link = 0 #exec message
    dp_Port = 4 #reply msgport
    dp_Type = 8 #ACTION_whatever
    dp_Res1 = 12 #typically return value
    dp_Res2 = 16 #typically IoErr
    dp_Arg1 = 20
    dp_Arg2 = 24
    dp_Arg3 = 28
    dp_Arg4 = 32
    dp_Arg5 = 36
    dp_Arg6 = 40
    dp_Arg7 = 44
    #dos packet types
    ACTION_INHIBIT = 31
    ACTION_DISK_TYPE = 32
    ACTION_DISK_CHANGE = 33
    #FileInfoBlock, 260 bytes.
    fib_DiskKey = 0
    fib_DirEntryType = 4 #0 file 1+ dir.
    fib_FileName = 8
    fib_Protection = 116
    fib_EntryType = 120
    fib_Size = 124
    fib_NumBlocks = 128
    fib_Date = 132 #DateStamp
    fib_Comment = 144
    fib_Reserved = 224
    #InfoData, 36 bytes.
    id_NumSoftErrors = 0
    id_UnitNumber = 4
    id_DiskState = 8
    id_NumBlocks = 12
    id_NumBlocksUsed = 16
    id_BytesPerBlock = 20
    id_DiskType = 24
    id_VolumeNode = 28
    id_InUse = 32
    #disk states
    ID_WRITE_PROTECTED = 80
    ID_VALIDATING = 81
    ID_VALIDATED = 82 #write enabled, too
    def __init__(self, debugger, base): #FIXME: Add a sanity check: Are we a Process?.
        if not base:
            raise ValueException()
        self.base = base
        self.amiga = debugger
        fullversion = self.amiga.peek32(self.base + self.lib_Version)
        self.version = fullversion >> 16
        self.revision = fullversion & 0xFF
        return
    def libcall(self, **kwargs):
        kwargs["base"] = self.base
        return self.amiga.libcall(**kwargs)
    def Open(self, name, accessMode):
        fd = self.libcall(lvo=self.LVOOpen, d1=name, d2=accessMode, result="d0")
        return fd
    def Close(self, fd):
        success = self.libcall(lvo=self.LVOClose, d1=fd, result="d0")
        if self.version < 36:
            return None
        return success
    def Read(self, fd, buf, size):
        actualLength = self.libcall(lvo=self.LVORead, d1=fd, d2=buf, d3=size, result="d0")
        return actualLength
    def Write(self, fd, buf, size):
        returnedLength = self.libcall(lvo=self.LVOWrite, d1=fd, d2=buf, d3=size, result="d0")
        return returnedLength
    def Delay(self, ticks):
        #uint32 ticks, 50 ticks per second.
        self.libcall(lvo=self.LVODelay, d1=ticks)
        self.amiga.sync()
        return
    def Lock(self, name, accessMode):
        lock = self.libcall(lvo=self.LVOLock, d1=name, d2=accessMode, result="d0")
        return lock
    def UnLock(self, lock):
        self.libcall(lvo=self.LVOUnLock, d1=lock)
        self.amiga.sync()
        return
    def Examine(self, lock, FileInfoBlock):
        success = self.libcall(lvo=self.LVOExamine, d1=lock, d2=FileInfoBlock, result="d0")
        return success
    def Info(self, lock, InfoData):
        success = self.libcall(lvo=self.LVOInfo, d1=lock, d2=InfoData, result="d0")
        return success
    def DeviceProc(self, name):
        process = self.libcall(lvo=self.LVODeviceProc, d1=name, result="d0")
        return process
    def Inhibit(self, filesystem, flag):
        success = self.libcall(lvo=self.LVOInhibit, d1=filesystem, d2=flag, result="d0")
        return success
