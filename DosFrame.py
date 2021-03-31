import wx
import os
import re
import threading
from DosLibrary import DosLibrary
from DosUtils import DosUtils
class DosFrame(wx.Frame):
    def __init__(self):
        self.endcallback = None
        self.ser = None
        self.amiga = None
        self.execlib = None
        self.doslib = None
        self.snip = None
        self.wantclose = False
        self.busy = False
        self.bufaddr = None
        self.delay = 0
        self.delaydisk = 200
        super().__init__(None, id=wx.ID_ANY, title=u"amigaXfer DOS Tool", pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        bSizer7 = wx.BoxSizer(wx.VERTICAL)
        self.m_amigapathmsg = wx.StaticText(self, wx.ID_ANY, u"Amiga path", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_amigapathmsg.Wrap(-1)
        bSizer7.Add(self.m_amigapathmsg, 0, wx.ALL, 5)
        self.m_amigapath = wx.TextCtrl(self, wx.ID_ANY, u"RAM:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_amigapath.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        bSizer7.Add(self.m_amigapath, 0, wx.ALL | wx.EXPAND, 5)
        wSizer9 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)
        self.m_fromamiga = wx.Button(self, wx.ID_DOWN, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        wSizer9.Add(self.m_fromamiga, 0, wx.ALL, 5)
        self.m_xfermsg = wx.StaticText(self, wx.ID_ANY, u"Xfer", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_xfermsg.Wrap(-1)
        wSizer9.Add(self.m_xfermsg, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_toamiga = wx.Button(self, wx.ID_UP, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        wSizer9.Add(self.m_toamiga, 0, wx.ALL, 5)
        bSizer7.Add(wSizer9, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.m_localpathmsg = wx.StaticText(self, wx.ID_ANY, u"Local path", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_localpathmsg.Wrap(-1)
        bSizer7.Add(self.m_localpathmsg, 0, wx.ALL, 5)
        self.m_localpath = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"", wx.DefaultPosition, wx.DefaultSize, wx.FLP_OPEN | wx.FLP_USE_TEXTCTRL)
        bSizer7.Add(self.m_localpath, 0, wx.ALL | wx.EXPAND, 5)
        self.m_staticline2 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer7.Add(self.m_staticline2, 0, wx.EXPAND | wx.ALL, 5)
        self.m_progress = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        self.m_progress.SetValue(0)
        bSizer7.Add(self.m_progress, 0, wx.ALL | wx.EXPAND, 5)
        gSizer1 = wx.GridSizer(0, 2, 0, 0)
        wSizer10 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)
        self.m_status = wx.TextCtrl(self, wx.ID_ANY, u"Init", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.m_status.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        wSizer10.Add(self.m_status, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_overwrite = wx.CheckBox(self, wx.ID_ANY, u"Overwrite", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_overwrite.SetForegroundColour(wx.Colour(255, 0, 0))
        wSizer10.Add(self.m_overwrite, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gSizer1.Add(wSizer10, 0, wx.EXPAND, 5)
        self.m_exit = wx.Button(self, wx.ID_ANY, u"Exit", wx.DefaultPosition, wx.DefaultSize, 0)
        gSizer1.Add(self.m_exit, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        bSizer7.Add(gSizer1, 0, wx.EXPAND, 5)
        self.SetSizer(bSizer7)
        self.Layout()
        self.Centre(wx.BOTH)
        self.m_exit.Bind(wx.EVT_BUTTON, self.onExitPressed)
        self.m_overwrite.Bind(wx.EVT_CHECKBOX, self.onOverwriteCheckBox)
        self.m_toamiga.Bind(wx.EVT_BUTTON, self.onToAmigaPressed)
        self.m_fromamiga.Bind(wx.EVT_BUTTON, self.onFromAmigaPressed)
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
    def onOverwriteCheckBox(self, event):
        danger = self.m_overwrite.GetValue()
        if danger:
            self.fromamigacolor = self.m_fromamiga.GetForegroundColour()
            self.toamigacolor = self.m_toamiga.GetForegroundColour()
            self.xfermsgcolor = self.m_xfermsg.GetForegroundColour()
            self.m_fromamiga.SetForegroundColour(wx.Colour(255, 0, 0))
            self.m_toamiga.SetForegroundColour(wx.Colour(255, 0, 0))
            self.m_xfermsg.SetForegroundColour(wx.Colour(255, 0, 0))
        else:
            self.m_fromamiga.SetForegroundColour(self.fromamigacolor)
            self.m_toamiga.SetForegroundColour(self.toamigacolor)
            self.m_xfermsg.SetForegroundColour(self.xfermsgcolor)
        return
    def onToAmigaPressed(self, event):
        self.Enablement(False)
        self.UpdateStatus("Start")
        localpath = self.m_localpath.GetPath()
        amigapath = self.m_amigapath.GetValue()
        overwrite = self.m_overwrite.GetValue()
        threading.Thread(target=self.ToAmigaWorker, args=(localpath, amigapath, overwrite)).start()
        return
    def onFromAmigaPressed(self, event):
        self.Enablement(False)
        self.UpdateStatus("Start")
        localpath = self.m_localpath.GetPath()
        amigapath = self.m_amigapath.GetValue()
        overwrite = self.m_overwrite.GetValue()
        threading.Thread(target=self.FromAmigaWorker, args=(localpath, amigapath, overwrite)).start()
        return
    def Stop(self):
        self.doslib.Delay(self.delay)
        self.busy = False
        wx.CallAfter(self.UpdateProgressDone)
        if self.wantclose:
            wx.CallAfter(self.CleanUp)
        else:
            self.Enablement(True)
        return
    def ToAmigaWorker(self, localpath, amigapath, overwrite):
        if not amigapath:
            wx.CallAfter(self.UpdateStatus, "DstFile?")
            wx.CallAfter(self.Stop)
            return
        if not ':' in amigapath:
            wx.CallAfter(self.UpdateStatus, "DstVol?")
            wx.CallAfter(self.Stop)
            return
        wx.CallAfter(self.UpdateStatus, "Checks")
        vol = amigapath.split(':')[0]
        if vol.upper() == "RAM":
            self.delay = 0
        else:
            self.delay = self.delaydisk
        if vol[0:2].upper() == "DF":
            #diskchange, as floppies might have been swapped while interrupts disabled
            self.dosutil.inhibit(amigapath[0:4], self.doslib.DOSTRUE)
            self.dosutil.inhibit(amigapath[0:4], self.doslib.DOSFALSE)
        #FIXME: For huge filetransfers, it might make sense not to read the source file all at once.
        try:
            with open(localpath, "rb") as fh:
                data = fh.read()
        except:
            data = None
        if not data:
            wx.CallAfter(self.UpdateStatus, "SrcFile?")
            wx.CallAfter(self.Stop)
            return
        voladdr = self.snip.getaddrstr(vol + ':')
        lock = self.doslib.Lock(voladdr, self.doslib.ACCESS_READ)
        if not lock:
            print("Could not get read lock on volume.")
            wx.CallAfter(self.UpdateStatus, "DstVol?")
            wx.CallAfter(self.Stop)
            return
        if not self.doslib.Info(lock, self.bufaddr):
            print("Could not Info() lock.")
            self.doslib.UnLock(lock)
            wx.CallAfter(self.UpdateStatus, "InfoErr.")
            wx.CallAfter(self.Stop)
            return
        self.doslib.UnLock(lock)
        diskstate = self.amiga.speek32(self.bufaddr + self.doslib.id_DiskState)
        print(f"DiskState: {hex(diskstate)}.")
        if diskstate == self.doslib.ID_WRITE_PROTECTED:
            print(f"Disk state ID_WRITE_PROTECTED thus not writable.")
            wx.CallAfter(self.UpdateStatus, "WriteProt?")
            wx.CallAfter(self.Stop)
            return
        if diskstate == self.doslib.ID_VALIDATING:
            print(f"Disk state ID_VALIDATING thus not writable.")
            wx.CallAfter(self.UpdateStatus, "DskInval?")
            wx.CallAfter(self.Stop)
            return
        if diskstate != self.doslib.ID_VALIDATED:
            print(f"Disk state not ID_VALIDATED: {diskstate}")
            wx.CallAfter(self.UpdateStatus, "InfoUnk?!")
            wx.CallAfter(self.Stop)
            return
        amigapathaddr = self.snip.getaddrstr(amigapath)
        lock = self.doslib.Lock(amigapathaddr, self.doslib.ACCESS_READ)
        if lock:
            if not self.doslib.Examine(lock, self.bufaddr):
                print("Could not Examine() lock.")
                self.doslib.UnLock(lock)
                wx.CallAfter(self.UpdateStatus, "ExamErr.")
                wx.CallAfter(self.Stop)
                return
            self.doslib.UnLock(lock)
            filetype = self.amiga.speek32(self.bufaddr + self.doslib.fib_DirEntryType)
            print(f"Filetype: {filetype}")
            if (filetype < 0) and (not overwrite):
                print("File exists, and overwrite is not enabled.")
                wx.CallAfter(self.UpdateStatus, "OverWrit?")
                wx.CallAfter(self.Stop)
                return
            if filetype > 0:
                basename = os.path.basename(localpath)
                if amigapath[-1] != ":":
                    amigapath += "/"
                amigapath += basename
                amigapathaddr = self.snip.getaddrstr(amigapath)
                print(f"Target is a dir. New amigapath: {amigapath}")
                lock = self.doslib.Lock(amigapathaddr, self.doslib.ACCESS_READ)
                if lock:
                    if not self.doslib.Examine(lock, self.bufaddr):
                        print("Could not Examine() lock.")
                        self.doslib.UnLock(lock)
                        wx.CallAfter(self.UpdateStatus, "SrcFile?")
                        wx.CallAfter(self.Stop)
                        return
                    self.doslib.UnLock(lock)
                    filetype = self.amiga.speek32(self.bufaddr + self.doslib.fib_DirEntryType)
                    print(f"Filetype: {filetype}")
                    if filetype > 0:
                        print("Target directory exists, but name inside exists and is not a file.")
                        print(f"path: {localpath}")
                        wx.CallAfter(self.UpdateStatus, "LNotFile?")
                        wx.CallAfter(self.Stop)
                        return
                    if not overwrite:
                        print("File exists, and overwrite is not enabled.")
                        wx.CallAfter(self.UpdateStatus, "OverWrit?")
                        wx.CallAfter(self.Stop)
                        return
        print(f"Local path: {localpath}, Amiga path: {amigapath}.")
        dosfh = self.doslib.Open(amigapathaddr, self.doslib.MODE_NEWFILE)
        print(f"dosfh: {hex(dosfh)}")
        if not dosfh:
            wx.CallAfter(self.UpdateStatus, "DstFile?")
            wx.CallAfter(self.Stop)
            return
        blocks = len(data) // self.bufsize
        if len(data) % self.bufsize:
            blocks += 1
        wx.CallAfter(self.UpdateProgressRange, blocks)
        block = 0
        wx.CallAfter(self.UpdateProgressValue, 0)
        for offset in range(0, len(data), self.bufsize):
            remaining = len(data) - offset
            stepsize = min(remaining, self.bufsize)
            print(f"transferring {hex(stepsize)} at offset {hex(offset)} remaining {hex(remaining)}")
            wx.CallAfter(self.UpdateStatus, "Xfer+CRC")
            self.snip.verifiedwritemem(self.bufaddr, data[offset:offset + stepsize])
            wx.CallAfter(self.UpdateStatus, "Write")
            returnedLength = self.doslib.Write(dosfh, self.bufaddr, stepsize)
            if returnedLength != stepsize:
                print(f"Error: size written != requested length.")
                wx.CallAfter(self.UpdateStatus, "IOErr.")
                success = self.doslib.Close(dosfh)
                wx.CallAfter(self.Stop)
            print(f"returnedLength: {hex(returnedLength)}")
            block += 1
            wx.CallAfter(self.UpdateProgressValue, block)
        wx.CallAfter(self.UpdateStatus, "Close")
        success = self.doslib.Close(dosfh)
        wx.CallAfter(self.UpdateStatus, "Done.")
        wx.CallAfter(self.Stop)
        return
    def FromAmigaWorker(self, localpath, amigapath, overwrite):
        wx.CallAfter(self.UpdateProgressPulse)
        if not amigapath or amigapath[-1] == ':' or amigapath[-1] == '/':
            wx.CallAfter(self.UpdateStatus, "SrcFile?")
            wx.CallAfter(self.Stop)
            return
        if amigapath[0:4].upper() == "RAM:":
            self.delay = 0
        else:
            self.delay = self.delaydisk
        if amigapath[0:2].upper() == "DF":
            #diskchange, as floppies might have been swapped while interrupts disabled
            self.dosutil.inhibit(amigapath[0:4], self.doslib.DOSTRUE)
            self.dosutil.inhibit(amigapath[0:4], self.doslib.DOSFALSE)
        if os.path.exists(localpath) and not os.path.isfile(localpath):
            if not os.access(localpath, os.W_OK):
                wx.CallAfter(self.UpdateStatus, "LDirPerm?")
                print("Target directory is not writable.")
                wx.CallAfter(self.Stop)
                return
            else:
                basename = re.split(':|/', amigapath)[-1]
                localpath = os.path.join(localpath, basename)
        if os.path.exists(localpath):
            if os.path.isfile(localpath):
                if not os.access(localpath, os.W_OK):
                    print("Target is not writable.")
                    wx.CallAfter(self.UpdateStatus, "LFilePerm?")
                    wx.CallAfter(self.Stop)
                    return
                elif not overwrite:
                    print("File exists, and overwrite is not enabled.")
                    wx.CallAfter(self.UpdateStatus, "OverWrit?")
                    wx.CallAfter(self.Stop)
                    return
            else:
                print("Target directory exists, but name inside exists and is not a file.")
                print(f"path: {localpath}")
                wx.CallAfter(self.UpdateStatus, "LNotFile?")
                wx.CallAfter(self.Stop)
                return
        print(f"Local path: {localpath}, Amiga path: {amigapath}.")
        try:
            fh = open(localpath, "wb")
        except:
            fh = None
        if not fh:
            print("Could not open destination file.")
            wx.CallAfter(self.UpdateStatus, "DstFile?")
            wx.CallAfter(self.Stop)
            return
        amigapathaddr = self.snip.getaddrstr(amigapath)
        lock = self.doslib.Lock(amigapathaddr, self.doslib.ACCESS_READ)
        if not lock:
            print("Could not Lock() source file.")
            wx.CallAfter(self.UpdateStatus, "SrcFile?")
            wx.CallAfter(self.Stop)
            return
        if not self.doslib.Examine(lock, self.bufaddr):
            print("Could not Examine() lock.")
            self.doslib.UnLock(lock)
            wx.CallAfter(self.UpdateStatus, "SrcFile?")
            wx.CallAfter(self.Stop)
            return
        self.doslib.UnLock(lock)
        length = self.amiga.peek32(self.bufaddr + self.doslib.fib_Size)
        print(f"Source file length: {length}")
        dosfh = self.doslib.Open(amigapathaddr, self.doslib.MODE_OLDFILE)
        if not dosfh:
            print("Could not Open() source file.")
            wx.CallAfter(self.UpdateStatus, "SrcFile?")
            wx.CallAfter(self.Stop)
            return
        blocks = length // self.bufsize
        if length % self.bufsize:
            blocks += 1
        wx.CallAfter(self.UpdateProgressRange, blocks)
        block = 0
        wx.CallAfter(self.UpdateProgressValue, block)
        for offset in range(0, length, self.bufsize):
            wx.CallAfter(self.UpdateStatus, "Read")
            remaining = length - offset
            stepsize = min(remaining, self.bufsize)
            actualLength = self.doslib.Read(dosfh, self.bufaddr, self.bufsize)
            if actualLength != stepsize:
                print("Error reading file.")
                self.doslib.Close(dosfh)
                wx.CallAfter(self.UpdateStatus, "IOErr.")
                wx.CallAfter(self.Stop)
                return
            wx.CallAfter(self.UpdateStatus, "Xfer+CRC")
            fh.write(self.snip.verifiedreadmem(self.bufaddr, actualLength))
            block += 1
            wx.CallAfter(self.UpdateProgressValue, block)
        wx.CallAfter(self.UpdateStatus, "Close")
        fh.close()
        success = self.doslib.Close(dosfh)
        wx.CallAfter(self.UpdateStatus, "Done.")
        wx.CallAfter(self.Stop)
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
    def Enablement(self, enable):
        self.m_exit.Enable(enable)
        self.m_overwrite.Enable(enable)
        self.m_fromamiga.Enable(enable)
        self.m_toamiga.Enable(enable)
        self.m_localpath.Enable(enable)
        self.m_amigapath.Enable(enable)
        return
    def DosSetup(self, endcallback, ser, amiga, execlib, snip):
        self.Bind(wx.EVT_CLOSE, self.onCloseSetup)
        self.m_status.ChangeValue(u'Setup')
        self.endcallback = endcallback
        self.ser = ser
        self.amiga = amiga
        self.execlib = execlib
        self.snip = snip
        threading.Thread(target=self.DosSetupWorker).start()
        return
    def DosSetupWorker(self):
        wx.CallAfter(self.UpdateStatus, "Buffer")
        avail = self.execlib.AvailMem(self.execlib.MEMF_PUBLIC)
        largest = self.execlib.AvailMem(self.execlib.MEMF_LARGEST | self.execlib.MEMF_PUBLIC)
        print(f"MEMF_PUBLIC avail {hex(avail)}, largest {hex(largest)}")
        if avail > 1024 * 1024 * 2 and largest >= 256 * 1024:
            self.bufsize = 256 * 1024
        elif avail > 1024 * 1024 and largest >= 128 * 1024:
            self.bufsize = 128 * 1024
        elif avail > 512 * 1024 and largest >= 64 * 1024:
            self.bufsize = 64 * 1024
        elif avail > 256 * 1024 and largest >= 16 * 1024:
            self.bufsize = 16 * 1024
        elif largest > 4096:
            self.bufsize = 4096
        else:
            print("RAM is too low, bailing out")
            wx.CallAfter(self.DosSetupFail)
            return
        print(f"Allocating bufsize {hex(self.bufsize)}")
        self.bufaddr = self.execlib.AllocMem(self.bufsize, self.execlib.MEMF_PUBLIC)
        dosname = self.snip.getaddrstr("dos.library")
        self.dosbase = self.execlib.OldOpenLibrary(dosname)
        if not self.dosbase:
            wx.CallAfter(self.UpdateStatus, "NoDOS?!")
        self.doslib = DosLibrary(debugger=self.amiga, base=self.dosbase)
        self.dosutil = DosUtils(debugger=self.amiga, execlib=self.execlib, doslib=self.doslib, snippets=self.snip)
        wx.CallAfter(self.DosSetupDone)
        return
    def DosSetupFail(self):
        wx.CallAfter(self.endcallback)
        return
    def DosSetupDone(self):
        wx.CallAfter(self.UpdateStatus, "Ready.")
        wx.CallAfter(self.Enablement, True)
        self.Unbind(wx.EVT_CLOSE, handler=self.onCloseSetup)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        return
    def CleanUp(self):
        self.Enablement(False)
        threading.Thread(target=self.CleanUpWorker).start()
        return
    def CleanUpWorker(self):
        print("CleanUp start.")
        self.execlib.FreeMem(self.bufaddr, self.bufsize)
        self.execlib.CloseLibrary(self.dosbase)
        print("CleanUp done.")
        wx.CallAfter(self.endcallback)
        return
