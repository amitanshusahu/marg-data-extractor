; -- NexInsightsInstaller.iss --

[Setup]
AppName=NexInsights
AppVersion=1.0.0
AppPublisher=NexSoft Solutions
AppPublisherURL=https://nexusinfotech.co
AppSupportURL=https://nexusinfotech.co
AppUpdatesURL=https://nexusinfotech.co
DefaultDirName={autopf}\NexInsights
DefaultGroupName=NexInsights
UninstallDisplayIcon={app}\NexInsights.exe
OutputDir=dist
OutputBaseFilename=NexInsightsSetup
Compression=lzma
SolidCompression=yes
DisableWelcomePage=no
WizardStyle=modern
WizardImageFile=installer-assets\wizard-image.bmp
WizardSmallImageFile=installer-assets\wizard-small.bmp
SetupIconFile=installer-assets\setup-icon.ico
LicenseFile=installer-assets\EULA.txt
VersionInfoDescription=NexInsights Data Monitor
VersionInfoCompany=NexSoft Solutions
VersionInfoProductName=NexInsights
VersionInfoVersion=1.0.0.0

[Files]
Source: "C:\Users\USER\Desktop\Code\marg-data-extractor\dist\NexInsights.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\USER\Desktop\Code\marg-data-extractor\dist\SumatraPDF-3.5.2-64.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\USER\Desktop\Code\marg-data-extractor\dist\Setup_BullzipPDFPrinter_14_5_0_2974.exe"; DestDir: "{tmp}"; Flags: ignoreversion

[Icons]
Name: "{group}\NexInsights"; Filename: "{app}\NexInsights.exe"
Name: "{group}\Uninstall NexInsights"; Filename: "{uninstallexe}"
Name: "{userdesktop}\NexInsights"; Filename: "{app}\NexInsights.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"
Name: "autorun"; Description: "Start NexInsights on login"; GroupDescription: "Startup options:"

[Run]
; Conditionally run Bullzip installer only if it's not already installed
Filename: "{tmp}\Setup_BullzipPDFPrinter_14_5_0_2974.exe"; \
    Description: "Install Bullzip PDF Printer"; \
    StatusMsg: "Launching Bullzip PDF Printer installer..."; \
    Flags: waituntilterminated; \
    Check: Not IsBullzipInstalled

Filename: "{app}\NexInsights.exe"; Parameters: "--autorun"; Description: "Launch after install"; Flags: nowait postinstall skipifsilent

[Code]
function IsBullzipInstalled: Boolean;
begin
  // Check if Bullzip PDF Printer uninstall key exists
  // This key name can vary depending on version and architecture
  // The below example is known for Bullzip PDF Printer v14+
  Result := RegKeyExists(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\Bullzip PDF Printer_is1');
end;
