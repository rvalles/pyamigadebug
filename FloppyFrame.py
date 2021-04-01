import wx
import os
import time
import threading
from DosLibrary import DosLibrary
from DosUtils import DosUtils
from FloppyXferIO import FloppyXferIO
class FloppyFrame(wx.Frame):
    tracksize = 512 * 11
    IOERR_WRITEPROT = 0x1C
    IOERR_NOFLOPPY = 0x1D
    def __init__(self):
        self.endcallback = None
        self.ser = None
        self.amiga = None
        self.execlib = None
        self.snip = None
        self.abort = threading.Event()
        self.wantclose = False
        self.busy = False
        self.drives = 4 #maximum we test for
        self.timerperiod = 50
        super().__init__(None, id=wx.ID_ANY, title=u"amigaXfer floppy tool", pos=wx.DefaultPosition, size=wx.Size(450, 340), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        m_modeChoices = [u"ADF2Disk", u"Disk2ADF", u"Compare"]
        self.m_mode = wx.RadioBox(self, wx.ID_ANY, u"Mode", wx.DefaultPosition, wx.DefaultSize, m_modeChoices, 1, wx.RA_SPECIFY_ROWS)
        self.m_mode.SetSelection(0)
        self.m_mode.Bind(wx.EVT_RADIOBOX, self.onModeChange)
        bSizer1.Add(self.m_mode, 0, wx.ALL | wx.EXPAND, 5)
        wSizer7 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)
        m_driveChoices = [u"DF0:", u"DF1:", u"DF2:", u"DF3:"]
        self.m_drive = wx.RadioBox(self, wx.ID_ANY, u"Drive", wx.DefaultPosition, wx.DefaultSize, m_driveChoices, 1, wx.RA_SPECIFY_COLS)
        self.m_drive.SetSelection(0)
        wSizer7.Add(self.m_drive, 0, wx.ALL, 5)
        bSizer5 = wx.BoxSizer(wx.VERTICAL)
        m_verifyChoices = [u"None", u"Xfer", u"Read"]
        self.m_verify = wx.RadioBox(self, wx.ID_ANY, u"Verify", wx.DefaultPosition, wx.DefaultSize, m_verifyChoices, 1, wx.RA_SPECIFY_ROWS)
        self.m_verify.SetSelection(2)
        bSizer5.Add(self.m_verify, 0, wx.ALL, 5)
        wSizer10 = wx.WrapSizer(wx.HORIZONTAL, wx.EXTEND_LAST_ON_EACH_LINE | wx.WRAPSIZER_DEFAULT_FLAGS)
        self.m_adfsourcemsg = wx.StaticText(self, wx.ID_ANY, u"ADF Source", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_adfsourcemsg.Wrap(-1)
        wSizer10.Add(self.m_adfsourcemsg, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_adfsource = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select an ADF image", u"Amiga Disk File (.adf)|*.adf;*.ADF", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE)
        self.m_adfsource.SetMinSize(wx.Size(300, -1))
        wSizer10.Add(self.m_adfsource, 0, wx.ALL, 5)
        bSizer5.Add(wSizer10, 1, wx.ALL | wx.ALIGN_RIGHT, 5)
        wSizer102 = wx.WrapSizer(wx.HORIZONTAL, wx.EXTEND_LAST_ON_EACH_LINE | wx.WRAPSIZER_DEFAULT_FLAGS)
        self.m_adftargetmsg = wx.StaticText(self, wx.ID_ANY, u"ADF Target", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_adftargetmsg.Wrap(-1)
        self.m_adftargetmsg.Hide()
        wSizer102.Add(self.m_adftargetmsg, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        defaulttarget = wx.EmptyString
        self.m_adftarget = wx.FilePickerCtrl(self, wx.ID_ANY, defaulttarget, u"Select target ADF filename", u"Amiga Disk File (.adf)|*.adf;*.ADF", wx.DefaultPosition, wx.DefaultSize, wx.FLP_OVERWRITE_PROMPT | wx.FLP_SAVE | wx.FLP_SMALL | wx.FLP_USE_TEXTCTRL)
        self.m_adftarget.SetMinSize(wx.Size(300, -1))
        self.m_adftarget.Hide()
        wSizer102.Add(self.m_adftarget, 0, wx.ALL, 5)
        bSizer5.Add(wSizer102, 1, wx.ALL | wx.ALIGN_RIGHT, 5)
        wSizer7.Add(bSizer5, 0, wx.ALL, 5)
        bSizer1.Add(wSizer7, 0, wx.ALL | wx.EXPAND, 5)
        self.m_progress = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        self.m_progress.SetValue(0)
        bSizer1.Add(self.m_progress, 0, wx.ALL | wx.EXPAND, 5)
        wSizer16 = wx.WrapSizer(wx.HORIZONTAL, 0)
        self.m_crcmsg = wx.StaticText(self, wx.ID_ANY, u"Last CRC", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_crcmsg.Wrap(-1)
        wSizer16.Add(self.m_crcmsg, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_crc = wx.TextCtrl(self, wx.ID_ANY, u"00000000", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        maxlen = 8
        self.m_crc.SetMaxLength(maxlen)
        self.m_crc.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        self.m_crc.SetInitialSize(self.m_crc.GetSizeFromTextSize(self.m_crc.GetTextExtent("A" * maxlen)))
        wSizer16.Add(self.m_crc, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_exit = wx.Button(self, wx.ID_ANY, u"Exit", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_exit.Bind(wx.EVT_BUTTON, self.onExitPressed)
        wSizer16.Add(self.m_exit, 0, wx.ALL, 5)
        self.m_abort = wx.Button(self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_abort.Hide()
        self.m_abort.Bind(wx.EVT_BUTTON, self.onAbortPressed)
        wSizer16.Add(self.m_abort, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_start = wx.Button(self, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_start.Bind(wx.EVT_BUTTON, self.onStartPressed)
        wSizer16.Add(self.m_start, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        bSizer1.Add(wSizer16, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        wSizer101 = wx.WrapSizer(wx.HORIZONTAL, 0)
        maxlen = 10
        self.m_status = wx.TextCtrl(self, wx.ID_ANY, u"Init", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.m_status.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        self.m_status.SetMaxLength(maxlen)
        self.m_status.SetInitialSize(self.m_status.GetSizeFromTextSize(self.m_status.GetTextExtent("A" * maxlen)))
        wSizer101.Add(self.m_status, 0, wx.ALL, 5)
        self.m_cylmsg = wx.StaticText(self, wx.ID_ANY, u"Cylinder", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_cylmsg.Wrap(-1)
        wSizer101.Add(self.m_cylmsg, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        maxlen = 2
        self.m_cyl = wx.TextCtrl(self, wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.m_cyl.SetMaxLength(2)
        self.m_cyl.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        self.m_cyl.SetInitialSize(self.m_cyl.GetSizeFromTextSize(self.m_cyl.GetTextExtent("A" * maxlen)))
        wSizer101.Add(self.m_cyl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_sidemsg = wx.StaticText(self, wx.ID_ANY, u"Side", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_sidemsg.Wrap(-1)
        wSizer101.Add(self.m_sidemsg, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        maxlen = 1
        self.m_side = wx.TextCtrl(self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.m_side.SetMaxLength(maxlen)
        self.m_side.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        self.m_side.SetInitialSize(self.m_side.GetSizeFromTextSize(self.m_side.GetTextExtent("A" * maxlen)))
        wSizer101.Add(self.m_side, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.m_timermsg = wx.StaticText(self, wx.ID_ANY, u"Time", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_timermsg.Wrap(-1)
        wSizer101.Add(self.m_timermsg, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_timer = wx.TextCtrl(self, wx.ID_ANY, u"   0.0s", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.m_timer.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        maxlen = 7
        self.m_timer.SetMaxLength(maxlen)
        self.m_timer.SetInitialSize(self.m_timer.GetSizeFromTextSize(self.m_timer.GetTextExtent("A" * maxlen)))
        wSizer101.Add(self.m_timer, 0, wx.ALL, 5)
        bSizer1.Add(wSizer101, 0, wx.EXPAND, 5)
        self.SetSizer(bSizer1)
        self.Enablement(False)
        self.Layout()
        self.Centre(wx.BOTH)
        self.Bind(wx.EVT_CLOSE, self.onCloseSetup)
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
            self.Abort()
            self.wantclose = True
            return
        self.UpdateStatus("UserClose")
        self.CleanUp()
    def onTimer(self, event):
        value = time.monotonic() - self.timerbase
        self.m_timer.ChangeValue(f"{value:6.1F}s")
        return
    def onModeChange(self, event):
        #FIXME: Duplicated "verify" logic with Enablement.
        mode = self.m_mode.GetSelection()
        if mode == 0:
            self.m_adftarget.Hide()
            self.m_adftargetmsg.Hide()
            self.m_adfsource.Show()
            self.m_adfsourcemsg.Show()
            self.m_verify.Show()
            self.m_verify.Enable(True)
            self.m_verify.EnableItem(2, True)
            self.m_verify.SetSelection(2)
        elif mode == 1:
            self.m_adfsource.Hide()
            self.m_adfsourcemsg.Hide()
            self.m_adftarget.Show()
            self.m_adftargetmsg.Show()
            self.m_verify.Show()
            self.m_verify.Enable(True)
            self.m_verify.EnableItem(2, False)
            self.m_verify.SetSelection(1)
            self.Layout() #FIXME: Workaround for terrible behaviour
        elif mode == 2:
            self.m_adftarget.Hide()
            self.m_adftargetmsg.Hide()
            self.m_adfsource.Show()
            self.m_adfsourcemsg.Show()
            self.m_verify.Hide()
        self.Layout()
        return
    def Enablement(self, enable):
        self.m_start.Enable(enable)
        self.m_exit.Enable(enable)
        self.m_abort.Enable(enable)
        self.m_mode.Enable(enable)
        self.m_adftarget.Enable(enable)
        self.m_adftargetmsg.Enable(enable)
        self.m_adfsource.Enable(enable)
        self.m_adfsourcemsg.Enable(enable)
        mode = self.m_mode.GetSelection()
        self.m_verify.Enable(enable)
        if enable and mode == 1:
            self.m_verify.EnableItem(2, False)
        self.m_drive.Enable(enable)
        if enable:
            for i in range(0, 4):
                self.m_drive.EnableItem(i, i < self.drives)
        return
    def UpdateStatus(self, status):
        self.m_status.ChangeValue(status)
        return
    def UpdateProgressValue(self, value):
        self.m_progress.SetValue(value)
        return
    def UpdateProgressRange(self, value):
        self.m_progress.SetRange(value)
        return
    def UpdateProgressPulse(self):
        self.m_progress.Pulse()
        return
    def UpdateProgressDone(self):
        maxval = self.m_progress.GetRange()
        self.m_progress.SetValue(maxval)
        return
    def UpdateTrack(self, cyl, side, status):
        self.m_status.ChangeValue(status)
        self.m_cyl.ChangeValue(f'{cyl:02}')
        self.m_side.ChangeValue(str(side))
        return
    def UpdateCrc(self, crc):
        self.m_crc.ChangeValue(f'{crc:08x}')
        return
    def XferSetup(self, endcallback, ser, amiga, execlib, snip):
        self.endcallback = endcallback
        self.ser = ser
        self.amiga = amiga
        self.execlib = execlib
        self.snip = snip
        self.wantclose = False
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        threading.Thread(target=self.XferSetupWorker).start()
        self.m_status.ChangeValue(u'Setup')
        return
    def XferSetupWorker(self):
        wx.CallAfter(self.UpdateProgressValue, 0)
        wx.CallAfter(self.UpdateStatus, "Buffer")
        self.trackbuffer = self._getbuffer(self.tracksize)
        self.drives = self._initdrives(self.drives)
        if self.drives == 0:
            print("Couldn't open DF0. Aborting.")
            wx.CallAfter(self.UpdateStatus, "NoDrives")
            wx.CallAfter(self.CleanUp)
            return
        wx.CallAfter(self.UpdateStatus, "DOSInhibit")
        if self.execlib.is_process():
            dosname = self.snip.getaddrstr("dos.library")
            self.dosbase = self.execlib.OldOpenLibrary(dosname)
        else:
            print("DOSInhibit skipped, as current task is not a process.")
            self.dosbase = None
        if self.dosbase:
            self.doslib = DosLibrary(debugger=self.amiga, base=self.dosbase)
            self.dosutil = DosUtils(debugger=self.amiga, execlib=self.execlib, doslib=self.doslib, snippets=self.snip)
            for drive in range(0, self.drives):
                if not self.dosutil.inhibit(f"DF{drive}:", self.doslib.DOSTRUE):
                    self.drives = drive
                    break
        wx.CallAfter(self.UpdateStatus, "Call")
        self.fxio = FloppyXferIO(self.snip) #from here, floppyxfer is running exclusively.
        wx.CallAfter(self.UpdateStatus, "Test")
        self.fxio.setbuffer(self.trackbuffer)
        testdata = b"123456789"
        self.fxio.setlength(len(testdata))
        self.fxio.setusr(self.snip.amigacrc)
        self.fxio.sendbuffer(testdata)
        amigacrc = self.fxio.callusr()
        wx.CallAfter(self.UpdateCrc, amigacrc)
        if amigacrc != self.snip.keysum(testdata):
            print("CRC Test Failed.")
            wx.CallAfter(self.UpdateStatus, "TestFail")
            wx.CallAfter(self.CleanUp)
            return
        print("CRC Test Successful.")
        self.fxio.setlength(self.tracksize)
        wx.CallAfter(self.XferSetupDone)
        return
    def XferSetupDone(self):
        wx.CallAfter(self.UpdateStatus, "Ready.")
        wx.CallAfter(self.Enablement, True)
        self.Unbind(wx.EVT_CLOSE, handler=self.onCloseSetup)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        return
    def _getbuffer(self, size):
        if self.execlib.version >= 36:
            bufaddr = self.execlib.AllocMem(size, self.execlib.MEMF_PUBLIC)
        else:
            bufaddr = self.execlib.AllocMem(size, self.execlib.MEMF_CHIP | self.execlib.MEMF_PUBLIC)
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
        if self.drives:
            self.fxio.exit()
        for (ioaddr, msgport) in self._ioreq:
            if not ioaddr:
                continue
            print(f"ioreq: {hex(ioaddr)}")
            self.execlib.CloseDevice(ioaddr)
            self.execlib.deleteiorequest(ioaddr)
            self.execlib.deletemsgport(msgport)
        if self.dosbase:
            for drive in range(0, self.drives):
                self.dosutil.inhibit(f"DF{drive}:", self.doslib.DOSFALSE)
            self.execlib.CloseLibrary(self.dosbase)
        self.execlib.FreeMem(self.trackbuffer, self.tracksize)
        print("CleanUp done.")
        wx.CallAfter(self.endcallback)
        return
    def onStartPressed(self, event):
        self.Enablement(False)
        self.abort.clear()
        self.busy = True
        self.m_abort.Enable(True)
        self.m_start.Hide()
        self.m_abort.Show()
        self.UpdateStatus("Start")
        self.Layout()
        mode = self.m_mode.GetSelection()
        verify = self.m_verify.GetSelection()
        drive = self.m_drive.GetSelection()
        self.timerbase = time.monotonic()
        self.timer.Start(self.timerperiod)
        if mode == 0: #Adf2Disk
            adf = self.m_adfsource.GetPath()
            wx.CallAfter(self.Adf2Disk, drive, adf, verify)
        elif mode == 1: #Disk2Adf
            adf = self.m_adftarget.GetPath()
            wx.CallAfter(self.Disk2Adf, drive, adf, verify)
        elif mode == 2: #Compare
            adf = self.m_adfsource.GetPath()
            wx.CallAfter(self.CompareDiskAdf, drive, adf)
        return
    def Stop(self):
        self.busy = False
        self.timer.Stop()
        self.m_abort.Hide()
        self.Enablement(True)
        self.m_start.Show()
        self.Layout()
        if self.wantclose:
            self.UpdateStatus("UserClose")
            self.CleanUp()
        return
    def onAbortPressed(self, event):
        self.Abort()
        return
    def Abort(self):
        self.m_abort.Enable(False)
        self.abort.set()
        return
    def Adf2Disk(self, drive, adf, verify):
        try:
            with open(adf, "rb") as fh:
                diskdump = fh.read()
        except:
            diskdump = b""
        if len(diskdump) != self.tracksize * 160:
            self.UpdateStatus("ADF Error.")
            self.Stop()
            return
        threading.Thread(target=self.Adf2DiskWorker, args=(drive, diskdump, verify)).start()
    #Verify 0:None/1:CRCxfer/2:CRCread/3:BothPointless.
    def Adf2DiskWorker(self, drive, diskdump, verify):
        wx.CallAfter(self.UpdateProgressRange, 159)
        self.fxio.setioreq(self.getioreq(drive))
        for track in range(0, 160):
            wx.CallAfter(self.UpdateProgressValue, track)
            cyl = track // 2
            side = track % 2
            print(f'Writing   Cyl:{cyl:02} Side:{side}', end='\r', flush=True)
            wx.CallAfter(self.UpdateTrack, cyl, side, "Xfer")
            startpos = track * self.tracksize
            endpos = startpos + self.tracksize
            trackdump = diskdump[startpos:endpos]
            self.fxio.settrack(track)
            self.fxio.sendbuffer(trackdump)
            if verify % 2:
                wx.CallAfter(self.UpdateStatus, "CRC")
                amigacrc = self.fxio.callusr()
                wx.CallAfter(self.UpdateCrc, amigacrc)
                if amigacrc != self.snip.keysum(trackdump):
                    wx.CallAfter(self.UpdateStatus, "XFerCRCErr.")
                    print("\nXFER CRC ERROR.")
                    self.fxio.motoroff()
                    wx.CallAfter(self.Stop)
            if self.abort.is_set():
                wx.CallAfter(self.UpdateStatus, "UserStop.")
                print("\nUser stopped.")
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                return
            wx.CallAfter(self.UpdateStatus, "Write")
            ioerr = self.fxio.trackformat()
            if ioerr == self.IOERR_WRITEPROT:
                wx.CallAfter(self.UpdateStatus, "WriteProt?")
                print("\nIOERR_WRITEPROT.")
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                return
            elif ioerr == self.IOERR_NOFLOPPY:
                wx.CallAfter(self.UpdateStatus, "NoFloppy?")
                print("\nIOERR_NOFLOPPY.")
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                return
            elif ioerr:
                wx.CallAfter(self.UpdateStatus, f"FmErr: {ioerr:02X}h")
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                print(f"\nFORMAT IO ERROR {ioerr:02X}h.")
                return
        if verify & 2:
            for track in range(0, 160):
                wx.CallAfter(self.UpdateProgressValue, 159-track)
                cyl = track // 2
                side = track % 2
                print(f'Verifying Cyl:{cyl:02} Side:{side}', end='\r', flush=True)
                wx.CallAfter(self.UpdateTrack, cyl, side, "Read")
                startpos = track * self.tracksize
                endpos = startpos + self.tracksize
                trackdump = diskdump[startpos:endpos]
                if self.abort.is_set():
                    wx.CallAfter(self.UpdateStatus, "UserStop.")
                    print("\nUser stopped.")
                    self.fxio.motoroff()
                    wx.CallAfter(self.Stop)
                    return
                self.fxio.settrack(track)
                ioerr = self.fxio.trackread()
                if ioerr:
                    wx.CallAfter(self.UpdateStatus, f"RdErr: {ioerr:02X}h")
                    print(f'\nVerify IO ERROR {ioerr:02X}h.')
                    self.fxio.motoroff()
                    wx.CallAfter(self.Stop)
                    return
                wx.CallAfter(self.UpdateStatus, "CRC")
                amigacrc = self.fxio.callusr()
                wx.CallAfter(self.UpdateCrc, amigacrc)
                if amigacrc != self.snip.keysum(trackdump):
                    wx.CallAfter(self.UpdateStatus, "CRC Error.")
                    print('\nVerify CRC ERROR.')
                    self.fxio.motoroff()
                    wx.CallAfter(self.Stop)
                    return
        wx.CallAfter(self.UpdateTrack, 0, 0, "Seek")
        self.fxio.settrack(0)
        self.fxio.seek()
        print("Done     ")
        self.fxio.motoroff()
        wx.CallAfter(self.UpdateStatus, "Done.")
        wx.CallAfter(self.Stop)
        return
    def CompareDiskAdf(self, drive, adf):
        try:
            with open(adf, "rb") as fh:
                diskdump = fh.read()
        except:
            diskdump = b""
        if len(diskdump) != self.tracksize * 160:
            self.UpdateStatus("ADF Error.")
            self.Stop()
            return
        threading.Thread(target=self.CompareDiskAdfWorker, args=(drive, diskdump)).start()
    def CompareDiskAdfWorker(self, drive, diskdump):
        wx.CallAfter(self.UpdateProgressRange, 159)
        self.fxio.setioreq(self.getioreq(drive))
        for track in range(0, 160):
            wx.CallAfter(self.UpdateProgressValue, track)
            cyl = track // 2
            side = track % 2
            print(f'Comparing Cyl:{cyl:02} Side:{side}', end='\r', flush=True)
            wx.CallAfter(self.UpdateTrack, cyl, side, "Read")
            startpos = track * self.tracksize
            endpos = startpos + self.tracksize
            trackdump = diskdump[startpos:endpos]
            if self.abort.is_set():
                wx.CallAfter(self.UpdateStatus, "UserStop.")
                print("\nUser stopped.")
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                return
            self.fxio.settrack(track)
            ioerr = self.fxio.trackread()
            if ioerr == self.IOERR_NOFLOPPY:
                wx.CallAfter(self.UpdateStatus, "NoFloppy?")
                print("\nIOERR_NOFLOPPY.")
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                return
            elif ioerr:
                wx.CallAfter(self.UpdateStatus, f"RdErr: {ioerr:02X}h")
                print(f'\nRead IO ERROR {ioerr:02X}h.')
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                return
            wx.CallAfter(self.UpdateStatus, "CRC")
            amigacrc = self.fxio.callusr()
            wx.CallAfter(self.UpdateCrc, amigacrc)
            if amigacrc != self.snip.keysum(trackdump):
                wx.CallAfter(self.UpdateStatus, "Differs.")
                print('\nCRC DIFFERS.')
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                return
        wx.CallAfter(self.UpdateTrack, 0, 0, "Seek")
        self.fxio.settrack(0)
        self.fxio.seek()
        print("Done     ")
        self.fxio.motoroff()
        wx.CallAfter(self.UpdateStatus, "Match.")
        wx.CallAfter(self.Stop)
        return
    def Disk2Adf(self, drive, adf, verify):
        if not adf:
            wx.CallAfter(self.UpdateStatus, "File?")
            print("No target file selected.")
            wx.CallAfter(self.Stop)
            return
        #FIXME: Ugly test. No better way?
        if os.path.exists(adf):
            if os.path.isfile(adf):
                if not os.access(adf, os.W_OK):
                    wx.CallAfter(self.UpdateStatus, "FilePerm?")
                    print("Target is not writable.")
                    wx.CallAfter(self.Stop)
                    return
            else:
                wx.CallAfter(self.UpdateStatus, "FileNot?")
                print("Target is not a file.")
                wx.CallAfter(self.Stop)
                return
        else:
            adfdir = os.path.dirname(adf)
            if os.path.exists(adfdir):
                if not os.access(adfdir, os.W_OK):
                    wx.CallAfter(self.UpdateStatus, "DirPerm?")
                    print("Target directory is not writable.")
                    wx.CallAfter(self.Stop)
                    return
            else:
                wx.CallAfter(self.UpdateStatus, "FileDir?")
                print("Target directory does not exist.")
                wx.CallAfter(self.Stop)
                return
        threading.Thread(target=self.Disk2AdfWorker, args=(drive, adf, verify)).start()
        return
    def Disk2AdfWorker(self, drive, adf, verify):
        wx.CallAfter(self.UpdateProgressRange, 159)
        diskdump = bytearray()
        self.fxio.setioreq(self.getioreq(drive))
        for track in range(0, 160):
            wx.CallAfter(self.UpdateProgressValue, track)
            cyl = track // 2
            side = track % 2
            if self.abort.is_set():
                wx.CallAfter(self.UpdateStatus, "UserStop.")
                print("\nUser stopped.")
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                return
            print(f'Reading   Cyl:{cyl:02} Side:{side}', end='\r', flush=True)
            wx.CallAfter(self.UpdateTrack, cyl, side, "Read")
            self.fxio.settrack(track)
            ioerr = self.fxio.trackread()
            if ioerr == self.IOERR_NOFLOPPY:
                wx.CallAfter(self.UpdateStatus, "NoFloppy?")
                print("\nIOERR_NOFLOPPY.")
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                return
            elif ioerr:
                wx.CallAfter(self.UpdateStatus, f"RdErr: {ioerr:02X}h")
                print(f'\nRead IO ERROR {ioerr:02X}h.')
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                return
            if self.abort.is_set():
                wx.CallAfter(self.UpdateStatus, "UserStop.")
                print("\nUser stopped.")
                self.fxio.motoroff()
                wx.CallAfter(self.Stop)
                return
            wx.CallAfter(self.UpdateTrack, cyl, side, "Xfer")
            trackdump = self.fxio.recvbuffer()
            if verify:
                wx.CallAfter(self.UpdateStatus, "CRC")
                amigacrc = self.fxio.callusr()
                wx.CallAfter(self.UpdateCrc, amigacrc)
                if amigacrc != self.snip.keysum(trackdump):
                    wx.CallAfter(self.UpdateStatus, "XFerCRCErr.")
                    print("\nXFER CRC ERROR.")
                    self.fxio.motoroff()
                    wx.CallAfter(self.Stop)
            diskdump += trackdump
        wx.CallAfter(self.UpdateTrack, 0, 0, "Seek")
        self.fxio.settrack(0)
        self.fxio.seek()
        print("Done     ")
        self.fxio.motoroff()
        if self.abort.is_set():
            wx.CallAfter(self.UpdateStatus, "UserStop.")
            print("\nUser stopped.")
            wx.CallAfter(self.Stop)
            return
        wx.CallAfter(self.UpdateStatus, "Saving")
        print(f'Saving as "{adf}".')
        try:
            with open(adf, "wb") as fh:
                fh.write(diskdump)
            print("ADF Saved.")
            wx.CallAfter(self.UpdateStatus, "Done.")
        except:
            print("Error writing adf file.")
            wx.CallAfter(self.UpdateStatus, "FileError.")
        wx.CallAfter(self.Stop)
        return
