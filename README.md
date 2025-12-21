# SheCan Video Compressor

简单易用的视频批量压缩工具，支持 macOS 和 Windows。  
A simple batch video compression tool for macOS and Windows.

![SheCan Video Compressor](https://img.shields.io/badge/version-2.8-blue) ![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey) ![Language](https://img.shields.io/badge/language-中文%20%7C%20English-green)

## 下载安装 / Installation

### macOS
1. 下载 [macOS 安装包](https://github.com/joesun16/shecan-video-compressor/releases/latest)（.dmg 文件）
2. 双击打开 DMG 文件
3. 将应用图标拖到右侧的 Applications 文件夹
4. 从「启动台」或「应用程序」中打开应用，即可使用

### Windows
1. 下载 [Windows 安装包](https://github.com/joesun16/shecan-video-compressor/releases/latest)（.exe 文件）
2. 双击运行安装程序
3. 安装完成后即可使用

> 💡 FFmpeg 已内置，无需额外下载，安装即用！

---

## 功能特点 / Features

- 批量压缩视频，支持拖放
- 多种编码模式（CPU / GPU 硬件加速）
- 可调节质量、速度、分辨率
- 实时显示压缩进度和压缩比
- 自动限制 CPU 使用，避免过热
- 中英文双语界面，跟随系统语言

## 支持的编码器 / Supported Encoders

| 平台 | 编码器 |
|------|--------|
| macOS | Apple GPU H.264/H.265 (VideoToolbox)、CPU H.264/H.265 |
| Windows | NVIDIA GPU、AMD GPU、Intel 核显、CPU H.264/H.265 |

## 支持的视频格式 / Supported Formats

MP4, MKV, AVI, MOV, WMV, FLV, WebM, M4V, MPG, MPEG, TS

## 使用方法 / How to Use

1. 选择编码模式（推荐 GPU 加速）
2. 设置质量、速度、分辨率
3. 拖放视频文件或点击添加
4. 点击「开始压缩」

## 许可证 / License

MIT License
