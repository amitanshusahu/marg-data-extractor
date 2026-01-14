; -- NexInsightsInstaller.iss --

[Setup]
AppName=NexInsights
AppVersion=2.0.0
AppPublisher=Nexusinfotech
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
VersionInfoCompany=Nexusinfotech
VersionInfoProductName=NexInsights
VersionInfoVersion=1.0.0.0

[Files]
Source: "C:\Users\Amitanshu Sahu\Desktop\Code\marg-data-extractor\dist\NexInsights.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Amitanshu Sahu\Desktop\Code\marg-data-extractor\dist\SumatraPDF-3.5.2-64.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\NexInsights"; Filename: "{app}\NexInsights.exe"
Name: "{group}\Uninstall NexInsights"; Filename: "{uninstallexe}"
Name: "{userdesktop}\NexInsights"; Filename: "{app}\NexInsights.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"
Name: "autorun"; Description: "Start NexInsights on login"; GroupDescription: "Startup options:"

[Run]
Filename: "{app}\NexInsights.exe"; Parameters: "--autorun"; Description: "Launch after install"; Flags: nowait postinstall skipifsilent
