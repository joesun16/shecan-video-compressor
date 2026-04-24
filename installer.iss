; EllaPuede 视频压缩工具 V3.0 - Inno Setup 安装脚本
; 在 Windows 上使用 Inno Setup 编译此脚本生成安装包
; 下载 Inno Setup: https://jrsoftware.org/isinfo.php

[Setup]
AppName=EllaPuede视频压缩工具
AppVersion=3.0
AppPublisher=EllaPuede
DefaultDirName={autopf}\EllaPuede视频压缩工具
DefaultGroupName=EllaPuede视频压缩工具
OutputDir=installer_output
OutputBaseFilename=EllaPuede视频压缩工具_Setup
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional options:"

[Files]
Source: "dist\EllaPuede视频压缩工具\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\EllaPuede视频压缩工具"; Filename: "{app}\EllaPuede视频压缩工具.exe"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"
Name: "{autodesktop}\EllaPuede视频压缩工具"; Filename: "{app}\EllaPuede视频压缩工具.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\EllaPuede视频压缩工具.exe"; Description: "Launch EllaPuede Video Compressor"; Flags: nowait postinstall skipifsilent
