import wx
class MenuFrame(wx.Frame):
    def __init__(self, endcallback):
        self.endcallback = endcallback
        self.wantclose = False
        super().__init__(None, id=wx.ID_ANY, title=u"amigaXfer", pos=wx.DefaultPosition, size=wx.Size(250, 425), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        bSizer6 = wx.BoxSizer(wx.VERTICAL)
        self.m_floppy = wx.Button(self, wx.ID_ANY, u"Floppy Tool", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_floppy.SetToolTip(u"Read/Write/Compare Floppies with ADFs")
        bSizer6.Add(self.m_floppy, 0, wx.ALL | wx.EXPAND, 5)
        self.m_bootblock = wx.Button(self, wx.ID_ANY, u"Bootblock Tool", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_bootblock.SetToolTip(u"Install bootblocks")
        bSizer6.Add(self.m_bootblock, 0, wx.ALL | wx.EXPAND, 5)
        self.m_dos = wx.Button(self, wx.ID_ANY, u"DOS Tool (preview)", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_dos.SetToolTip(u"File transfer (prototype)")
        bSizer6.Add(self.m_dos, 0, wx.ALL | wx.EXPAND, 5)
        self.m_rom = wx.Button(self, wx.ID_ANY, u"ROM Tool", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_rom.SetToolTip(u"Dump Kickstart ROM")
        bSizer6.Add(self.m_rom, 0, wx.ALL | wx.EXPAND, 5)
        self.m_about = wx.Button(self, wx.ID_ANY, u"About", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_about, 0, wx.ALL | wx.EXPAND, 5)
        bSizer6.Add((0, 0), 1, wx.EXPAND, 5)
        self.m_staticline1 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer6.Add(self.m_staticline1, 0, wx.EXPAND | wx.ALL, 5)
        self.m_exitmsg = wx.StaticText(self, wx.ID_ANY, u"Exit and...", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_exitmsg.Wrap(-1)
        bSizer6.Add(self.m_exitmsg, 0, wx.ALL, 5)
        self.m_exitreset = wx.Button(self, wx.ID_ANY, u"Reset", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_exitreset.SetToolTip(u"Reboots the Amiga")
        bSizer6.Add(self.m_exitreset, 0, wx.ALL | wx.EXPAND, 5)
        self.m_exithardreset = wx.Button(self, wx.ID_ANY, u"Hard Reset", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_exithardreset.SetToolTip(u"Triggers rebuild of execbase")
        bSizer6.Add(self.m_exithardreset, 0, wx.ALL | wx.EXPAND, 5)
        self.m_exitdebug = wx.Button(self, wx.ID_ANY, u"Debug", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_exitdebug.SetToolTip(u"Leaves debugger running")
        bSizer6.Add(self.m_exitdebug, 0, wx.ALL | wx.EXPAND, 5)
        self.m_exitresume = wx.Button(self, wx.ID_ANY, u"Resume", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_exitresume.SetToolTip(u"Exits debugger")
        bSizer6.Add(self.m_exitresume, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(bSizer6)
        self.Layout()
        self.Centre(wx.BOTH)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.m_about.Bind(wx.EVT_BUTTON, self.onAboutPressed)
        self.m_floppy.Bind(wx.EVT_BUTTON, self.onFloppyPressed)
        self.m_bootblock.Bind(wx.EVT_BUTTON, self.onBootblockPressed)
        self.m_dos.Bind(wx.EVT_BUTTON, self.onDosPressed)
        self.m_rom.Bind(wx.EVT_BUTTON, self.onRomPressed)
        self.m_exitreset.Bind(wx.EVT_BUTTON, self.onExitResetPressed)
        self.m_exithardreset.Bind(wx.EVT_BUTTON, self.onExitHardResetPressed)
        self.m_exitdebug.Bind(wx.EVT_BUTTON, self.onExitDebugPressed)
        self.m_exitresume.Bind(wx.EVT_BUTTON, self.onExitResumePressed)
        return
    def MenuSetup(self, process, resetfirst):
        self.resetfirst = resetfirst
        self.m_dos.Enable(process)
        self.m_exitreset.Enable(not resetfirst)
        self.m_exitdebug.Enable(not resetfirst)
        self.m_exitresume.Enable(not resetfirst)
        return
    def onClose(self, event):
        if event.CanVeto():
            event.Veto()
        if self.resetfirst:
            wx.CallAfter(self.endcallback, "exithardreset")
        else:
            wx.CallAfter(self.endcallback, "exitresume")
        return
    def onAboutPressed(self, event):
        app = wx.GetApp()
        app.ShowAboutDialog()
        return
    def onFloppyPressed(self, event):
        wx.CallAfter(self.endcallback, "floppytool")
        return
    def onBootblockPressed(self, event):
        wx.CallAfter(self.endcallback, "bootblocktool")
        return
    def onDosPressed(self, event):
        wx.CallAfter(self.endcallback, "dostool")
        return
    def onRomPressed(self, event):
        wx.CallAfter(self.endcallback, "romtool")
        return
    def onExitResetPressed(self, event):
        wx.CallAfter(self.endcallback, "exitreset")
        return
    def onExitHardResetPressed(self, event):
        wx.CallAfter(self.endcallback, "exithardreset")
        return
    def onExitDebugPressed(self, event):
        wx.CallAfter(self.endcallback, "exitdebug")
        return
    def onExitResumePressed(self, event):
        wx.CallAfter(self.endcallback, "exitresume")
        return
