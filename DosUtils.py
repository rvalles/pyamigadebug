import struct
class DosUtils(object):
    def __init__(self, **kwargs):
        self.amiga = kwargs["debugger"]
        self.execlib = kwargs["execlib"]
        self.doslib = kwargs["doslib"]
        self.snip = kwargs["snippets"]
        self.bufsize = 0x10000
    def readfile(self, filepath):
        bufaddr = self.execlib.AllocMem(self.bufsize, self.execlib.MEMF_PUBLIC)
        print(f"buffer addr: {hex(bufaddr)} size: {self.bufsize}")
        filepathaddr = self.snip.getaddrstr(filepath)
        fh = self.doslib.Open(filepathaddr, self.doslib.MODE_OLDFILE)
        if not fh:
            raise ValueError()
        data = bytearray()
        while True:
            actualLength = self.doslib.Read(fh, bufaddr, self.bufsize)
            if not actualLength:
                break
            data += self.snip.verifiedreadmem(bufaddr, actualLength)
            if actualLength < self.bufsize:
                break
        self.doslib.Close(fh)
        return bytes(data)
    def writefile(self, filepath, data):
        bufsize = min(self.bufsize, len(data))
        bufaddr = self.execlib.AllocMem(bufsize, self.execlib.MEMF_PUBLIC)
        print(f"buffer addr: {hex(bufaddr)} size: {hex(bufsize)}")
        filepathaddr = self.snip.getaddrstr(filepath)
        fh = self.doslib.Open(filepathaddr, self.doslib.MODE_NEWFILE)
        if not fh:
            raise ValueError()
        for offset in range(0, len(data), bufsize):
            remaining = len(data) - offset
            stepsize = min(remaining, bufsize)
            print(f"transferring offset {hex(offset)} remaining {hex(remaining)}")
            self.snip.verifiedwritemem(bufaddr, data[offset:offset + stepsize])
            returnedLength = self.doslib.Write(fh, bufaddr, stepsize)
            print(f"returnedLength: {hex(returnedLength)}")
        print("Closing file.")
        success = self.doslib.Close(fh)
        print(f"Success: {success}")
        self.execlib.FreeMem(bufaddr, bufsize)
        return
    def sendpacket(self, replyport, handlerport, action, arg1):
        msg = self.execlib.AllocMem(68, self.execlib.MEMF_PUBLIC | self.execlib.MEMF_CLEAR)
        pkt = msg+20
        self.amiga.poke32(msg+self.execlib.ln_Name, pkt)
        self.amiga.poke32(pkt+self.doslib.dp_Link, msg)
        self.amiga.poke32(pkt+self.doslib.dp_Port, replyport)
        self.amiga.poke32(pkt+self.doslib.dp_Type, action)
        self.amiga.poke32(pkt+self.doslib.dp_Arg1, arg1)
        print(f"PutMsg handler {hex(handlerport)} msg {hex(msg)}")
        self.execlib.PutMsg(handlerport, msg)
        self.execlib.WaitPort(replyport)
        self.execlib.GetMsg(replyport)
        res1 = self.amiga.peek32(pkt+self.doslib.dp_Res1)
        self.execlib.FreeMem(msg, 68)
        return res1
    def inhibit(self, filesystem, flag):
        filesystemaddr = self.snip.getaddrstr(filesystem)
        if self.execlib.version >= 36:
            success = self.doslib.Inhibit(filesystemaddr, flag)
        else:
            handlerport = self.doslib.DeviceProc(filesystemaddr)
            if not handlerport:
                print("DeviceProc failed.")
                return self.doslib.DOSFALSE
            msgport = self.execlib.createmsgport()
            if not msgport:
                print("createmsgport() failed.")
                return self.doslib.DOSFALSE
            print(f"msgport: {hex(msgport)}")
            success = self.sendpacket(msgport, handlerport, self.doslib.ACTION_INHIBIT, flag)
            self.execlib.deletemsgport(msgport)
        return success
