#!/usr/bin/env python3
import wx
import wx.adv
from SetupDialog import SetupDialog
from MenuFrame import MenuFrame
from FloppyFrame import FloppyFrame
from BootblockFrame import BootblockFrame
from DosFrame import DosFrame
from RomFrame import RomFrame
class AmigaXfer(wx.App):
    def __init__(self):
        super().__init__(redirect=False)
        self.floppyframe = None
        self.bootblockframe = None
        self.dosframe = None
        self.romframe = None
        return
    def OnInit(self):
        self.debugger = None
        self.toolmenu = MenuFrame(self.MenuDone)
        self.setupframe = SetupDialog(self.SetupDialogDone)
        self.setupframe.Show()
        return True
    def ShowAboutDialog(self):
        info = wx.adv.AboutDialogInfo()
        info.SetName("amigaXfer")
        info.SetVersion("1.0.1")
        info.SetDescription("Data transfer and tools for an Amiga on the serial port.")
        info.SetCopyright("(C) 2021 Roc Vallès i Domènech")
        wx.adv.AboutBox(info)
        return
    def SetupDialogDone(self, ser, amiga, execlib, snip, resetfirst, crashentry, regs):
        self.setupframe.Hide()
        self.ser = ser
        self.amiga = amiga
        self.execlib = execlib
        self.snip = snip
        self.resetfirst = resetfirst
        self.crashentry = crashentry
        self.savedregs = regs
        wx.CallAfter(self.menutool)
        return
    def FloppyToolDone(self):
        self.floppyframe.Hide()
        wx.CallAfter(self.menutool)
        return
    def BootblockToolDone(self):
        self.bootblockframe.Hide()
        wx.CallAfter(self.menutool)
        return
    def DosToolDone(self):
        self.dosframe.Hide()
        wx.CallAfter(self.menutool)
        return
    def RomToolDone(self):
        self.romframe.Hide()
        wx.CallAfter(self.menutool)
        return
    def MenuDone(self, choice):
        self.toolmenu.Hide()
        if choice == "exitresume":
            print(f"Exit method: {choice}.")
            print("Freeing snippets.")
            self.snip.freeall()
            print("Restoring non-scratch registers.")
            self.amiga.setregs(self.savedregs)
            print("Enable.")
            self.execlib.Enable()
            if self.amiga.debugger == "SAD":
                self.execlib.exitdebugloop()
            self.amiga.setreg("d0", 0)
            self.amiga.resume()
            wx.Exit()
        elif choice == "exitreset":
            print(f"Exit method: {choice}.")
            self.amiga.reboot()
            wx.Exit()
        elif choice == "exithardreset":
            print(f"Exit method: {choice}.")
            self.amiga.poke32(self.execlib.base+self.execlib.ColdCapture, 0)
            self.amiga.poke32(self.execlib.base+self.execlib.WarmCapture, 0xFFFFFFFF)
            self.amiga.reboot()
            wx.Exit()
        elif choice == "exitdebug":
            print(f"Exit method: {choice}.")
            print("Freeing snippets.")
            self.snip.freeall()
            print("Restoring non-scratch registers.")
            self.amiga.setregs(self.savedregs)
            self.amiga.setreg("d0", 0)
            print("Enable.")
            self.execlib.Enable()
            if self.amiga.debugger == "SAD":
                self.execlib.exitdebugloop()
            wx.Exit()
        elif choice == "floppytool":
            wx.CallAfter(self.floppytool)
        elif choice == "bootblocktool":
            wx.CallAfter(self.bootblocktool)
        elif choice == "dostool":
            wx.CallAfter(self.dostool)
        elif choice == "romtool":
            wx.CallAfter(self.romtool)
        else:
            print(f"Choice {choice} isn't implemented.")
        return
    def menutool(self):
        self.toolmenu.Show()
        wx.CallAfter(self.toolmenu.MenuSetup, self.execlib.is_process(), self.crashentry)
        return
    def floppytool(self):
        if not self.floppyframe:
            self.floppyframe = FloppyFrame()
        self.floppyframe.Show()
        wx.CallAfter(self.floppyframe.XferSetup, self.FloppyToolDone, self.ser, self.amiga, self.execlib, self.snip)
        return
    def bootblocktool(self):
        if not self.bootblockframe:
            self.bootblockframe = BootblockFrame()
        self.bootblockframe.Show()
        wx.CallAfter(self.bootblockframe.BootblockSetup, self.BootblockToolDone, self.ser, self.amiga, self.execlib, self.snip)
        return
    def dostool(self):
        if not self.dosframe:
            self.dosframe = DosFrame()
        self.dosframe.Show()
        wx.CallAfter(self.dosframe.DosSetup, self.DosToolDone, self.ser, self.amiga, self.execlib, self.snip)
        return
    def romtool(self):
        if not self.romframe:
            self.romframe = RomFrame()
        self.romframe.Show()
        wx.CallAfter(self.romframe.RomSetup, self.RomToolDone, self.ser, self.amiga, self.execlib, self.snip)
        return
    def UglyExit(self):
        wx.Exit()
        return
def main():
    app = AmigaXfer()
    app.SetExitOnFrameDelete(False)
    app.MainLoop()
    return
if __name__ == "__main__":
    main()
