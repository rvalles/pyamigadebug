import os
import time
import threading
import serial
import serial.tools.list_ports
import wx
from RomWack import RomWack
from SAD import SAD
from ExecLibrary import ExecLibrary
from AmigaSnippets import AmigaSnippets
class SetupDialog(wx.Frame):
    #(CLK/BAUDRATE)-1 = SERPER
    #CLK/(SERPER+1) = BAUDRATE
    #(serper, bps)
    #3546895 PALCLK Hz
    baudtablePAL=[
        (372, 9600), #368, but romwack/sad value to avoid trouble
        (183, 19200),
        (91, 38400),
        (60, 57600),
        (29, 115200),
        (13, 253349),
        (6, 506699),
        (4, 709379)
        ]
    #3579545 NTSCCLK Hz
    baudtableNTSC=[
        (372, 9600),
        (185, 19200),
        (92, 38400),
        (61, 57600),
        (30, 115200),
        (13, 255681),
        (6, 511363),
        (4, 715909)
        ]
    def __init__(self, endcallback):
        self.endcallback = endcallback
        self.syncabort = threading.Event()
        super().__init__(None, id=wx.ID_ANY, title=u"amigaXfer Setup", pos=wx.DefaultPosition, size=wx.Size(512, 225), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        gbSizer1 = wx.GridBagSizer(0, 0)
        gbSizer1.SetFlexibleDirection(wx.BOTH)
        gbSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        self.m_portmsg = wx.StaticText(self, wx.ID_ANY, u"Port", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_portmsg.Wrap(-1)
        gbSizer1.Add(self.m_portmsg, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        m_portChoices = [port for (port,desc,hwid) in serial.tools.list_ports.comports()]
        m_portChoices.reverse()
        self.m_port = wx.ComboBox(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_portChoices, 0)
        self.m_port.SetSelection(0)
        gbSizer1.Add(self.m_port, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_baudratemsg = wx.StaticText(self, wx.ID_ANY, u"Xfer Baudrate", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_baudratemsg.Wrap(-1)
        gbSizer1.Add(self.m_baudratemsg, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        m_baudrateChoices = [u"9600", u"19200", u"38400", u"57600", u"115200", u"256k", u"512k"]
        self.m_baudrate = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_baudrateChoices, 0)
        self.m_baudrate.SetSelection(4)
        gbSizer1.Add(self.m_baudrate, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALL, 5)
        bSizer1.Add(gbSizer1, 0, wx.EXPAND, 5)
        m_debuggerChoices = [u"RomWack (exec v37-)", u"SAD (exec v39+)"]
        self.m_debugger = wx.RadioBox(self, wx.ID_ANY, u"Debugger", wx.DefaultPosition, wx.DefaultSize, m_debuggerChoices, 1, wx.RA_SPECIFY_ROWS)
        self.m_debugger.SetSelection(0)
        bSizer1.Add(self.m_debugger, 0, wx.ALL | wx.EXPAND, 5)
        wSizer1 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)
        self.m_dangerfast = wx.CheckBox(self, wx.ID_ANY, u"DangerFast", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_dangerfast.Hide()
        self.m_dangerfast.SetForegroundColour(wx.Colour(255, 0, 0))
        self.m_dangerfast.SetToolTip(u"Dev's hardcoded speeds")
        self.m_dangerfast.Bind(wx.EVT_CHECKBOX, self.onCheckBox)
        wSizer1.Add(self.m_dangerfast, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_crashentry = wx.CheckBox(self, wx.ID_ANY, u"CrashEntry", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_crashentry.SetToolTip(u"Refer to bootstrap doc")
        self.m_crashentry.Bind(wx.EVT_CHECKBOX, self.onCheckBox)
        wSizer1.Add(self.m_crashentry, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_resetfirst = wx.CheckBox(self, wx.ID_ANY, u"ResetFirst", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_resetfirst.SetToolTip(u"Reboots for cleaner env")
        self.m_resetfirst.Bind(wx.EVT_CHECKBOX, self.onCheckBox)
        wSizer1.Add(self.m_resetfirst, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_paranoid = wx.CheckBox(self, wx.ID_ANY, u"Paranoid", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_paranoid.SetToolTip(u"AmigaSnippets verifyuse (slow)")
        wSizer1.Add(self.m_paranoid, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_debug = wx.CheckBox(self, wx.ID_ANY, u"Debug", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_debug.SetToolTip(u"Extra debug text")
        wSizer1.Add(self.m_debug, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_logwindow = wx.CheckBox(self, wx.ID_ANY, u"LogWindow", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_logwindow.SetToolTip(u"Redirect log to a window")
        self.m_logwindow.SetValue(True)
        wSizer1.Add(self.m_logwindow, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        bSizer1.Add(wSizer1, 1, wx.EXPAND, 5)
        wSizer14 = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)
        self.m_quit = wx.Button(self, wx.ID_ANY, u"Quit", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_quit.Bind(wx.EVT_BUTTON, self.onQuitPressed)
        wSizer14.Add(self.m_quit, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.m_about = wx.Button(self, wx.ID_ANY, u"About", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_about.Bind(wx.EVT_BUTTON, self.onAbout)
        wSizer14.Add(self.m_about, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.m_connect = wx.Button(self, wx.ID_ANY, u"Connect", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_connect.Bind(wx.EVT_BUTTON, self.DebuggerConnect)
        wSizer14.Add(self.m_connect, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        bSizer1.Add(wSizer14, 0, wx.ALIGN_RIGHT, 5)
        self.SetSizer(bSizer1)
        self.Layout()
        self.Fit()
        self.Centre(wx.BOTH)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        #FIXME: Secret tickboxes.
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        return
    def onCheckBox(self, event):
        self.Enablement(True)
        return
    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SHIFT:
            self.m_dangerfast.Show()
            self.Layout()
        event.Skip()
        return
    def onClose(self, event):
        if event.CanVeto():
            event.Veto()
        self.Quit()
        return
    def onQuitPressed(self, event):
        self.Quit()
        return
    def Quit(self):
        self.syncabort.set()
        wx.Exit()
        return
    def onAbout(self, event):
        app = wx.GetApp()
        app.ShowAboutDialog()
        return
    def DebuggerConnectFail(self):
        wx.MessageBox("Serial port could not be opened.\n\nWrong serial port or incompatible baudrate\n\nNote the standard PC serial port is limited to 115200. For higher speeds, use USB-serial adapters.", "ERROR", wx.OK|wx.ICON_ERROR)
        self.Enablement(True)
        return
    def Enablement(self, enable):
        crashentry = self.m_crashentry.GetValue()
        dangerfast = self.m_dangerfast.GetValue()
        self.m_debugger.Enable(enable)
        self.m_paranoid.Enable(enable)
        self.m_debug.Enable(enable)
        self.m_crashentry.Enable(enable)
        self.m_dangerfast.Enable(enable)
        self.m_logwindow.Enable(enable)
        self.m_connect.Enable(enable)
        self.m_about.Enable(enable)
        self.m_port.Enable(enable)
        self.m_portmsg.Enable(enable)
        if crashentry:
            self.m_resetfirst.Enable(False)
        else:
            self.m_resetfirst.Enable(enable)
        if (not crashentry) and (not dangerfast):
            self.m_baudrate.Enable(enable)
            self.m_baudratemsg.Enable(enable)
        else:
            self.m_baudrate.Enable(False)
            self.m_baudratemsg.Enable(False)
        return
    def DebuggerConnect(self, event): #Using name "Connect" would painfully override wx.
        self.Enablement(False)
        serialdev = self.m_port.GetValue()
        baudrate = self.m_baudrate.GetSelection()
        ntscbaudrate = self.baudtableNTSC[baudrate][1]
        debugger = self.m_debugger.GetSelection()
        paranoid = self.m_paranoid.GetValue()
        debug = self.m_debug.GetValue()
        dangerfast = self.m_dangerfast.GetValue()
        logwindow = self.m_logwindow.GetValue()
        crashentry = self.m_crashentry.GetValue()
        resetfirst = self.m_resetfirst.GetValue()
        if crashentry:
            resetfirst = True
        if logwindow:
            wx.GetApp().RedirectStdio()
        with open("nativeobjs.list", "r") as fh:
            asmfiles = fh.read().splitlines()
        missing = False
        for asmfile in asmfiles:
            if not os.path.isfile(asmfile):
                missing = True
                print(f"Object file {asmfile} is missing.")
        if missing:
            wx.MessageBox("Some m68k object files are missing.\n\nBuild missing objects or copy them from matching Windows binary release archive.\n\namigaXfer might work partially or not at all until resolved.", "ERROR", wx.OK|wx.ICON_ERROR)
        print(f'port {serialdev}, baud {baudrate}, debugger {debugger}, paranoid {paranoid}, debug {debug}, dangerfast {dangerfast}, resetfirst {resetfirst}, crashentry {crashentry}')
        if crashentry:
            print("*** Crash entry mode: Refer to bootstrapping documentation.")
            print("Overriding settings for safety. Serial will run at 9600.")
            baudrate = 0
            #debug = True
            paranoid = False
            try:
                ser = serial.Serial(serialdev, 9600, timeout=None, exclusive=True)
            except:
                print("Serial device could not be opened.")
                wx.CallAfter(self.DebuggerConnectFail)
                return
        else:
            try:
                ser = serial.Serial(serialdev, ntscbaudrate, timeout=None, exclusive=True)
            except:
                print(f"Serial device {serialdev} could not be opened at {ntscbaudrate} baud.")
                wx.CallAfter(self.DebuggerConnectFail)
                return
        print("Serial device opened.")
        self.ser = ser
        if resetfirst:
            threading.Thread(target=self.ResetFirstWorker, args=(baudrate, debugger, paranoid, debug, dangerfast, resetfirst, crashentry)).start()
        else:
            threading.Thread(target=self.DebuggerConnectWorker, args=(baudrate, debugger, paranoid, debug, dangerfast, resetfirst, crashentry)).start()
        return
    def DebuggerConnectWorker(self, baudrate, debugger, paranoid, debug, dangerfast, resetfirst, crashentry):
        if resetfirst:
            print('Syncing with debugger.')
        else:
            print('Syncing with debugger. Please have Amiga enter debugger now. Refer to README for help.')
        if debugger==0:
            self.debugger = RomWack(syncabort=self.syncabort, serial=self.ser, Debug=debug)
        elif debugger==1:
            self.debugger = SAD(syncabort=self.syncabort, serial=self.ser, Debug=debug)
        amiga = self.debugger
        if amiga.debugger == "SAD":
            print(f'In SAD debugger. Bugged: {amiga.sadbug}. Entry: {amiga.entry}.')
        else:
            print(f"In {amiga.debugger} debugger.")
        execlib = ExecLibrary(amiga)
        self.execlib = execlib
        print(f'Exec v{execlib.version}.{execlib.revision}. Base at {hex(execlib.base)}.')
        execlib.Disable() #romwack/sad unreliable at wire speed if interrupts on, on 000/010 7MHz.
        print("Disable.")
        savedregs = []
        if not resetfirst:
            print("Saving non-scratch registers.")
            savedregs = amiga.getregs(["a2", "a3", "a4", "a5", "a6", "a7", "d2", "d3", "d4", "d5", "d6", "d7"])
        if amiga.debugger == "SAD":
            execlib.enterdebugloop()
        clkpal = execlib.is_pal()
        if clkpal:
            (serper, baudrate) = self.baudtablePAL[baudrate]
        else:
            (serper, baudrate) = self.baudtableNTSC[baudrate]
        readmemserper=serper
        writememserper=serper
        readmembaudrate=baudrate
        writemembaudrate=baudrate
        if dangerfast:
            serper=6
            baudrate=506699
            readmemserper=3
            readmembaudrate=886723
            writememserper=5
            writemembaudrate=591149
        print(f'clkpal: {clkpal}, SERPER: {serper}, baud: {baudrate}')
        print(f'AmigaSnippets initialization start.')
        snip = AmigaSnippets(
            debugger=amiga,
            serial=self.ser,
            execlib=execlib,
            allocmem=execlib.AllocMem,
            verifyupload=True,
            verifyuse=paranoid,
            debug=debug,
            serper=serper,
            baudrate=baudrate,
            readmemserper=readmemserper,
            readmembaudrate=readmembaudrate,
            writememserper=writememserper,
            writemembaudrate=writemembaudrate)
        if snip.reusing:
            print("Reusing snippets.")
        else:
            print("Bootstrapped snippets.")
        self.snip = snip
        wx.CallAfter(self.endcallback, self.ser, self.debugger, self.execlib, self.snip, resetfirst, crashentry, savedregs)
        return
    def ResetFirstWorker(self, baudrate, debugger, paranoid, debug, dangerfast, resetfirst, crashentry):
        ser = self.ser
        if crashentry:
            print("Waiting for Amiga to enter unrecoverable alert routine (the blink + reboot + guru sort).")
            while not ser.in_waiting:
                ser.write(b'\x7F')
                time.sleep(0.3)
            print("Amiga is alive. Attempting debugger entry.")
        else:
            print('Syncing with debugger. Please have Amiga enter debugger now. Refer to README for help.')
        if debugger==0:
            amiga = RomWack(syncabort=self.syncabort, serial=self.ser, Debug=debug)
        elif debugger==1:
            amiga = SAD(syncabort=self.syncabort, serial=self.ser, Debug=debug)
        if amiga.debugger == "SAD":
            print(f'In SAD debugger. Bugged: {amiga.sadbug}. Entry: {amiga.entry}.')
        else:
            print(f"In {amiga.debugger} debugger.")
        print("Obtaining exec.library base and probing.")
        execlib = ExecLibrary(amiga)
        print(f'Exec v{execlib.version}.{execlib.revision}. Base at {hex(execlib.base)}.')
        print("Setting up CoolCapture.")
        amiga.poke32(execlib.base+execlib.CoolCapture, execlib.base+execlib.LVODebug)
        print("Updating sysvars checksum.")
        execlib.sysvarschksum()
        print("Clearing 'HELP' guru flag.")
        amiga.poke32(0, 0) #clear 'HELP' guru flag.
        print("Rebooting Amiga.")
        amiga.reboot()
        print("Waiting for debugger to show up.")
        if debugger==0:
            amiga = RomWack(syncabort=self.syncabort, serial=self.ser, Debug=debug)
        elif debugger==1:
            amiga = SAD(syncabort=self.syncabort, serial=self.ser, Debug=debug)
        if amiga.debugger == "SAD":
            print(f'In SAD debugger. Bugged: {amiga.sadbug}. Entry: {amiga.entry}.')
        else:
            print(f"In {amiga.debugger} debugger.")
        #execlib should be the same as before, else CoolCapture wouldn't be called, as execbase would have been rebuilt.
        if execlib.version < 36:
            print("Patching table of residents to disable strap.")
            execlib.removeresidentstrap()
        else:
            print("Preparing resident module structure with init pointing to Debug().")
            #Allocate chip just to ensure addr MSB is not set, as that has special meaning in resident table.
            debugromtag = execlib.AllocMem(execlib.rt_sizeof, execlib.MEMF_CLEAR|execlib.MEMF_CHIP)
            amiga.poke16(debugromtag+execlib.rt_MatchWord, execlib.RTC_MATCHWORD)
            amiga.poke32(debugromtag+execlib.rt_MatchTag, debugromtag)
            amiga.poke8(debugromtag+execlib.rt_Flags, 1)
            amiga.poke8(debugromtag+execlib.rt_Version, execlib.version) #not actually needed as far as I can tell, but polite.
            amiga.poke32(debugromtag+execlib.rt_Init, amiga.execdebug)
            print("Patching table of residents to replace strap with the prepared resident module.")
            execlib.replaceresidentbyname("strap", debugromtag)
        print("Releasing Amiga.")
        if execlib.version < 36:
            print("If all went well, without strap, Amiga will call Debug() after resident initialization.")
        else:
            print("If all went well, in place of strap, Amiga will call Debug() during resident initialization.")
        amiga.resume()
        self.DebuggerConnectWorker(baudrate, debugger, paranoid, debug, dangerfast, resetfirst, crashentry)
        return
