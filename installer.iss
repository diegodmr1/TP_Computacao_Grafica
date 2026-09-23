[Setup]
AppName=TP_CG
AppVersion=1.0
DefaultDirName={autopf}\TP_CG
DefaultGroupName=TP_CG
OutputDir=installer
OutputBaseFilename=TP_CG_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\TP_CG\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\TP_CG"; Filename: "{app}\TP_CG.exe"
Name: "{autodesktop}\TP_CG"; Filename: "{app}\TP_CG.exe"

[Run]
Filename: "{app}\TP_CG.exe"; Description: "Abrir TP_CG"; Flags: nowait postinstall skipifsilent