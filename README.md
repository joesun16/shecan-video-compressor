# EllaPuede Video Compressor

简单易用的视频批量压缩工具，支持 macOS 和 Windows。
A simple batch video compression tool for macOS and Windows.

![Version](https://img.shields.io/badge/version-3.1-blue) ![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey) ![Language](https://img.shields.io/badge/language-中文%20%7C%20English-green) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

> 前身为 SheCan Video Compressor，V3.0 起更名为 EllaPuede。

## 下载安装 / Installation

### macOS
1. 从 [Releases](../../releases/latest) 下载 `EllaPuede视频压缩工具_macOS.dmg`
2. 双击打开 DMG
3. 将应用图标拖到右侧的 Applications 文件夹
4. 从启动台或应用程序中打开

### Windows
1. 从 [Releases](../../releases/latest) 下载 `EllaPuede视频压缩工具_Setup.exe`
2. 双击运行安装程序
3. 安装完成即可使用

> 💡 FFmpeg 已内置，无需额外下载或配置 PATH，安装即用。

---

## 功能特点 / Features

- 批量压缩视频，支持拖放
- **并行压缩**：可同时处理多个文件（GPU 建议 2-4，CPU 建议 1-2）
- 多种编码模式：CPU H.264/H.265、Apple GPU、NVIDIA、AMD、Intel Quick Sync
- 四档质量：高质量 / 平衡 / 小体积 / **极致压缩**
- 五档分辨率：保持原始 / 1080p / 720p / 480p / **360p**
- **智能音频处理**：输入已是低码率 AAC 时自动 copy，避免无意义重编码
- **动态码率**：GPU 编码器根据目标分辨率自动计算最优码率
- 输出体积大于原始时自动删除
- 实时显示压缩进度和压缩比
- **内置参数指南**：5 个常见场景的推荐参数组合
- **即时语言切换**：中英双语，无需重启
- 右键菜单 + Delete 键快速删除文件

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

点击「💡 参数指南」按钮查看各场景的推荐配置。

---

## 从源码运行 / Run from Source

```bash
# macOS
brew install ffmpeg
pip3 install PyQt6
python3 video_compressor.py

# Windows
pip install PyQt6
python video_compressor.py
# 需要先安装 FFmpeg 并加入系统 PATH
```

## 构建说明 / Build

本项目通过 GitHub Actions 自动构建两个平台的安装包，每次构建会通过 smoke test（启动测试）验证 app 可正常运行。

手动构建：

```bash
# macOS
pyinstaller --name="EllaPuede视频压缩工具" --windowed --onedir --icon=icon.icns \
  --osx-bundle-identifier=com.ellapuede.videocompressor video_compressor.py

# Windows
pyinstaller --name="EllaPuede视频压缩工具" --windowed --onedir --icon=icon.ico \
  --add-data "ffmpeg;ffmpeg" video_compressor.py
```

## 更新日志 / Changelog

### V3.1
- 修复打包后 `ImportError`（延迟 import 上提到模块顶层）
- CI 增加 smoke test，验证打出的 app 能启动
- 两个平台统一使用 PyInstaller

### V3.0
- 品牌更名：SheCan → EllaPuede
- 并行压缩、极致压缩档位、360p 分辨率
- 智能音频、动态码率
- 内置参数指南
- 即时语言切换
- 右键菜单 + Delete 键
- 修复统计弹窗数据不真实的问题
- 修复压缩中途停止时残留损坏文件的问题

## 许可证 / License

MIT License
