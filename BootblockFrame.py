import os
import glob
import wx
import threading
import struct
from TrackdiskDevice import TrackdiskDevice
from FloppyUtils import FloppyUtils
class BootblockFrame(wx.Frame):
    tracksize = 512 * 11
    def __init__(self):
        self.endcallback = None
        self.ser = None
        self.amiga = None
        self.execlib = None
        self.snip = None
        self.wantclose = False
        self.busy = False
        self.installcolor = None
        self.drives = 4 #maximum we test for
        self.bbpath = "asm/"
        self.bbdesc = glob.glob(f"{self.bbpath}/*desc")
        self.bbdesc.sort()
        self.bbname = [os.path.splitext(os.path.split(bb)[1])[0] for bb in self.bbdesc]
        self.bbimg = [os.path.join(dir, os.path.splitext(file)[0]+".dd") for bb in self.bbdesc for dir, file in [os.path.split(bb)]]
        super().__init__(None, id=wx.ID_ANY, title=u"amigaXfer Bootblock Tool", pos=wx.DefaultPosition, size=wx.Size(550, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        bSizer4 = wx.BoxSizer(wx.VERTICAL)
        m_bootblockChoices = self.bbname
        self.m_bootblock = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_bootblockChoices, 0)
        self.m_bootblock.SetSelection(0)
        bSizer4.Add(self.m_bootblock, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, 5)
        self.m_description = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY | wx.TE_MULTILINE)
        bSizer4.Add(self.m_description, 1, wx.ALL | wx.EXPAND, 5)
        wSizer8 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)
        bSizer6 = wx.BoxSizer(wx.VERTICAL)
        self.m_format = wx.CheckBox(self, wx.ID_ANY, u"Format", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_format.SetForegroundColour(wx.Colour(255, 13, 0))
        self.m_format.SetToolTip(u"Formats track 0. Data will be lost.")
        bSizer6.Add(self.m_format, 0, 0, 5)
        self.m_status = wx.TextCtrl(self, wx.ID_ANY, "Init", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.m_status.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        bSizer6.Add(self.m_status, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        wSizer8.Add(bSizer6, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        wSizer8.Add((0, 0), 1, wx.EXPAND, 5)
        m_driveChoices = [u"DF0", u"DF1", u"DF2", u"DF3"]
        self.m_drive = wx.RadioBox(self, wx.ID_ANY, u"Drive", wx.DefaultPosition, wx.DefaultSize, m_driveChoices, 1, wx.RA_SPECIFY_ROWS)
        self.m_drive.SetSelection(0)
        wSizer8.Add(self.m_drive, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        wSizer8.Add((0, 0), 1, wx.EXPAND, 5)
        self.m_exit = wx.Button(self, wx.ID_ANY, u"Exit", wx.DefaultPosition, wx.DefaultSize, 0)
        wSizer8.Add(self.m_exit, 0, wx.ALIGN_BOTTOM | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        self.m_install = wx.Button(self, wx.ID_ANY, u"Install", wx.DefaultPosition, wx.DefaultSize, 0)
        wSizer8.Add(self.m_install, 0, wx.ALIGN_BOTTOM | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        bSizer4.Add(wSizer8, 0, wx.EXPAND | wx.TOP | wx.LEFT, 5)
        self.SetSizer(bSizer4)
        self.Enablement(False)
        self.Layout()
        self.Centre(wx.BOTH)
        self.Bind(wx.EVT_CLOSE, self.onCloseSetup)
        self.m_format.Bind(wx.EVT_CHECKBOX, self.onFormatCheckBox)
        self.m_bootblock.Bind(wx.EVT_CHOICE,self.onBootblockChoice)
        self.m_exit.Bind(wx.EVT_BUTTON, self.onExitPressed)
        self.m_install.Bind(wx.EVT_BUTTON, self.onInstallPressed)
        return
    def UpdateStatus(self, status):
        self.m_status.ChangeValue(status)
        return
    def Enablement(self, enable):
        self.m_install.Enable(enable)
        self.m_exit.Enable(enable)
        self.m_format.Enable(enable)
        self.m_bootblock.Enable(enable)
        self.m_drive.Enable(enable)
        if enable:
            for i in range(0, 4):
                self.m_drive.EnableItem(i, i < self.drives)
        return
    def onCloseSetup(self, event):
        if event.CanVeto():
            event.Veto()
        return
    def onClose(self, event):
        if event.CanVeto():
            event.Veto()
        if self.wantclose:
            return
        if self.busy:
            self.wantclose = True
            return
        self.UpdateStatus("UserClose")
        self.CleanUp()
        return
    def onExitPressed(self, event):
        self.wantclose = True
        wx.CallAfter(self.UpdateStatus, "CleanUp")
        wx.CallAfter(self.CleanUp)
        return
    def onFormatCheckBox(self, event):
        danger = self.m_format.GetValue()
        if danger:
            self.installcolor = self.m_install.GetForegroundColour()
            self.m_install.SetForegroundColour(wx.Colour(255, 0, 0))
        else:
            self.m_install.SetForegroundColour(self.installcolor)
        return
    def onBootblockChoice(self, event):
        self.UpdateDescription()
        return
    def UpdateDescription(self):
        choice = self.m_bootblock.GetSelection()
        with open(self.bbdesc[choice]) as fh:
            text = fh.read()
        self.m_description.ChangeValue(text)
        return
    def onInstallPressed(self, event):
        self.Enablement(False)
        self.busy = True
        self.UpdateStatus("Install")
        self.Layout()
        bbsel = self.m_bootblock.GetSelection()
        bootblock = self.bbimg[bbsel]
        drive = self.m_drive.GetSelection()
        doformat = self.m_format.GetValue()
        print(f'Writing bootblock {self.bbname[bbsel]} to drive DF{drive}. Format: {doformat}.')
        blockdump = bytes()
        try:
            with open(bootblock, "rb") as fh:
                blockdump = fh.read()
        except:
            print(f"Couldn't read bootblock file {bootblock}.")
        if blockdump:
            threading.Thread(target=self.InstallWorker, args=(drive, blockdump, doformat)).start()
        else:
            self.UpdateStatus("FileErr.")
            wx.CallAfter(self.InstallCleanup)
        return
    def InstallCleanup(self):
        self.busy = False
        if self.wantclose:
            self.UpdateStatus("UserClose")
            self.CleanUp()
        else:
            self.Enablement(True)
        return
    def InstallWorker(self, drive, blockdump, doformat):
        floppy = TrackdiskDevice(debugger=self.amiga, execlib=self.execlib, ioreqaddr=self.getioreq(drive))
        if len(blockdump) > 1024:
            print("Passed bootblock is above 1024 bytes. Not supported.")
            return
        bootblock = bytearray(blockdump)
        if len(bootblock) < 1024:
            bootblock += bytes(1024 - len(bootblock))
        wx.CallAfter(self.UpdateStatus, "Clear")
        ioerr = floppy.clear()
        if ioerr:
            print(f"CLEAR IO ERROR {ioerr:02X}h.")
            wx.CallAfter(self.UpdateStatus, f"CrErr: {ioerr:02X}h")
            floppy.motoroff()
            wx.CallAfter(self.InstallCleanup)
            return
        bufaddr = self.trackbuffer
        if not doformat:
            wx.CallAfter(self.UpdateStatus, "Read")
            ioerr = floppy.read(bufaddr, 1024, 0)
            if ioerr==floppy.TDERR_DiskChanged:
                print("Couldn't read floppy. Is the floppy in the drive?")
                wx.CallAfter(self.UpdateStatus, "NoFloppy?")
                floppy.motoroff()
                wx.CallAfter(self.InstallCleanup)
                return
            elif ioerr:
                print(f"Bootblock on target couldn't be read. IO Error {ioerr:02X}h. Is this floppy formatted?")
                wx.CallAfter(self.UpdateStatus, "NoFormat?")
                floppy.motoroff()
                wx.CallAfter(self.InstallCleanup)
                return
            wx.CallAfter(self.UpdateStatus, "Recv+CRC")
            bbhdr = self.snip.verifiedreadmem(bufaddr, 12)
            if bbhdr[0:3] != b"DOS":
                print("Floppy's current bootblock lacks DOS signature. Guessing flags/root block is not supported.")
                wx.CallAfter(self.UpdateStatus, "NDOS.")
                wx.CallAfter(self.InstallCleanup)
                return
            bootblock[3] = bbhdr[3]
            bootblock[4:8] = bytes(4)
            bootblock[8:12] = bbhdr[8:12]
            bootblock[4:8] = struct.pack(">I", self.bootblocksum(bootblock))
        wx.CallAfter(self.UpdateStatus, "Send+CRC")
        self.snip.verifiedwritemem(bufaddr, bootblock)
        if doformat:
            wx.CallAfter(self.UpdateStatus, "Format")
            ioerr = floppy.tdformat(bufaddr, self.tracksize, 0)
            if ioerr==floppy.TDERR_WriteProt:
                wx.CallAfter(self.UpdateStatus, "WriteProt?")
                print("Couldn't write to floppy. Is the floppy write-protected?")
                floppy.motoroff()
                wx.CallAfter(self.InstallCleanup)
                return
            elif ioerr==floppy.TDERR_DiskChanged:
                wx.CallAfter(self.UpdateStatus, "NoFloppy?")
                print("Couldn't write to floppy. Is the floppy in the drive?")
                floppy.motoroff()
                wx.CallAfter(self.InstallCleanup)
                return
            elif ioerr:
                print(f"Couldn't format track. IO Error {ioerr:02X}h. Is this a bad floppy?")
                wx.CallAfter(self.UpdateStatus, f"BadFloppy?")
                floppy.motoroff()
                wx.CallAfter(self.InstallCleanup)
                return
        else:
            wx.CallAfter(self.UpdateStatus, "Write")
            ioerr = floppy.write(bufaddr, 1024, 0)
            if ioerr:
                print(f"Write ioerr {ioerr}.")
            else:
                ioerr = floppy.update()
                if ioerr:
                    print(f"Update ioerr {ioerr}.")
            if ioerr==floppy.TDERR_WriteProt:
                wx.CallAfter(self.UpdateStatus, "WriteProt?")
                print("Couldn't write to floppy. Is the floppy write-protected?")
                floppy.motoroff()
                wx.CallAfter(self.InstallCleanup)
                return
            elif ioerr==floppy.TDERR_DiskChanged:
                wx.CallAfter(self.UpdateStatus, "NoFloppy?")
                print("TDERR_DiskChanged.")
                floppy.motoroff()
                wx.CallAfter(self.InstallCleanup)
                return
            elif ioerr:
                print(f"WRITE IO ERROR {ioerr:02X}h.")
                wx.CallAfter(self.UpdateStatus, f"WrErr: {ioerr:02X}h")
                floppy.motoroff()
                wx.CallAfter(self.InstallCleanup)
                return
        wx.CallAfter(self.UpdateStatus, "Clear")
        ioerr = floppy.clear()
        wx.CallAfter(self.UpdateStatus, "Read")
        ioerr = floppy.read(bufaddr, 1024, 0)
        if ioerr==floppy.TDERR_DiskChanged:
            print("Couldn't read floppy. Is the floppy in the drive?")
            wx.CallAfter(self.UpdateStatus, "NoFloppy?")
            floppy.motoroff()
            wx.CallAfter(self.InstallCleanup)
            return
        elif ioerr:
            print(f"Verify read failed. IO Error {ioerr:02X}h. Is this a bad floppy?")
            wx.CallAfter(self.UpdateStatus, "BadFloppy?")
            floppy.motoroff()
            wx.CallAfter(self.InstallCleanup)
            return
        if ioerr := floppy.motoroff():
            print("Couldn't stop motor. Why?!")
        wx.CallAfter(self.UpdateStatus, "CRC")
        amigacrc = self.snip.amigakeysum(bufaddr, 1024)
        localcrc = self.snip.keysum(bootblock)
        if amigacrc != localcrc:
            print("Verify failed. CRC does not match.")
            wx.CallAfter(self.UpdateStatus, f"CRCErr.")
            wx.CallAfter(self.InstallCleanup)
            return
        wx.CallAfter(self.UpdateStatus, "Done.")
        wx.CallAfter(self.InstallCleanup)
        return
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
    def BootblockSetup(self, endcallback, ser, amiga, execlib, snip):
        self.Bind(wx.EVT_CLOSE, self.onCloseSetup)
        self.m_status.ChangeValue(u'Setup')
        self.endcallback = endcallback
        self.ser = ser
        self.amiga = amiga
        self.execlib = execlib
        self.snip = snip
        self.wantclose = False
        self.Enablement(False)
        threading.Thread(target=self.BootblockSetupWorker).start()
        return
    def BootblockSetupWorker(self):
        wx.CallAfter(self.UpdateStatus, "Buffer")
        self.trackbuffer = self._getbuffer(self.tracksize)
        self.drives = self._initdrives(self.drives)
        if self.drives == 0:
            print("Couldn't open DF0. Aborting.")
            wx.CallAfter(self.UpdateStatus, "NoDrives")
            wx.CallAfter(self.CleanUp)
            return
        wx.CallAfter(self.BootblockSetupDone)
        return
    def BootblockSetupDone(self):
        wx.CallAfter(self.UpdateDescription)
        wx.CallAfter(self.UpdateStatus, "Ready.")
        wx.CallAfter(self.Enablement, True)
        self.Unbind(wx.EVT_CLOSE, handler=self.onCloseSetup)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        return
    def _getbuffer(self, size):
        if self.execlib.version >= 36:
            bufaddr = self.execlib.AllocMem(size, self.execlib.MEMF_PUBLIC | self.execlib.MEMF_CLEAR)
        else:
            bufaddr = self.execlib.AllocMem(size, self.execlib.MEMF_CHIP | self.execlib.MEMF_PUBLIC | self.execlib.MEMF_CLEAR)
        print(f'Allocated {hex(size)} bytes buffer @ {hex(bufaddr)}')
        return bufaddr
    def getioreq(self, unit):
        (ioreq, msgport) = self._ioreq[unit]
        return ioreq
    def _getioreq(self, devname, unit):
        msgport = self.execlib.createmsgport()
        if not msgport:
            print('Failed to obtain msgport.')
            raise BufferError()
        ioaddr = self.execlib.createiorequest(msgport)
        if not ioaddr:
            print('Failed to obtain ioreq.')
            raise BufferError()
        devname = self.snip.getaddrstr("trackdisk.device")
        err = self.execlib.OpenDevice(devname, unit, ioaddr, 0)
        if err:
            self.execlib.deleteiorequest(ioaddr)
            self.execlib.deletemsgport(msgport)
            return (None, None)
        return (ioaddr, msgport)
    def _initdrives(self, maxdrives):
        devname = self.snip.getaddrstr("trackdisk.device")
        self._ioreq = []
        founddrives = 0
        for unit in range(0, maxdrives):
            wx.CallAfter(self.UpdateStatus, f'Init DF{unit}:')
            (ioreq, msgport) = self._getioreq(devname, unit)
            if ioreq:
                self._ioreq.append((ioreq, msgport))
                founddrives += 1
                print(f'DF{unit} @ {hex(ioreq)}.')
            else:
                print(f'DF{unit} Not Present.')
                break
        return founddrives
    def onExitPressed(self, event):
        self.wantclose = True
        wx.CallAfter(self.UpdateStatus, "CleanUp")
        wx.CallAfter(self.CleanUp)
        return
    def CleanUp(self):
        self.Enablement(False)
        threading.Thread(target=self.CleanUpWorker).start()
        return
    def CleanUpWorker(self):
        print("CleanUp start.")
        for (ioaddr, msgport) in self._ioreq:
            if not ioaddr:
                continue
            print(f"ioreq: {hex(ioaddr)}")
            self.execlib.CloseDevice(ioaddr)
            self.execlib.deleteiorequest(ioaddr)
            self.execlib.deletemsgport(msgport)
        self.execlib.FreeMem(self.trackbuffer, self.tracksize)
        print("CleanUp done.")
        wx.CallAfter(self.endcallback)
        return
