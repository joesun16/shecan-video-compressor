; SheCan 视频压缩工具 - Inno Setup 安装脚本
; 在 Windows 上使用 Inno Setup 编译此脚本生成安装包
; 下载 Inno Setup: https://jrsoftware.org/isinfo.php

[Setup]
AppName=SheCan视频压缩工具
AppVersion=2.1
AppPublisher=SheCan
DefaultDirName={autopf}\SheCan视频压缩工具
DefaultGroupName=SheCan视频压缩工具
OutputDir=installer_output
OutputBaseFilename=SheCan视频压缩工具_Setup
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加选项:"

[Files]
; 复制 dist\SheCan视频压缩工具 目录下的所有文件
Source: "dist\SheCan视频压缩工具\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\SheCan视频压缩工具"; Filename: "{app}\SheCan视频压缩工具.exe"
Name: "{group}\卸载"; Filename: "{uninstallexe}"
Name: "{autodesktop}\SheCan视频压缩工具"; Filename: "{app}\SheCan视频压缩工具.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SheCan视频压缩工具.exe"; Description: "运行 SheCan视频压缩工具"; Flags: nowait postinstall skipifsilent
