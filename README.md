# EllaPuede Video Compressor

简单易用的视频批量压缩工具，支持 macOS 和 Windows。
A simple batch video compression tool for macOS and Windows.

![Version](https://img.shields.io/badge/version-3.0-blue) ![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey) ![Language](https://img.shields.io/badge/language-中文%20%7C%20English-green)

## 下载安装 / Installation

### macOS
1. 下载 [macOS 安装包](../../releases/latest)（.dmg 文件）
2. 双击打开 DMG 文件
3. 将应用图标拖到右侧的 Applications 文件夹
4. 从「启动台」或「应用程序」中打开应用

### Windows
1. 下载 [Windows 安装包](../../releases/latest)（.exe 文件）
2. 双击运行安装程序
3. 安装完成后即可使用

> 💡 FFmpeg 已内置，无需额外下载，安装即用！

---

## 功能特点 / Features

- 批量压缩视频，支持拖放
- 并行压缩：可同时处理多个文件（GPU 建议 2-4，CPU 建议 1-2）
- 多种编码模式（CPU / GPU 硬件加速）
- 四档质量：高质量 / 平衡 / 小体积 / 极致压缩
- 五档分辨率：原始 / 1080p / 720p / 480p / 360p
- 智能音频处理：已是低码率 AAC 时自动跳过重编码
- 动态码率：GPU 编码器根据目标分辨率自动计算最优码率
- 输出体积大于原始时自动删除，避免浪费空间
- 实时显示压缩进度和压缩比
- 内置参数指南，帮助选择最佳压缩组合
- 中英文双语界面，跟随系统语言

## 支持的编码器 / Supported Encoders

| 平台 | 编码器 |
|------|--------|
| macOS | Apple GPU H.264/H.265 (VideoToolbox)、CPU H.264/H.265 |
| Windows | NVIDIA GPU、AMD GPU、Intel 核显、CPU H.264/H.265 |

## 支持的视频格式 / Supported Formats

MP4, MKV, AVI, MOV, WMV, FLV, WebM, M4V, MPG, MPEG, TS, 3GP, VOB

## 使用方法 / How to Use

1. 选择编码模式（推荐 GPU 加速）
2. 设置质量、速度、分辨率、并行数
3. 拖放视频文件或点击添加
4. 点击「开始压缩」

> 💡 点击「参数指南」按钮查看常见场景的推荐参数组合

## 从源码运行 / Run from Source

```bash
# macOS
brew install ffmpeg
pip3 install PyQt6
python3 video_compressor.py

# Windows
pip install PyQt6
python video_compressor.py
# 需要先安装 FFmpeg 并添加到 PATH
```

## 许可证 / License

MIT License
