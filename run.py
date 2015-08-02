# Sorry if it looks messy

import wx
import sys
import win32serviceutil
import pywintypes
import subprocess
import _winreg


class WinFrame(wx.Frame):
    def __init__(self, parent, title):
        super(WinFrame, self).__init__(parent, title=title, size=[375, 100],
                                       style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        wxpanel = wx.Panel(self)

        self.telebox = wx.CheckBox(wxpanel, label="Disable Telemetry", pos=(10, 15))
        self.telebox.Set3StateValue(0)

        self.diagbox = wx.CheckBox(wxpanel, label="Clear Diagtrack log", pos=(10, 45))
        self.diagbox.Set3StateValue(0)

        self.servicebox = wx.CheckBox(wxpanel, label="Services", pos=(10, 30))
        self.servicebox.Set3StateValue(0)
        self.servicebox.Bind(wx.EVT_CHECKBOX, self.serviceradcheck)

        self.servicerad = wx.RadioBox(wxpanel, label="Service Method", pos=(135, 10), choices=["Delete", "Disable"])
        self.servicerad.Disable()

        self.okbutton = wx.Button(wxpanel, -1, "Go Private", (275, 25))
        self.Bind(wx.EVT_BUTTON, self.onok, self.okbutton)
        self.Centre()
        self.Show()

    def serviceradcheck(self, event):
        self.servicerad.Enable(self.servicebox.IsChecked())  # If Service box is ticked enable Service radio box

    def onok(self, event):
        if self.telebox.IsChecked():
            self.telekeypath = r'SOFTWARE\Policies\Microsoft\Windows\DataCollection'  # Path to Telemetry key

            self.telekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.telekeypath, 0, _winreg.KEY_ALL_ACCESS)
            _winreg.SetValueEx(self.telekey, "AllowTelemetry", 0, _winreg.REG_SZ, "0")  # Disable Telemetry
            _winreg.CloseKey(self.telekey)
        if self.diagbox.IsChecked():
            try:
                open('C:\ProgramData\Microsoft\Diagnosis\ETLLogs\AutoLogger\AutoLogger-Diagtrack-Listener.etl', 'w').close()  # Clear the AutoLogger file
                subprocess.Popen("echo y|cacls C:\ProgramData\Microsoft\Diagnosis\ETLLogs\AutoLogger\AutoLogger-Diagtrack-Listener.etl /d SYSTEM", shell=True)  # Prevent modification to file
            except IOError:
                pass

        if self.servicerad.Selection == 0 and self.servicebox.IsChecked():
            try:
                win32serviceutil.RemoveService('dmwappushsvc')  # Delete dmwappushsvc
            except pywintypes.error:
                pass

            try:
                win32serviceutil.RemoveService('Diagnostics Tracking Service')  # Delete the DiagnosticsTracking Service
            except pywintypes.error:
                pass
        elif self.servicerad.Selection == 1 and self.servicebox.IsChecked():
            self.diagkeypath = r'SYSTEM\CurrentControlSet\Services\DiagTrack'
            self.dmwakeypath = r'SYSTEM\CurrentControlSet\Services\dmwappushsvc'

            try:
                self.diagkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.diagkeypath, 0, _winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(self.diagkey, "Start", 0, _winreg.REG_DWORD, 0x0000004)
                _winreg.CloseKey(self.diagkey)
            except WindowsError:
                pass

            try:
                self.dmwakey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.dmwakeypath, 0, _winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(self.dmwakey, "Start", 0, _winreg.REG_DWORD, 0x0000004)
                _winreg.CloseKey(self.dmwakey)
            except WindowsError:
                pass

            try:
                win32serviceutil.StopService('Diagnostics Tracking Service')  # Disable Diagnostics Tracking Service
            except pywintypes.error:
                pass

            try:
                win32serviceutil.StopService('dmwappushsvc')  # Disable dmwappushsvc
            except pywintypes.error:
                pass

            print "Services Disabled"
        sys.exit()


if __name__ == '__main__':
    wxwindow = wx.App(False)
    WinFrame(None, title='Disable Windows 10 Tracking') # Create Window
    wxwindow.MainLoop()
