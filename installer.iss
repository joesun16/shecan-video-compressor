; SheCan 视频压缩工具 - Inno Setup 安装脚本

[Setup]
AppName=SheCan视频压缩工具
AppVersion=2.6
AppPublisher=SheCan
DefaultDirName={autopf}\SheCan视频压缩工具
DefaultGroupName=SheCan视频压缩工具
OutputDir=installer_output
OutputBaseFilename=SheCan视频压缩工具_Setup
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional options:"

[Files]
Source: "dist\SheCan视频压缩工具\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\SheCan视频压缩工具"; Filename: "{app}\SheCan视频压缩工具.exe"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"
Name: "{autodesktop}\SheCan视频压缩工具"; Filename: "{app}\SheCan视频压缩工具.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SheCan视频压缩工具.exe"; Description: "Launch SheCan Video Compressor"; Flags: nowait postinstall skipifsilent
