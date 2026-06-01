# Create "Switchboard" shortcuts (Desktop + Start Menu) that launch the cockpit
# windowlessly via Switchboard.vbs, with the custom icon. Re-run after moving.
#
# Each shortcut is also stamped with the AppUserModelID that app.py declares
# (gielinor.cockpit.switchboard) so the running cockpit window coalesces with the
# pinned shortcut into ONE taskbar button showing the SB icon -- without a matching
# AUMID the running window splits off under pythonw's identity (python icon). (S140)
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$ws = New-Object -ComObject WScript.Shell
$icon = Join-Path $here "icon.ico"
$vbs  = Join-Path $here "Switchboard.vbs"
$AUMID = "gielinor.cockpit.switchboard"

# Shell Property Store interop -- sets System.AppUserModel.ID on a .lnk. WScript's
# shortcut object can't write this property, so we go through IPropertyStore.
if (-not ("CockpitLnk" -as [type])) {
  Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class CockpitLnk {
  [DllImport("shell32.dll")]
  static extern int SHGetPropertyStoreFromParsingName(
    [MarshalAs(UnmanagedType.LPWStr)] string pszPath, IntPtr pbc, int flags,
    ref Guid riid, out IPropertyStore ppv);

  [ComImport, Guid("886d8eeb-8cf2-4446-8d02-cdba1dbdcf99"),
   InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  interface IPropertyStore {
    int GetCount(out uint c);
    int GetAt(uint i, out PROPERTYKEY pk);
    int GetValue(ref PROPERTYKEY key, out PROPVARIANT pv);
    int SetValue(ref PROPERTYKEY key, ref PROPVARIANT pv);
    int Commit();
  }
  [StructLayout(LayoutKind.Sequential)]
  struct PROPERTYKEY { public Guid fmtid; public uint pid; }
  [StructLayout(LayoutKind.Sequential)]
  struct PROPVARIANT { public ushort vt; ushort r1, r2, r3; public IntPtr p; IntPtr p2; }

  public static void SetAumid(string lnkPath, string aumid) {
    const int GPS_READWRITE = 2;
    const ushort VT_LPWSTR = 31;
    var iid = typeof(IPropertyStore).GUID;
    IPropertyStore ps;
    int hr = SHGetPropertyStoreFromParsingName(lnkPath, IntPtr.Zero, GPS_READWRITE, ref iid, out ps);
    if (hr != 0) throw new Exception("SHGetPropertyStoreFromParsingName failed: 0x" + hr.ToString("X"));
    // PKEY_AppUserModel_ID = {9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3}, pid 5
    var key = new PROPERTYKEY { fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"), pid = 5 };
    var pv = new PROPVARIANT { vt = VT_LPWSTR, p = Marshal.StringToCoTaskMemUni(aumid) };
    ps.SetValue(ref key, ref pv);
    ps.Commit();
    Marshal.ReleaseComObject(ps);
  }
}
'@
}

function New-SBShortcut($path) {
  $lnk = $ws.CreateShortcut($path)
  $lnk.TargetPath = "wscript.exe"
  $lnk.Arguments = '"' + $vbs + '"'
  $lnk.WorkingDirectory = $here
  if (Test-Path $icon) { $lnk.IconLocation = $icon }
  $lnk.Description = "Switchboard cockpit"
  $lnk.Save()
  [CockpitLnk]::SetAumid($path, $AUMID)
  Write-Output ("shortcut -> " + $path + "  (AUMID " + $AUMID + ")")
}

New-SBShortcut (Join-Path ([Environment]::GetFolderPath("Desktop")) "Switchboard.lnk")
New-SBShortcut (Join-Path ([Environment]::GetFolderPath("Programs")) "Switchboard.lnk")

Write-Output ""
Write-Output "NOTE: an EXISTING pinned taskbar icon is a copy made before this AUMID was set --"
Write-Output "unpin it and re-pin from this shortcut so the pin and the running window coalesce."
