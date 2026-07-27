[Setup]
AppName=AUTOMA
AppVersion=1.0.0
DefaultDirName={pf}\AUTOMA
DefaultGroupName=AUTOMA
OutputDir=.\Output
OutputBaseFilename=AUTOMA_Installer
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Frontend Electron app
Source: "..\frontend\dist\win-unpacked\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs
; Backend PyInstaller executable
Source: "..\backend\dist\automa-backend.exe"; DestDir: "{app}\backend"; Flags: ignoreversion
; Pre-create folders
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AUTOMA"; Filename: "{app}\frontend\automa.exe"
Name: "{group}\{cm:UninstallProgram,AUTOMA}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\AUTOMA"; Filename: "{app}\frontend\automa.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\backend\automa-backend.exe"; Description: "Start Backend Engine"; Flags: nowait postinstall runhidden
Filename: "{app}\frontend\automa.exe"; Description: "Launch AUTOMA"; Flags: nowait postinstall
