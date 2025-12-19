# SheCan 视频批量压缩工具 V2.1

跨平台视频批量压缩工具，支持 macOS 和 Windows。

## 功能特点

- 批量压缩视频文件，支持拖放操作
- 多种编码模式：CPU / GPU 硬件加速
- 可调节质量、速度、分辨率
- 实时显示压缩进度和压缩比
- 限制 CPU 使用，避免过热

## 支持的编码器

### macOS
- CPU H.264 (兼容性最好)
- CPU H.265 (体积更小)
- Apple GPU H.264 (推荐，使用 VideoToolbox)
- Apple GPU H.265

### Windows
- CPU H.264 / H.265
- NVIDIA GPU (N卡加速)
- AMD GPU (A卡加速)
- Intel GPU (核显加速)

---

## macOS 安装

### 方式一：使用 DMG 安装包（推荐）
1. 双击 `SheCan视频压缩工具_macOS.dmg`
2. 将应用拖到「应用程序」文件夹
3. 从启动台打开应用

### 方式二：从源码运行
```bash
# 安装 FFmpeg
brew install ffmpeg

# 安装依赖
pip3 install PyQt6

# 运行
python3 video_compressor.py
```

---

## Windows 安装

### 方式一：使用打包好的程序
1. 解压 `SheCan视频压缩工具_Windows.zip`
2. 运行 `SheCan视频压缩工具.exe`
3. 确保已安装 FFmpeg

### 方式二：自行打包
1. 安装 Python 3.8+ 和 FFmpeg
2. 运行 `python build_windows_package.py`
3. 打包结果在 `dist\SheCan视频压缩工具\`

### 方式三：制作安装包
1. 先完成方式二的打包
2. 下载安装 [Inno Setup](https://jrsoftware.org/isinfo.php)
3. 用 Inno Setup 打开 `installer.iss`
4. 点击编译，生成 `SheCan视频压缩工具_Setup.exe`

### FFmpeg 安装（Windows）
1. 下载: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. 解压到 `C:\ffmpeg`
3. 添加 `C:\ffmpeg\bin` 到系统环境变量 PATH

---

## 使用说明

1. 选择编码模式（推荐使用 GPU 加速）
2. 设置质量、速度、分辨率
3. 可选：设置输出目录（默认保存到原文件目录）
4. 拖放视频文件或点击添加
5. 点击「开始压缩」

## 支持的视频格式

MP4, MKV, AVI, MOV, WMV, FLV, WebM, M4V, MPG, MPEG, TS

## 注意事项

- GPU 编码速度快但文件可能稍大
- CPU 编码压缩率高但速度慢
- 程序自动限制 CPU 线程数，避免过热
