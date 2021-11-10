class SCSIDevice(object):
    #ioreq: 0x20
    #iostdreq: +0x10 = 0x30
    #http://lclevy.free.fr/adflib/adf_info.html#p6
    io_Message = 0x0
    io_Command = 0x1c
    io_Flags = 0x1e
    io_Error = 0x1f
    io_Actual = 0x20
    io_Length = 0x24
    io_Data = 0x28
    io_Offset = 0x2c
    io_HighOffset = 0x20 #same field as io_Actual.
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
    #Trackdisk commands supported by scsi.device as per ndk2.1 docs
    TD_SEEK = 10
    TD_FORMAT = 11
    TD_CHANGESTATE = 14
    TD_PROTSTATUS = 15
    #TD64/Trackdisk64
    TD_READ64 = 24
    TD_WRITE64 = 25
    TD_SEEK64 = 26
    TD_FORMAT64 = 27
    #NSD
    NSCMD_DEVICEQUERY = 0x4000
    NSCMD_TD_READ64 = 0xC000
    NSCMD_TD_WRITE64 = 0xC001
    NSCMD_TD_SEEK64 = 0xC002
    NSCMD_TD_FORMAT64 = 0xC003
    #NSDeviceQueryResult/nsdqr
    NSDQR_DevQueryFormat = 0
    NSDQR_SizeAvailable = 4
    NSDQR_DeviceType = 8
    NSDQR_DeviceSubType = 10
    NSDQR_SupportedCommands = 12 #pointer to 0-terminated array of commands.
    NSDQR_Size = 16
    #flags
    IOTDB_WORDSYNC = 1<<4
    IOTDB_INDEXSYNC = 1<<5
    #tderr
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
    #ioerr
    IOERR_OPENFAIL = 0xFF
    IOERR_ABORTED = 0xFE
    IOERR_NOCMD = 0xFD
    IOERR_BADLENGTH = 0xFC
    IOERR_BADADDRESS = 0xFB
    IOERR_UNITBUSY = 0xFA
    IOERR_SELFTEST = 0xF9
    #RigidDiskBlock structure
    rdb_ID = 0
    rdb_SummedLongs = 4
    rdb_ChkSum = 8
    rdb_HostID = 12
    rdb_BlockBytes = 16
    rdb_Flags = 20
    #block list heads
    rdb_BadBlockList = 24
    rdb_PartitionList = 28
    rdb_FileSysHeaderList = 32
    rdb_DriveInit = 36
    rdb_Reserved1 = 40 #ulong[6] = 24 bytes
    #physical drive characteristics
    rdb_Cylinders = 64
    rdb_Sectors = 68
    rdb_Heads = 72
    rdb_Interleave = 76
    rdb_Park = 80
    rdb_Reserved2 = 84 #ulong[3] = 12 bytes
    rdb_WritePreComp = 96
    rdb_ReducedWrite = 100
    rdb_StepRate = 104
    rdb_Reserved3 = 108 #ulong[5] = 20 bytes
    rdb_RDBBlocksLo = 128
    rdb_RDBBlocksHi = 132
    rdb_LoCylinder = 136
    rdb_HiCylinder = 140
    rdb_CylBlocks = 144
    rdb_AutoParkSeconds = 148
    rdb_HighRDSKBlock = 152
    rdb_Reserved4 = 156
    #drive identification
    rdb_DiskVendor = 160 #char[8]
    rdb_DiskProduct = 168 #char[16]
    rdb_DiskRevision = 184 #char[4]
    rdb_ControllerVendor = 188 #char[8]
    rdb_ControllerProduct = 196 #char[16]
    rdb_ControllerRevision = 212 #char[4]
    rdb_Reserved5 = 216 #ulong[10] = 40 bytes
    #PartitionBlock structure
    pb_ID = 0 #char[4]
    pb_SummedLongs = 4
    pb_ChkSum = 8
    pb_HostID = 12
    pb_Next = 16
    pb_Flags = 20
    pb_Reserved1 = 24 #ulong[2]
    pb_DevFlags = 32
    pb_DriveName = 36 #char[32]
    pb_Reserved2 = 68 #ulong[15]
    pb_Environment = 128 #ulong[17]
    pb_EReserved = 196 #ulong[15]
    #DosEnvVec
    DOSEnvVec_VecSize = 128
    DOSEnvVec_SizeBlock = 132 #in longs, 128 = 512byte
    #CHS pain
    DOSEnvVec_Surfaces = 140
    DOSEnvVec_SectorsPerBlock = 144 #1
    DOSEnvVec_BlocksPerTrack = 148
    DOSEnvVec_Interleave = 160
    DOSEnvVec_LowCyl = 164
    DOSEnvVec_HighCyl = 168
    DOSEnvVec_MaxTransfer = 180 #http://www.boomerangsworld.de/cms/blog/2021/2021-08-15.html
    DOSEnvVec_DosType = 192
    DOSEnvVec_BootBlocks = 204
    def __init__(self, **kwargs):
        if (not "execlib" in kwargs) or (not "debugger" in kwargs) or (not "ioreqaddr" in kwargs):
            raise ValueError()
        self.debug = False
        if "debug" in kwargs:
            self.debug = kwargs["debug"]
        self.amiga = kwargs["debugger"]
        self.execlib = kwargs["execlib"]
        self.ioreqaddr = kwargs["ioreqaddr"]
        self.can64 = None
        return
    def cmd_read(self, addr, length, offset):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, offset)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.CMD_READ)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def cmd_write(self, addr, length, offset):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, offset)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.CMD_WRITE)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def td_format(self, addr, length, offset):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, offset)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.TD_FORMAT)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def td_read64(self, addr, length, offset):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, offset&0xFFFFFFFF)
        self.amiga.poke32(self.ioreqaddr + self.io_HighOffset, offset>>32)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.TD_READ64)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def td_write64(self, addr, length, offset):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, offset&0xFFFFFFFF)
        self.amiga.poke32(self.ioreqaddr + self.io_HighOffset, offset>>32)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.TD_WRITE64)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def nsd_td_read64(self, addr, length, offset):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, offset&0xFFFFFFFF)
        self.amiga.poke32(self.ioreqaddr + self.io_HighOffset, offset>>32)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.NSCMD_TD_READ64)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def nsd_td_write64(self, addr, length, offset):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, addr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, length)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, offset&0xFFFFFFFF)
        self.amiga.poke32(self.ioreqaddr + self.io_HighOffset, offset>>32)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.NSCMD_TD_WRITE64)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def cmd_update(self):
        self.amiga.poke8(self.ioreqaddr + self.io_Flags, 0)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.CMD_UPDATE)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def cmd_clear(self):
        self.amiga.poke8(self.ioreqaddr + self.io_Flags, 0)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.CMD_CLEAR)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        return ioerr
    def has_td64(self):
        self.amiga.poke32(self.ioreqaddr + self.io_Length, 0)
        self.amiga.poke32(self.ioreqaddr + self.io_Offset, 0)
        self.amiga.poke32(self.ioreqaddr + self.io_HighOffset, 0)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.TD_READ64)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        if self.debug:
            print(f"td64 test ioerr: {ioerr} {hex(ioerr)}")
        return (ioerr != self.IOERR_NOCMD) and (ioerr != self.IOERR_OPENFAIL)
    def has_nsd(self):
        self.amiga.poke32(self.ioreqaddr + self.io_Data, 0)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, 0)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.NSCMD_DEVICEQUERY)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        if self.debug:
            print(f"nsd test ioerr: {ioerr} {hex(ioerr)}")
        if not ((ioerr != self.IOERR_NOCMD) and (ioerr != self.IOERR_OPENFAIL)):
            print("No NSD.")
            return False
        nsdqr = self.execlib.AllocMem(self.NSDQR_Size, 0)
        self.amiga.poke32(self.ioreqaddr + self.io_Data, nsdqr)
        self.amiga.poke32(self.ioreqaddr + self.io_Length, self.NSDQR_Size)
        self.amiga.poke16(self.ioreqaddr + self.io_Command, self.NSCMD_DEVICEQUERY)
        ioerr = self.execlib.DoIO(self.ioreqaddr)
        if self.debug:
            print(f"nsd 2nd test ioerr: {ioerr} {hex(ioerr)}")
        actual = self.amiga.peek32(self.ioreqaddr+self.io_Actual)
        if not ((actual >= 16) and (actual <= self.NSDQR_Size)):
            print(f"NSD test failed. Weird actual: {hex(actual)}.")
            self.execlib.FreeMem(nsdqr, self.NSDQR_Size)
            return False
        devqueryformat = self.amiga.peek32(nsdqr+self.NSDQR_DevQueryFormat)
        size = self.amiga.peek32(nsdqr+self.NSDQR_SizeAvailable)
        devicetype = self.amiga.peek16(nsdqr+self.NSDQR_DeviceType)
        devicesubtype = self.amiga.peek16(nsdqr+self.NSDQR_DeviceSubType)
        supportedcommandsaddr = self.amiga.peek32(nsdqr+self.NSDQR_SupportedCommands)
        if self.debug:
            print(f"nsd devqueryformat: {hex(devqueryformat)}, size: {hex(size)}, devicetype: {hex(devicetype)}, devicesubtype: {hex(devicesubtype)}, *supportedcommands: {hex(supportedcommandsaddr)}.")
        supportedcommands = []
        while command := self.amiga.peek16(supportedcommandsaddr):
            supportedcommands.append(command)
            supportedcommandsaddr += 2
        if self.debug:
            print(f"nsd supportedcommands: {[hex(cmd) for cmd in supportedcommands]}")
        self.execlib.FreeMem(nsdqr, self.NSDQR_Size)
        return self.NSCMD_TD_READ64 in supportedcommands
    def has_64bit(self):
        if self.can64 != None:
            return self.can64
        if self.has_td64():
            self.can64 = "td64"
            return "td64"
        if self.has_nsd():
            self.can64 = "nsd"
            return "nsd"
        self.can64 = False
        return False
    def read(self, addr, length, offset):
        if (offset+length) >= 1<<32:
            if self.has_64bit() == "td64":
                ioerr = self.td_read64(addr, length, offset)
            elif self.has_64bit() == "nsd":
                ioerr = self.nsd_td_read64(addr, length, offset)
            else:
                raise ValueError()
        else:
            ioerr = self.cmd_read(addr, length, offset)
        return ioerr
    def write(self, addr, length, offset):
        if (offset+length) >= 1<<32:
            if self.has_64bit() == "td64":
                ioerr = self.td_write64(addr, length, offset)
            elif self.has_64bit() == "nsd":
                ioerr = self.nsd_td_write64(addr, length, offset)
            else:
                raise ValueError()
        else:
            ioerr = self.cmd_read(addr, length, offset)
        return ioerr
    def read_steps(self, addr, length, start, step):
        if ((start+length) >= 1<<32) and not self.has_64bit():
            raise ValueError()
        data = bytearray()
        for offset in range(start, start+length, step):
            if self.debug:
                print(f'Reading @ {hex(offset)}, {hex((offset-start)//1024)}/{hex(length//1024)} KBytes', end='\r', flush=True)
            size = min((start+length)-offset, step)
            ioerr = self.read(addr, size, offset)
            if ioerr:
                raise BufferError()
            data += self.amiga.readmem(addr, size)
        if self.debug:
            print('Read done')
        return data
    def write_steps(self, addr, data, start, step):
        if ((start+len(data)) >= 1<<32) and not self.has_64bit():
            raise ValueError()
        for offset in range(0, len(data), step):
            if self.debug:
                print(f'Writing @ {hex(start+offset)}, {hex((offset)//1024)}/{hex(len(data)//1024)} KBytes', end='\r', flush=True)
            size = min(len(data)-offset, step)
            self.amiga.writemem(addr, data[offset:offset+size])
            ioerr = self.write(addr, size, start+offset)
            if ioerr:
                raise BufferError()
        if self.debug:
            print('Read done')
        return
    def printrdb(self):
        iobuf = self.execlib.AllocMem(0x200, 0)
        ioerr = self.read(iobuf, 0x200, 0)
        print(f"IOErr: {ioerr}")
        if ioerr:
            exit(-1)
        rdbid = diskvendor = self.amiga.readmem(iobuf+self.rdb_ID, 4)
        if rdbid != b'RDSK':
            print(f"Not an RDB disk. Magic: {rdbid}")
            exit(-1)
        #controllervendor = self.amiga.readmem(iobuf+self.rdb_ControllerVendor, 8)
        #controllerproduct = self.amiga.readmem(iobuf+self.rdb_ControllerProduct, 16)
        #controllerrevision = self.amiga.readmem(iobuf+self.rdb_ControllerRevision, 4)
        #print(f"vendor: {controllervendor}, product: {controllerproduct}, revision: {controllerrevision}")
        diskvendor = self.amiga.readmem(iobuf+self.rdb_DiskVendor, 8)
        diskproduct = self.amiga.readmem(iobuf+self.rdb_DiskProduct, 16)
        diskrevision = self.amiga.readmem(iobuf+self.rdb_DiskRevision, 4)
        print(f"vendor: {diskvendor}, product: {diskproduct}, revision: {diskrevision}")
        diskcyl = self.amiga.peek32(iobuf+self.rdb_Cylinders)
        cylblocks = self.amiga.peek32(iobuf+self.rdb_CylBlocks)
        blocksize = self.amiga.peek32(iobuf+self.rdb_BlockBytes)
        cylbytes = cylblocks * blocksize
        print(f"blocksize {blocksize}, cyl: {diskcyl}, blockspercyl: {cylblocks}, bytespercyl: {cylbytes}")
        nextpart = self.amiga.peek32(iobuf+self.rdb_PartitionList)
        self.execlib.FreeMem(iobuf, 0x200)
        iobuf = self.execlib.AllocMem(blocksize, 0)
        while nextpart and nextpart != 0xFFFFFFFF:
            ioerr = self.read(iobuf, blocksize, nextpart*blocksize)
            if ioerr:
                print(f"IOErr: {ioerr}")
                exit(-1)
            partid = self.amiga.readmem(iobuf+self.pb_ID, 4)
            if partid != b'PART':
                print(f"bad partblock magic: {partid}")
                exit(-1)
            partnamelen = self.amiga.peek8(iobuf+self.pb_DriveName)
            partname = self.amiga.readmem(iobuf+self.pb_DriveName+1, partnamelen)
            dostype =  self.amiga.readmem(iobuf+self.DOSEnvVec_DosType, 4)
            lowcyl = self.amiga.peek32(iobuf+self.DOSEnvVec_LowCyl)
            highcyl = self.amiga.peek32(iobuf+self.DOSEnvVec_HighCyl)
            bootblocks = self.amiga.peek32(iobuf+self.DOSEnvVec_BootBlocks)
            maxtransfer = self.amiga.peek32(iobuf+self.DOSEnvVec_MaxTransfer)
            #surfaces = self.amiga.peek32(iobuf+self.DOSEnvVec_Surfaces)
            #blockspertrack = self.amiga.peek32(iobuf+self.DOSEnvVec_BlocksPerTrack)
            #blockspercyl = blockspertrack*surfaces
            #print(f"CHS surfaces: {surfaces} blockspertrack: {blockspertrack} blockspercyl: {blockspercyl}")
            partoffset = lowcyl * cylbytes
            partsize = (highcyl-lowcyl+1)*cylbytes
            print(f"partblock block: {nextpart}, dostype: {dostype}, name: {partname}, Cyl {lowcyl}:{highcyl}, offset: {hex(partoffset)}, size: {hex(partsize)}, bootblocks: {bootblocks}, maxtransfer: {hex(maxtransfer)}.")
            nextpart = self.amiga.peek32(iobuf+self.pb_Next)
        self.execlib.FreeMem(iobuf, blocksize)
        return
    def readtofile(self, start, length, step, path):
        if ((start+length) >= 1<<32) and not self.has_64bit():
            raise ValueError()
        iobuf = self.execlib.AllocMem(step, 0)
        with open(path,"wb") as fh:
            for offset in range(start, start+length, step):
                print(f'Reading @ {hex(offset)}, {hex((offset-start)//1024)}/{hex(length//1024)} KBytes', end='\r', flush=True)
                size = min((start+length)-offset, step)
                ioerr = self.read(iobuf, size, offset)
                if ioerr:
                    raise BufferError()
                fh.write(self.amiga.readmem(iobuf, size))
        self.execlib.FreeMem(iobuf, step)
        print('')
        return
