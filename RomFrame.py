import wx
import os
import threading
from RomUtils import RomUtils
class RomFrame(wx.Frame):
    def __init__(self):
        self.endcallback = None
        self.ser = None
        self.amiga = None
        self.execlib = None
        self.doslib = None
        self.snip = None
        self.abort = threading.Event()
        self.wantclose = False
        self.busy = False
        self.done = False
        self.stepsize = 0x4000
        super().__init__(None, id=wx.ID_ANY, title=u"amigaXfer ROM Tool", pos=wx.DefaultPosition, size=wx.Size(400, 250), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        bSizer10 = wx.BoxSizer(wx.VERTICAL)
        wSizer15 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)
        self.m_versionmsg = wx.StaticText(self, wx.ID_ANY, u"Version", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_versionmsg.Wrap(-1)
        wSizer15.Add(self.m_versionmsg, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_version = wx.TextCtrl(self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.m_version.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        maxlen = 5
        self.m_version.SetMaxLength(maxlen)
        self.m_version.SetInitialSize(self.m_version.GetSizeFromTextSize(self.m_version.GetTextExtent("A" * maxlen)))
        wSizer15.Add(self.m_version, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_revisionmsg = wx.StaticText(self, wx.ID_ANY, u"Revision", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_revisionmsg.Wrap(-1)
        wSizer15.Add(self.m_revisionmsg, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_revision = wx.TextCtrl(self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.m_revision.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        maxlen = 5
        self.m_revision.SetMaxLength(maxlen)
        self.m_revision.SetInitialSize(self.m_revision.GetSizeFromTextSize(self.m_version.GetTextExtent("A" * maxlen)))
        wSizer15.Add(self.m_revision, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        bSizer10.Add(wSizer15, 0, wx.EXPAND, 5)
        wSizer16 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)
        self.m_addrmsg = wx.StaticText(self, wx.ID_ANY, u"Address", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_addrmsg.Wrap(-1)
        wSizer16.Add(self.m_addrmsg, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_addr = wx.TextCtrl(self, wx.ID_ANY, u"00000000", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.m_addr.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        maxlen = 8
        self.m_addr.SetMaxLength(maxlen)
        self.m_addr.SetInitialSize(self.m_addr.GetSizeFromTextSize(self.m_version.GetTextExtent("A" * maxlen)))
        wSizer16.Add(self.m_addr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_sizemsg = wx.StaticText(self, wx.ID_ANY, u"Size", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_sizemsg.Wrap(-1)
        wSizer16.Add(self.m_sizemsg, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_size = wx.TextCtrl(self, wx.ID_ANY, u"00000", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.m_size.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        maxlen = 5
        self.m_size.SetMaxLength(maxlen)
        self.m_size.SetInitialSize(self.m_size.GetSizeFromTextSize(self.m_version.GetTextExtent("A" * maxlen)))
        wSizer16.Add(self.m_size, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        bSizer10.Add(wSizer16, 0, wx.EXPAND, 5)
        self.m_targetmsg = wx.StaticText(self, wx.ID_ANY, u"Target file", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_targetmsg.Wrap(-1)
        bSizer10.Add(self.m_targetmsg, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.m_target = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.rom", wx.DefaultPosition, wx.DefaultSize, wx.FLP_OVERWRITE_PROMPT | wx.FLP_SAVE | wx.FLP_USE_TEXTCTRL)
        bSizer10.Add(self.m_target, 0, wx.ALL | wx.EXPAND, 5)
        self.m_progress = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL)
        self.m_progress.SetValue(0)
        bSizer10.Add(self.m_progress, 0, wx.ALL | wx.EXPAND, 5)
        wSizer17 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)
        self.m_status = wx.TextCtrl(self, wx.ID_ANY, u"Init", wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY)
        self.m_status.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        maxlen = 9
        self.m_status.SetMaxLength(maxlen)
        self.m_status.SetInitialSize(self.m_status.GetSizeFromTextSize(self.m_version.GetTextExtent("A" * maxlen)))
        wSizer17.Add(self.m_status, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        wSizer17.Add((0, 0), 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.m_abort = wx.Button(self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_abort.Hide()
        self.m_abort.Bind(wx.EVT_BUTTON, self.onAbortPressed)
        wSizer17.Add(self.m_abort, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_dump = wx.Button(self, wx.ID_ANY, u"Dump", wx.DefaultPosition, wx.DefaultSize, 0)
        wSizer17.Add(self.m_dump, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_exit = wx.Button(self, wx.ID_ANY, u"Exit", wx.DefaultPosition, wx.DefaultSize, 0)
        wSizer17.Add(self.m_exit, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        bSizer10.Add(wSizer17, 1, wx.EXPAND, 5)
        self.SetSizer(bSizer10)
        self.Layout()
        self.Centre(wx.BOTH)
        self.m_exit.Bind(wx.EVT_BUTTON, self.onExitPressed)
        self.m_dump.Bind(wx.EVT_BUTTON, self.onDumpPressed)
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
        if not self.done:
            self.m_target.Enable(enable)
            self.m_dump.Enable(enable)
        self.m_exit.Enable(enable)
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
            wx.CallAfter(self.Abort)
            return
        self.UpdateStatus("UserClose")
        self.CleanUp()
        return
    def onExitPressed(self, event):
        self.wantclose = True
        wx.CallAfter(self.UpdateStatus, "CleanUp")
        wx.CallAfter(self.CleanUp)
        return
    def onAbortPressed(self, event):
        self.Abort()
        return
    def Abort(self):
        self.m_abort.Enable(False)
        self.abort.set()
        return
    def onDumpPressed(self, event):
        self.Enablement(False)
        self.abort.clear()
        self.busy = True
        self.m_abort.Enable(True)
        self.m_dump.Hide()
        self.m_abort.Show()
        self.Layout()
        self.UpdateStatus("Start")
        localpath = self.m_target.GetPath()
        debug = False
        if not localpath:
            wx.CallAfter(self.UpdateStatus, "File?")
            print("No target file selected.")
            wx.CallAfter(self.Stop)
            return
        #FIXME: Ugly test. No better way?
        if os.path.exists(localpath):
            if os.path.isfile(localpath):
                if not os.access(localpath, os.W_OK):
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
            localpathdir = os.path.dirname(localpath)
            if os.path.exists(localpathdir):
                if not os.access(localpathdir, os.W_OK):
                    wx.CallAfter(self.UpdateStatus, "DirPerm?")
                    print("Target directory is not writable.")
                    wx.CallAfter(self.Stop)
                    return
            else:
                wx.CallAfter(self.UpdateStatus, "FileDir?")
                print("Target directory does not exist.")
                wx.CallAfter(self.Stop)
                return
        self.busy = True
        threading.Thread(target=self.DumpWorker, args=(localpath, debug)).start()
        return
    def DumpWorker(self, localpath, debug):
        romdump = bytearray()
        romaddr = self.romutil.getaddr()
        length = self.romutil.getsize()
        blocks = length / self.stepsize
        wx.CallAfter(self.UpdateProgressRange, blocks)
        block = 0
        for addr in range(romaddr, romaddr+length, self.stepsize):
            wx.CallAfter(self.UpdateStatus, f"{addr:x}")
            wx.CallAfter(self.UpdateProgressValue, block)
            print(f"read+crc size: {hex(self.stepsize)}, addr: {hex(addr)}.", end='\r', flush=True)
            blockdump = self.snip.verifiedreadmem(addr, self.stepsize)
            romdump += blockdump
            block += 1
            if self.abort.is_set():
                wx.CallAfter(self.UpdateStatus, "UserStop.")
                print("\nUser stopped.")
                wx.CallAfter(self.Stop)
                return
        wx.CallAfter(self.UpdateStatus, "Write")
        print(f"\nWriting ROM dump to {localpath}.")
        with open(localpath, "wb") as fh:
            fh.write(romdump)
        self.done = True
        print("Done.")
        wx.CallAfter(self.UpdateStatus, "Done.")
        wx.CallAfter(self.Stop)
        return
    def Stop(self):
        self.busy = False
        self.m_abort.Hide()
        self.m_dump.Show()
        self.Layout()
        if self.abort.is_set():
            wx.CallAfter(self.UpdateProgressValue, 0)
        else:
            wx.CallAfter(self.UpdateProgressDone)
        if self.wantclose:
            self.UpdateStatus("UserClose")
            self.CleanUp()
        self.Enablement(True)
        return
    def RomSetup(self, endcallback, ser, amiga, execlib, snip):
        self.Bind(wx.EVT_CLOSE, self.onCloseSetup)
        self.m_status.ChangeValue(u'Setup')
        self.endcallback = endcallback
        self.ser = ser
        self.amiga = amiga
        self.execlib = execlib
        self.snip = snip
        self.done = False
        self.wantclose = False
        threading.Thread(target=self.RomSetupWorker).start()
        return
    def RomSetupWorker(self):
        romutil = RomUtils(debugger=self.amiga)
        self.romutil = romutil
        wx.CallAfter(self.RomSetupDone)
        return
    def RomSetupDone(self):
        self.m_version.ChangeValue(f"{self.romutil.getversion()}")
        self.m_revision.ChangeValue(f"{self.romutil.getrevision()}")
        self.m_addr.ChangeValue(f"{self.romutil.getaddr():x}")
        self.m_size.ChangeValue(f"{self.romutil.getsize()//1024}K")
        wx.CallAfter(self.UpdateProgressValue, 0)
        wx.CallAfter(self.UpdateStatus, "Ready.")
        wx.CallAfter(self.Enablement, True)
        self.Unbind(wx.EVT_CLOSE, handler=self.onCloseSetup)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        return
    def CleanUp(self):
        self.Enablement(False)
        wx.CallAfter(self.endcallback)
        return
