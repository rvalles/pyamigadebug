import struct
from Library import Library
class ExecLibrary(Library):
    LVOInitCode = -72
    LVOFindResident = -96
    LVOInitResident = -102
    LVODebug = -114
    LVODisable = -120
    LVOEnable = -126
    LVOForbid = -132
    LVOPermit = -138
    LVOAllocMem = -198
    LVOAllocAbs = -204
    LVOFreeMem = -210
    LVOAvailMem = -216
    LVOAllocSignal = -330
    LVOFreeSignal = -336
    LVOAddPort = -354
    LVORemPort = -360
    LVOPutMsg = -366
    LVOGetMsg = -372
    LVOReplyMsg = -378
    LVOWaitPort = -384
    LVOFindPort = -390
    LVOOldOpenLibrary = -408
    LVOCloseLibrary = -414
    LVOOpenDevice = -444
    LVOCloseDevice = -450
    LVODoIO = -456
    LVOOpenLibrary = -552
    #v36+
    LVOCacheClearU = -636
    LVOCreateIORequest = -654
    LVODeleteIORequest = -660
    LVOCreateMsgPort = -666
    LVODeleteMsgPort = -672
    #static vars
    SoftVer = 34
    LowMemChkSum = 36
    ChkBase = 38
    ColdCapture = 42
    CoolCapture = 46
    WarmCapture = 50
    SysStkUpper = 54
    SysStkLower = 58
    MaxLocMem = 62
    DebugEntry = 66
    DebugData = 70
    AlertData = 74
    MaxExtMem = 78
    ChkSum = 82
    #interrupts
    IntVects = 84 #IntVector IntVects[16];
    #dynamic vars
    CurTask = 276
    IdleCount = 280
    DispCount = 284
    Quantum = 288
    Elapsed = 290
    SysFlags = 292
    IDNestCnt = 294
    TDNestCnt = 295
    AttnFlags = 296
    AttnResched = 298
    ResModules = 300
    TaskTrapCode = 304
    TaskExceptCode = 308
    TaskExitCode = 312
    TaskSigAlloc = 316
    TaskTrapAlloc = 320
    #system lists
    MemList = 322
    ResourceList = 336
    DeviceList = 350
    IntrList = 364
    LibList = 378
    PortList = 392
    TaskReady = 406
    TaskWait = 420
    #globals
    VBlankFrequency = 530
    PowerSupplyFrequency = 531
    KickMemPtr = 546
    KickTagPtr = 550
    KickCheckSum =  554
    #globals v36+
    ex_Pad0 = 558
    ex_LaunchPoint = 560
    ex_RamLibPrivate = 564
    ex_EClockFrequency = 568
    #mem flags
    MEMF_PUBLIC = 1 << 0 #won't be unmapped.
    MEMF_CHIP = 1 << 1
    MEMF_FAST = 1 << 2
    MEMF_LOCAL = 1 << 8 #v36+ won't go away on reset.
    MEMF_24BITDMA = 1 << 9
    MEMF_KICK = 1 << 10
    MEMF_CLEAR = 1 << 16
    MEMF_LARGEST = 1 << 17
    MEMF_REVERSE = 1 << 18 #v36+ from top of pool.
    MEMF_TOTAL = 1 << 19
    MEMF_NO_EXPUNGE = 1 << 31
    #msgport
    mp_Node = 0
    mp_Flags = 14
    mp_SigBit = 15
    mp_SigTask = 16
    mp_MsgList = 20
    mp_sizeof = 34
    #message
    mn_ReplyPort = 14
    mn_Length = 18
    #signal
    PA_SIGNAL = 0
    PA_SOFTINT = 1
    PA_IGNORE = 2
    PF_ACTION = 3
    #RomTag
    RTC_MATCHWORD = 0x4AFC
    rt_MatchWord = 0
    rt_MatchTag = 2
    rt_EndSkip = 6
    rt_Flags = 10
    rt_Version = 11
    rt_Type = 12
    rt_Pri = 13
    rt_Name = 14
    rt_IdString = 18
    rt_Init = 22
    rt_sizeof = 26
    def __init__(self, debugger):
        self.amiga = debugger
        self.base = self.amiga.peek32(0x4)
        fullversion = self.amiga.peek32(self.base + self.lib_Version)
        self.version = fullversion >> 16
        self.revision = fullversion & 0xFF
    def libcall(self, **kwargs):
        kwargs["base"] = self.base
        return self.amiga.libcall(**kwargs)
    def AllocMem(self, size, flags):
        addr = self.libcall(lvo=self.LVOAllocMem, d0=size, d1=flags, result="d0")
        if not addr:
            print("PANIC: AllocMem failed.")
            raise BufferError()
        return addr
    def FreeMem(self, addr, size):
        self.libcall(lvo=self.LVOFreeMem, a1=addr, d0=size)
        self.amiga.sync()
        return
    def AvailMem(self, flags):
        result = self.libcall(lvo=self.LVOAvailMem, d1=flags, result="d0")
        return result
    def Disable(self):
        self.libcall(lvo=self.LVODisable)
        self.amiga.sync()
        return
    def Enable(self):
        self.libcall(lvo=self.LVOEnable)
        self.amiga.sync()
        return
    def Forbid(self):
        self.libcall(lvo=self.LVOForbid)
        self.amiga.sync()
        return
    def Permit(self):
        self.libcall(lvo=self.LVOPermit)
        self.amiga.sync()
        return
    def DoIO(self, ioreqaddr):
        ioerr = self.libcall(lvo=self.LVODoIO, a1=ioreqaddr, result="d0")
        return ioerr
    def OpenLibrary(self, name, version):
        libbase = self.libcall(lvo=self.LVOOpenLibrary, a1=name, d0=version, result="d0")
        return libbase
    def OldOpenLibrary(self, name):
        libbase = self.libcall(lvo=self.LVOOldOpenLibrary, a1=name, result="d0")
        return libbase
    def CloseLibrary(self, base):
        self.libcall(lvo=self.LVOCloseLibrary, a1=base)
        self.amiga.sync()
        return
    def CreateMsgPort(self):
        msgport = self.libcall(lvo=self.LVOCreateMsgPort, result="d0")
        return msgport
    def DeleteMsgPort(self, msgport):
        self.libcall(lvo=self.LVODeleteMsgPort, a0=msgport)
        self.amiga.sync()
        return
    def CreateIORequest(self, ioreplyport, size):
        ioreq = self.libcall(lvo=self.LVOCreateIORequest, a0=ioreplyport, d0=size, result="d0")
        return ioreq
    def DeleteIORequest(self, ioreq):
        self.libcall(lvo=self.LVODeleteIORequest, a0=ioreq)
        self.amiga.sync()
        return
    def OpenDevice(self, devname, unitnumber, ioreq, flags):
        err = self.libcall(lvo=self.LVOOpenDevice, a0=devname, d0=unitnumber, a1=ioreq, d1=flags, result="d0")
        return err
    def CloseDevice(self, ioreq):
        self.libcall(lvo=self.LVOCloseDevice, a1=ioreq)
        self.amiga.sync()
        return
    def AllocSignal(self, signalnum):
        signalnum = self.libcall(lvo=self.LVOAllocSignal, d0=signalnum, result="d0")
        return signalnum
    def FreeSignal(self, signalnum):
        self.libcall(lvo=self.LVOAllocSignal, d0=signalnum)
        self.amiga.sync()
        return
    def FindResident(self, name):
        resident = self.libcall(lvo=self.LVOFindResident, a1=name, result="d0")
        return resident
    def InitResident(self, resident, segList):
        res = self.libcall(lvo=self.LVOInitResident, a1=resident, d1=segList, result="d0")
        return res
    def PutMsg(self, port, message):
        self.libcall(lvo=self.LVOPutMsg, a0=port, a1=message)
        self.amiga.sync()
        return
    def GetMsg(self, port):
        message = self.libcall(lvo=self.LVOGetMsg, a0=port, result="d0")
        return message
    def WaitPort(self, port):
        message = self.libcall(lvo=self.LVOWaitPort, a0=port, result="d0")
        return message
    def availdump(self):
        print(f'Memory Total: {hex(self.AvailMem(0))} Chip: {hex(self.AvailMem(self.MEMF_CHIP))} Largest: {hex(self.AvailMem(self.MEMF_LARGEST))} LargestChip: {hex(self.AvailMem(self.MEMF_LARGEST|self.MEMF_CHIP))}')
        return
    def createmsgport(self):
        if self.version >= 36:
            msgport = self.CreateMsgPort()
        else:
            msgport = self.AllocMem(self.mp_sizeof, self.MEMF_CLEAR|self.MEMF_PUBLIC)
            msgportsig = self.AllocSignal(-1)
            if msgportsig == 0xFF:
                return None
            #fill node
            self.amiga.poke8(msgport+self.ln_Type, self.NT_MSGPORT)
            #ln_Pri is ok at 0, ln_Name is ok at NULL, so no need to fill any more.
            #fill msgport
            self.amiga.poke8(msgport+self.mp_SigBit, msgportsig)
            self.amiga.poke8(msgport+self.mp_Flags, self.PA_SIGNAL)
            self.amiga.poke32(msgport+self.mp_SigTask, self.amiga.peek32(self.base + 276))
            #message list node head
            self.amiga.poke8(msgport+self.mp_MsgList+self.lh_Type, self.NT_MESSAGE)
            self.amiga.poke32(msgport+self.mp_MsgList+self.lh_Head, msgport+self.mp_MsgList+self.lh_Tail)
            self.amiga.poke32(msgport+self.mp_MsgList+self.lh_TailPred, msgport+self.mp_MsgList+self.lh_Head)
        return msgport
    def createiorequest(self, msgport):
        if self.version >= 36:
            ioaddr = self.CreateIORequest(msgport, 0x30)
        else:
            ioaddr = self.AllocMem(0x30, self.MEMF_CLEAR|self.MEMF_PUBLIC)
            self.amiga.poke32(ioaddr+0x0, msgport) #io_Message
            self.amiga.poke8(ioaddr+self.ln_Type, self.NT_MESSAGE)
            self.amiga.poke16(ioaddr+self.mn_Length, 0x30) #mn_Length
            self.amiga.poke32(ioaddr+self.mn_ReplyPort, msgport) #io_Message
        return ioaddr
    def deletemsgport(self, msgport):
        if self.version >= 36:
            self.DeleteMsgPort(msgport)
        else:
            msgportsig = self.amiga.peek8(msgport+self.mp_SigBit)
            self.FreeSignal(msgportsig)
            self.FreeMem(msgport, self.mp_sizeof)
        return
    def deleteiorequest(self, ioaddr):
        if self.version >= 36:
            self.DeleteIORequest(ioaddr)
        else:
            self.FreeMem(ioaddr, 0x30)
    def execchksum(self, data):
        cksum = 0
        mask = (1<<16)-1
        for i in struct.unpack('>24H', data):
            cksum += i
            if cksum > mask:
                cksum &= mask
        cksum = (~cksum) & mask
        return cksum
    def sysvarschksum(self):
        #Workaround for kickstart <36 rebuilding exec if chip ram higher than 512K exists.
        if self.version < 36:
            if self.amiga.peek32(self.base+self.CoolCapture):
                if self.amiga.peek32(self.base+self.MaxLocMem) > 0x80000:
                    self.amiga.poke32(self.base+self.MaxLocMem, 0x80000)
        sysvars = self.amiga.readmem(self.base+self.SoftVer, 48)
        self.amiga.poke16(self.base+self.ChkSum, self.execchksum(sysvars))
        return
    def printtasklist(self):
        tasks = []
        curtask = self.amiga.peek32(self.base + self.CurTask)
        tasks.append((curtask, *self.nodeheaderwithname(self.amiga.readmem(curtask, 14)), 'Run'))
        lh = self.base + self.TaskReady
        for (taskaddr, nodeheader) in self.nodeheaders(lh):
            tasks.append((taskaddr, *self.nodeheaderwithname(nodeheader), 'Ready'))
        lh = self.base + self.TaskWait
        for (taskaddr, nodeheader) in self.nodeheaders(lh):
            tasks.append((taskaddr, *self.nodeheaderwithname(nodeheader), 'Wait'))
        for (taskaddr, lnsucc, lnpred, lntype, lnpri, lnnameptr, lnname, taskstate) in tasks:
            tasktype = "Pr" if lntype == 13 else "Ta"
            print(f'{taskaddr:0>8x} {lnpri:3d} {taskstate:5s} {tasktype} {lnname.decode("ascii")}')
    def printresidentlist(self):
        resmodules = self.amiga.peek32(self.base + self.ResModules)
        print(f"ResModules: {hex(resmodules)}")
        curmod = self.amiga.peek32(resmodules)
        while curmod:
            nameptr = self.amiga.peek32(curmod+self.rt_Name)
            name = self.amiga.readstr(nameptr)
            flags = self.amiga.peek8(curmod+self.rt_Flags)
            version = self.amiga.peek8(curmod+self.rt_Version)
            pri = self.amiga.speek8(curmod+self.rt_Pri)
            print(f"addr {hex(curmod)} name: {name} flags: {bin(flags)} version: {version} pri: {pri}")
            resmodules += 4
            curmod = self.amiga.peek32(resmodules)
        return
    def removeresidentstrapbyname(self):
        resmodules = self.amiga.peek32(self.base + self.ResModules)
        print(f"ResModules: {hex(resmodules)}")
        curmod = self.amiga.peek32(resmodules)
        while curmod:
            nameptr = self.amiga.peek32(curmod+self.rt_Name)
            name = self.amiga.readstr(nameptr)
            flags = self.amiga.peek8(curmod+self.rt_Flags)
            version = self.amiga.peek8(curmod+self.rt_Version)
            pri = self.amiga.speek8(curmod+self.rt_Pri)
            print(f"addr {hex(curmod)} name: {name} flags: {bin(flags)} version: {version} pri: {pri}")
            if name == b"strap":
                self.amiga.poke32(resmodules, 0)
                print("Disabled strap.")
            resmodules += 4
            curmod = self.amiga.peek32(resmodules)
        return
    def replaceresidentbyname(self, resname, resaddr):
        resname = resname.encode("ascii")
        resmodules = self.amiga.peek32(self.base + self.ResModules)
        print(f"ResModules: {hex(resmodules)}")
        curmod = self.amiga.peek32(resmodules)
        while curmod:
            nameptr = self.amiga.peek32(curmod+self.rt_Name)
            name = self.amiga.readstr(nameptr)
            flags = self.amiga.peek8(curmod+self.rt_Flags)
            version = self.amiga.peek8(curmod+self.rt_Version)
            pri = self.amiga.speek8(curmod+self.rt_Pri)
            print(f"addr {hex(curmod)} name: {name} flags: {bin(flags)} version: {version} pri: {pri}")
            if name == resname:
                self.amiga.poke32(resmodules, resaddr)
                print(f"Replaced resident {resname} with resident @ {hex(resaddr)}.")
                break
            resmodules += 4
            curmod = self.amiga.peek32(resmodules)
        return
    def removeresidentstrap(self):
        resmodules = self.amiga.peek32(self.base + self.ResModules)
        print(f"ResModules: {hex(resmodules)}")
        curmod = self.amiga.peek32(resmodules)
        if not curmod:
            print("Resident table is empty. This shouldn't be the case at CoolCapture or later.")
            raise BufferError()
        print("Removing last resident (lowest priority) in the table.")
        while curmod:
            resmodules += 4
            curmod = self.amiga.peek32(resmodules)
        curmod = self.amiga.poke32(resmodules-4, 0)
        return
    def is_process(self):
        curtask = self.amiga.peek32(self.base + self.CurTask)
        tasktype = self.amiga.peek8(curtask + self.ln_Type)
        return tasktype == self.NT_PROCESS
    def is_pal(self):
        if self.version < 36:
            vblankfreq = self.amiga.peek8(self.base+self.VBlankFrequency)
            print(f"VBlankFreq: {vblankfreq}")
            pal = vblankfreq == 50
        else:
            eclockfreq = self.amiga.peek32(self.base+self.ex_EClockFrequency) 
            print(f"EClockFreq: {eclockfreq}")
            pal = eclockfreq < 712644
        return pal
    def enterdebugloop(self):
        if self.amiga.debugger != "SAD":
            print("debugloop: Debugger isn't SAD.")
            return
        with open("asm/debugloop.o", "rb") as fh:
            loopcode = fh.read()
        debugloopsize = len(loopcode)
        debugloopaddr = self.AllocMem(debugloopsize, self.MEMF_LOCAL)
        self.amiga.writemem(debugloopaddr, loopcode)
        print(f"debugloop enter addr: {hex(debugloopaddr)}")
        oldpc = self.amiga.getreg("pc")
        oldsp = self.amiga.getreg("sp")
        self.amiga.poke32(debugloopaddr+debugloopsize-8, oldpc)
        self.amiga.poke32(debugloopaddr+debugloopsize-12, oldsp)
        print(f"Saved sp: {hex(oldsp)}, pc: {hex(oldpc)}.")
        self.amiga.setreg("pc", debugloopaddr)
        self.amiga.resume()
        self.amiga.sync()
        return
    def exitdebugloop(self):
        if self.amiga.debugger != "SAD":
            print("debugloop: Debugger isn't SAD.")
            return
        with open("asm/debugloop.o", "rb") as fh:
            debugloopsize = len(fh.read())
        debugloopaddr = self.amiga.getreg("pc")-8
        print(f"debugloop leave addr: {hex(debugloopaddr)}")
        sig = self.amiga.peek32(debugloopaddr+debugloopsize-4)
        if sig != 0xDEB10070:
            print(f"debugloop bad signature: {hex(sig)}. Restore failed.")
            return
        oldpc = self.amiga.peek32(debugloopaddr+debugloopsize-8)
        oldsp = self.amiga.peek32(debugloopaddr+debugloopsize-12)
        print(f"Restored sp: {hex(oldsp)}, pc: {hex(oldpc)}.")
        self.FreeMem(debugloopaddr, debugloopsize)
        self.amiga.setreg("pc", oldpc)
        self.amiga.setreg("sp", oldsp)
        return
