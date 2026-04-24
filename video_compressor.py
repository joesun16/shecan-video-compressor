#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EllaPuede 视频批量压缩工具 V3.0
跨平台支持 (macOS / Windows)
FFmpeg 内置，双语界面，并行压缩
"""

import sys
import os
import subprocess
import re
import platform
import multiprocessing
import json
import threading
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QProgressBar, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QLineEdit,
    QAbstractItemView, QDialog, QMessageBox, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QLocale, QTimer
from PyQt6.QtGui import QColor, QAction

# ============ 常量 ============
VERSION = '3.0'
APP_NAME = 'EllaPuede'
IS_MAC = platform.system() == 'Darwin'
IS_WIN = platform.system() == 'Windows'
CPU_COUNT = multiprocessing.cpu_count()

VIDEO_EXTENSIONS = {
    '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv',
    '.webm', '.m4v', '.mpg', '.mpeg', '.ts', '.3gp', '.vob'
}

VIDEO_FILTER_STR = ' '.join(f'*{ext}' for ext in sorted(VIDEO_EXTENSIONS))

RESOLUTION_OPTIONS = [
    ('keep_original', None),
    ('1080p', 1080),
    ('720p', 720),
    ('480p', 480),
    ('360p', 360),
]

# ============ 日志 ============
LOG_DIR = None
if IS_WIN:
    _base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    LOG_DIR = os.path.join(_base, APP_NAME, 'VideoCompressor', 'logs')
else:
    LOG_DIR = os.path.expanduser(f'~/Library/Logs/{APP_NAME}/VideoCompressor')

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'app.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============ 语言管理 ============
TEXTS = {
    'zh': {
        'app_title': f'{APP_NAME} 视频压缩工具',
        'batch_compress': '视频批量压缩',
        'encoder_mode': '编码模式',
        'quality': '质量',
        'speed': '速度',
        'resolution': '分辨率',
        'output_dir': '输出目录',
        'output_placeholder': '默认保存到原文件所在目录',
        'select': '选择',
        'clear': '清除',
        'drop_hint': '拖放视频文件到这里，或点击选择',
        'format_hint': '支持 MP4、MKV、AVI、MOV 等格式',
        'add_files': '添加文件',
        'add_folder': '添加文件夹',
        'remove_selected': '移除选中',
        'clear_list': '清空列表',
        'start': '开始压缩',
        'stop': '停止',
        'ready': '就绪',
        'preparing': '准备中...',
        'compressing': '压缩中',
        'waiting': '等待',
        'failed': '失败',
        'cancelled': '已取消',
        'stopping': '正在停止...',
        'stopped': '已停止',
        'col_filename': '文件名',
        'col_duration': '时长',
        'col_size': '大小',
        'col_progress': '进度',
        'col_output': '压缩后',
        'col_status': '状态',
        'high_quality': '高质量',
        'balanced': '平衡',
        'small_size': '小体积',
        'extreme': '极致压缩',
        'fast': '快速',
        'high_compress': '高压缩',
        'keep_original': '保持原始',
        'compress_done': '压缩完成',
        'compress_stopped': '压缩已停止',
        'files_processed': '成功处理:',
        'files_failed': '失败:',
        'original_size': '原始大小:',
        'compressed_size': '压缩后:',
        'space_saved': '节省空间:',
        'size_increased': '体积增加:',
        'ok': '确定',
        'hint': '提示',
        'error': '错误',
        'add_files_first': '请先添加视频文件',
        'select_output': '选择输出目录',
        'select_video': '选择视频文件',
        'select_folder': '选择文件夹',
        'video_files': '视频文件',
        'all_files': '所有文件',
        'cannot_create_dir': '无法创建输出目录',
        'language': '语言',
        'chinese': '中文',
        'english': 'English',
        'restart_hint': '语言切换将在重启后生效',
        'ffmpeg_ready': '● FFmpeg 就绪',
        'ffmpeg_not_found': '● FFmpeg 未找到',
        'ffmpeg_error_mac': '请安装 FFmpeg:\nbrew install ffmpeg\n或从 https://ffmpeg.org 下载',
        'ffmpeg_error_win': '请安装 FFmpeg:\n从 https://ffmpeg.org 下载并添加到系统 PATH',
        'missing_dep': '缺少依赖',
        'parallel': '并行数',
        'parallel_tip': '同时压缩的文件数量（GPU编码建议2-4，CPU编码建议1-2）',
        'file_count': '共 {count} 个文件，{size}',
        'processing': '处理中 {current}/{total}',
        'done': '完成 {completed}/{total}',
        'size_increased_auto': '压缩后体积增大，已自动删除输出文件',
        # 编码器名称 — 使用内部 key，不再用翻译文本做 dict key
        'enc_cpu_h264': 'CPU H.264 (兼容性最好)',
        'enc_cpu_h265': 'CPU H.265 (体积更小)',
        'enc_apple_h264': 'Apple GPU H.264 (推荐)',
        'enc_apple_h265': 'Apple GPU H.265',
        'enc_nvidia': 'NVIDIA GPU (N卡加速)',
        'enc_amd': 'AMD GPU (A卡加速)',
        'enc_intel': 'Intel GPU (核显加速)',
        # 编码器提示
        'info_apple': '使用 Apple 硬件加速，速度快',
        'info_nvidia': '使用 NVIDIA GPU 加速',
        'info_amd': '使用 AMD GPU 加速',
        'info_intel': '使用 Intel 核显加速',
        'info_h265': 'H.265 编码，体积更小但兼容性稍差',
        'info_cpu': 'CPU 编码，兼容性最好',
        'speed_not_available': '当前编码器不支持速度调节',
        'guide_toggle': '💡 参数指南',
        'guide_content': (
            '<b>🎯 常见场景推荐组合：</b><br><br>'
            '<b>📱 发社交媒体（微信/抖音）</b><br>'
            '编码：Apple GPU H.264 ｜ 质量：小体积 ｜ 分辨率：720p<br>'
            '→ 体积小，上传快，画质够用<br><br>'
            '<b>💾 存档备份（节省硬盘空间）</b><br>'
            '编码：CPU H.265 ｜ 质量：平衡 ｜ 速度：高压缩 ｜ 分辨率：保持原始<br>'
            '→ 压缩率最高，速度较慢，适合挂机跑<br><br>'
            '<b>🎬 剪辑素材（保留画质）</b><br>'
            '编码：Apple GPU H.264 ｜ 质量：高质量 ｜ 分辨率：保持原始<br>'
            '→ 速度快，画质损失极小<br><br>'
            '<b>📧 邮件/网盘传输（极致压缩）</b><br>'
            '编码：CPU H.265 ｜ 质量：极致压缩 ｜ 速度：高压缩 ｜ 分辨率：480p<br>'
            '→ 体积最小，适合大批量传输<br><br>'
            '<b>⚡ 快速批量处理</b><br>'
            '编码：Apple GPU H.264 ｜ 质量：平衡 ｜ 并行数：3-4<br>'
            '→ GPU 加速 + 多文件并行，速度最快'
        ),
    },
    'en': {
        'app_title': f'{APP_NAME} Video Compressor',
        'batch_compress': 'Batch Video Compression',
        'encoder_mode': 'Encoder',
        'quality': 'Quality',
        'speed': 'Speed',
        'resolution': 'Resolution',
        'output_dir': 'Output',
        'output_placeholder': 'Default: same as source file',
        'select': 'Browse',
        'clear': 'Clear',
        'drop_hint': 'Drop video files here, or click to select',
        'format_hint': 'Supports MP4, MKV, AVI, MOV, etc.',
        'add_files': 'Add Files',
        'add_folder': 'Add Folder',
        'remove_selected': 'Remove',
        'clear_list': 'Clear All',
        'start': 'Start',
        'stop': 'Stop',
        'ready': 'Ready',
        'preparing': 'Preparing...',
        'compressing': 'Compressing',
        'waiting': 'Waiting',
        'failed': 'Failed',
        'cancelled': 'Cancelled',
        'stopping': 'Stopping...',
        'stopped': 'Stopped',
        'col_filename': 'Filename',
        'col_duration': 'Duration',
        'col_size': 'Size',
        'col_progress': 'Progress',
        'col_output': 'Output',
        'col_status': 'Status',
        'high_quality': 'High Quality',
        'balanced': 'Balanced',
        'small_size': 'Small Size',
        'extreme': 'Extreme',
        'fast': 'Fast',
        'high_compress': 'High Compress',
        'keep_original': 'Original',
        'compress_done': 'Compression Complete',
        'compress_stopped': 'Compression Stopped',
        'files_processed': 'Processed:',
        'files_failed': 'Failed:',
        'original_size': 'Original:',
        'compressed_size': 'Compressed:',
        'space_saved': 'Saved:',
        'size_increased': 'Increased:',
        'ok': 'OK',
        'hint': 'Info',
        'error': 'Error',
        'add_files_first': 'Please add video files first',
        'select_output': 'Select Output Directory',
        'select_video': 'Select Video Files',
        'select_folder': 'Select Folder',
        'video_files': 'Video Files',
        'all_files': 'All Files',
        'cannot_create_dir': 'Cannot create output directory',
        'language': 'Language',
        'chinese': '中文',
        'english': 'English',
        'restart_hint': 'Language change will take effect after restart',
        'ffmpeg_ready': '● FFmpeg Ready',
        'ffmpeg_not_found': '● FFmpeg Not Found',
        'ffmpeg_error_mac': 'Please install FFmpeg:\nbrew install ffmpeg\nor download from https://ffmpeg.org',
        'ffmpeg_error_win': 'Please install FFmpeg:\nDownload from https://ffmpeg.org and add to PATH',
        'missing_dep': 'Missing Dependency',
        'parallel': 'Parallel',
        'parallel_tip': 'Number of simultaneous compressions (GPU: 2-4, CPU: 1-2)',
        'file_count': '{count} files, {size}',
        'processing': 'Processing {current}/{total}',
        'done': 'Done {completed}/{total}',
        'size_increased_auto': 'Output larger than input, auto-deleted',
        # Encoder names
        'enc_cpu_h264': 'CPU H.264 (Best Compatibility)',
        'enc_cpu_h265': 'CPU H.265 (Smaller Size)',
        'enc_apple_h264': 'Apple GPU H.264 (Recommended)',
        'enc_apple_h265': 'Apple GPU H.265',
        'enc_nvidia': 'NVIDIA GPU (Hardware Accel)',
        'enc_amd': 'AMD GPU (Hardware Accel)',
        'enc_intel': 'Intel GPU (Quick Sync)',
        # Encoder info
        'info_apple': 'Apple hardware acceleration, fast',
        'info_nvidia': 'NVIDIA GPU acceleration',
        'info_amd': 'AMD GPU acceleration',
        'info_intel': 'Intel Quick Sync acceleration',
        'info_h265': 'H.265 codec, smaller but less compatible',
        'info_cpu': 'CPU encoding, best compatibility',
        'speed_not_available': 'Speed control not available for this encoder',
        'guide_toggle': '💡 Guide',
        'guide_content': (
            '<b>🎯 Recommended Presets:</b><br><br>'
            '<b>📱 Social Media (small & fast)</b><br>'
            'Encoder: Apple GPU H.264 ｜ Quality: Small Size ｜ Resolution: 720p<br>'
            '→ Small file, fast upload, good enough quality<br><br>'
            '<b>💾 Archive (save disk space)</b><br>'
            'Encoder: CPU H.265 ｜ Quality: Balanced ｜ Speed: High Compress ｜ Resolution: Original<br>'
            '→ Best compression ratio, slower, good for batch overnight<br><br>'
            '<b>🎬 Editing Source (preserve quality)</b><br>'
            'Encoder: Apple GPU H.264 ｜ Quality: High Quality ｜ Resolution: Original<br>'
            '→ Fast, minimal quality loss<br><br>'
            '<b>📧 Email/Cloud Transfer (extreme)</b><br>'
            'Encoder: CPU H.265 ｜ Quality: Extreme ｜ Speed: High Compress ｜ Resolution: 480p<br>'
            '→ Smallest file size, good for bulk transfer<br><br>'
            '<b>⚡ Fast Batch Processing</b><br>'
            'Encoder: Apple GPU H.264 ｜ Quality: Balanced ｜ Parallel: 3-4<br>'
            '→ GPU acceleration + parallel, fastest throughput'
        ),
    }
}


class LanguageManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.current = 'zh'
        self._load_saved_language()

    def _get_config_path(self):
        if IS_WIN:
            base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            return os.path.join(base, APP_NAME, 'VideoCompressor', 'config.json')
        return os.path.expanduser(f'~/Library/Application Support/{APP_NAME}/VideoCompressor/config.json')

    def _load_saved_language(self):
        config_path = self._get_config_path()
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('language') in ('zh', 'en'):
                        self.current = config['language']
                        return
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load language config: {e}")
        # 尝试迁移旧配置
        self._migrate_old_config(config_path)
        if self.current not in ('zh', 'en'):
            self._detect_system_language()

    def _migrate_old_config(self, new_path):
        """从旧 SheCan 路径迁移配置"""
        if IS_WIN:
            base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            old_path = os.path.join(base, 'SheCan', 'VideoCompressor', 'config.json')
        else:
            old_path = os.path.expanduser('~/Library/Application Support/SheCan/VideoCompressor/config.json')
        try:
            if os.path.exists(old_path) and not os.path.exists(new_path):
                with open(old_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                with open(new_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f)
                if config.get('language') in ('zh', 'en'):
                    self.current = config['language']
                logger.info(f"Migrated config from {old_path}")
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Config migration failed: {e}")

    def _detect_system_language(self):
        try:
            if IS_MAC:
                result = subprocess.run(
                    ['defaults', 'read', '-g', 'AppleLanguages'],
                    capture_output=True, text=True, timeout=2
                )
                if 'zh' in result.stdout.lower():
                    self.current = 'zh'
                    return
        except (subprocess.TimeoutExpired, OSError):
            pass
        try:
            locale_name = QLocale.system().name()
            if locale_name.startswith('zh'):
                self.current = 'zh'
                return
        except Exception:
            pass
        self.current = 'en'

    def save_language(self, lang):
        if lang not in ('zh', 'en'):
            return
        self.current = lang
        config_path = self._get_config_path()
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            config['language'] = lang
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to save language: {e}")

    def get(self):
        return self.current


LM = LanguageManager()


def get_lang():
    return LM.get()


def tr(key):
    """翻译函数 — 从预构建的字典中查找"""
    return TEXTS.get(get_lang(), TEXTS['zh']).get(key, key)


# ============ FFmpeg 路径 ============
def get_ffmpeg_path():
    """获取 FFmpeg 路径 - 优先使用内置版本"""
    # macOS: PyInstaller .app bundle 或 py2app
    if IS_MAC:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(sys.argv[0] if sys.argv[0] else __file__)
        # PyInstaller .app: executable is in .app/Contents/MacOS/
        if '.app/Contents/' in exe_path:
            parts = exe_path.split('.app/Contents/')
            if len(parts) >= 2:
                contents_dir = parts[0] + '.app/Contents'
                bundled = os.path.join(contents_dir, 'Resources', 'ffmpeg', 'ffmpeg')
                if os.path.exists(bundled):
                    return bundled
        # PyInstaller --onedir (not .app): check _MEIPASS
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundled = os.path.join(sys._MEIPASS, 'ffmpeg', 'ffmpeg')
            if os.path.exists(bundled):
                return bundled
        # Also check next to the executable
        if getattr(sys, 'frozen', False):
            bundled = os.path.join(os.path.dirname(sys.executable), 'ffmpeg', 'ffmpeg')
            if os.path.exists(bundled):
                return bundled

    # Windows: PyInstaller 打包
    if IS_WIN and getattr(sys, 'frozen', False):
        # _MEIPASS (--add-data puts files here)
        if hasattr(sys, '_MEIPASS'):
            bundled = os.path.join(sys._MEIPASS, 'ffmpeg', 'ffmpeg.exe')
            if os.path.exists(bundled):
                return bundled
        # Also check next to the exe (--onedir mode)
        bundled = os.path.join(os.path.dirname(sys.executable), 'ffmpeg', 'ffmpeg.exe')
        if os.path.exists(bundled):
            return bundled

    # 开发模式：查找系统 FFmpeg
    if IS_WIN:
        return 'ffmpeg'
    for p in ['/opt/homebrew/bin/ffmpeg', '/usr/local/bin/ffmpeg',
              os.path.expanduser('~/bin/ffmpeg')]:
        if os.path.exists(p):
            return p
    return 'ffmpeg'


def get_ffprobe_path():
    """获取 FFprobe 路径"""
    ffmpeg = get_ffmpeg_path()
    # 只替换最后一个 ffmpeg（文件名），不替换目录名中的 ffmpeg
    dir_name = os.path.dirname(ffmpeg)
    if IS_WIN:
        return os.path.join(dir_name, 'ffprobe.exe')
    return os.path.join(dir_name, 'ffprobe')


def _subprocess_kwargs(capture=True, text=True, timeout=None):
    """统一的 subprocess 参数"""
    kwargs = {}
    if capture:
        kwargs['capture_output'] = True
    if text:
        kwargs['text'] = True
    if timeout:
        kwargs['timeout'] = timeout
    if IS_WIN:
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
    return kwargs


# ============ 编码器配置（与翻译解耦）============
# 内部使用固定 key，显示名称通过 tr() 获取

ENCODER_CONFIGS = {
    'cpu_h264': {
        'encoder': 'libx264',
        'quality_param': '-crf',
        'quality_map': {'high': '18', 'balanced': '23', 'small': '30', 'extreme': '35'},
        'has_preset': True,
        'preset_map': {'fast': 'veryfast', 'balanced': 'medium', 'high_compress': 'slow'},
        'is_gpu': False,
        'info_key': 'info_cpu',
    },
    'cpu_h265': {
        'encoder': 'libx265',
        'quality_param': '-crf',
        'quality_map': {'high': '22', 'balanced': '28', 'small': '35', 'extreme': '40'},
        'has_preset': True,
        'preset_map': {'fast': 'veryfast', 'balanced': 'medium', 'high_compress': 'slow'},
        'is_gpu': False,
        'info_key': 'info_h265',
    },
}

if IS_MAC:
    ENCODER_CONFIGS['apple_h264'] = {
        'encoder': 'h264_videotoolbox',
        'quality_param': '-b:v',
        'quality_map': 'dynamic',  # 动态码率
        'has_preset': False,
        'preset_map': {},
        'is_gpu': True,
        'info_key': 'info_apple',
        'extra_params': ['-realtime', '0', '-allow_sw', '1'],
    }
    ENCODER_CONFIGS['apple_h265'] = {
        'encoder': 'hevc_videotoolbox',
        'quality_param': '-b:v',
        'quality_map': 'dynamic',
        'has_preset': False,
        'preset_map': {},
        'is_gpu': True,
        'info_key': 'info_apple',
        'extra_params': ['-realtime', '0', '-allow_sw', '1'],
    }

if IS_WIN:
    ENCODER_CONFIGS['nvidia'] = {
        'encoder': 'h264_nvenc',
        'quality_param': '-cq',
        'quality_map': {'high': '19', 'balanced': '23', 'small': '28', 'extreme': '32'},
        'has_preset': True,
        'preset_map': {'fast': 'fast', 'balanced': 'medium', 'high_compress': 'slow'},
        'is_gpu': True,
        'info_key': 'info_nvidia',
        'extra_params': ['-rc', 'vbr_hq'],
    }
    ENCODER_CONFIGS['amd'] = {
        'encoder': 'h264_amf',
        'quality_param': '-qp_i',
        'quality_map': {'high': '18', 'balanced': '23', 'small': '28', 'extreme': '32'},
        'has_preset': False,
        'preset_map': {},
        'is_gpu': True,
        'info_key': 'info_amd',
    }
    ENCODER_CONFIGS['intel'] = {
        'encoder': 'h264_qsv',
        'quality_param': '-global_quality',
        'quality_map': {'high': '20', 'balanced': '25', 'small': '30', 'extreme': '35'},
        'has_preset': True,
        'preset_map': {'fast': 'veryfast', 'balanced': 'medium', 'high_compress': 'slow'},
        'is_gpu': True,
        'info_key': 'info_intel',
    }

# 质量/速度选项的内部 key 映射
QUALITY_KEYS = ['high', 'balanced', 'small', 'extreme']
QUALITY_TR_KEYS = ['high_quality', 'balanced', 'small_size', 'extreme']
SPEED_KEYS = ['fast', 'balanced', 'high_compress']
SPEED_TR_KEYS = ['fast', 'balanced', 'high_compress']


def get_quality_internal_key(display_text):
    """将显示文本转换为内部 key"""
    for i, tr_key in enumerate(QUALITY_TR_KEYS):
        if display_text == tr(tr_key):
            return QUALITY_KEYS[i]
    return 'balanced'


def get_speed_internal_key(display_text):
    """将显示文本转换为内部 key"""
    for i, tr_key in enumerate(SPEED_TR_KEYS):
        if display_text == tr(tr_key):
            return SPEED_KEYS[i]
    return 'balanced'


def compute_dynamic_bitrate(quality_key, target_height, is_h265=False):
    """根据目标分辨率动态计算码率（用于 VideoToolbox 等硬件编码器）"""
    # 基准码率表 (H.264, 单位 Mbps)
    bitrate_table = {
        #           high   balanced  small  extreme
        2160: [20.0, 12.0, 6.0, 3.0],
        1080: [8.0, 4.0, 2.0, 1.0],
        720:  [5.0, 2.5, 1.2, 0.6],
        480:  [3.0, 1.5, 0.8, 0.4],
        360:  [2.0, 1.0, 0.5, 0.25],
    }
    qi = QUALITY_KEYS.index(quality_key) if quality_key in QUALITY_KEYS else 1
    # 找最近的分辨率档位
    heights = sorted(bitrate_table.keys())
    closest = min(heights, key=lambda h: abs(h - target_height))
    rate = bitrate_table[closest][qi]
    if is_h265:
        rate *= 0.7  # H.265 同质量下码率更低
    return f'{rate}M'


def detect_available_encoders():
    """检测可用的编码器，返回内部 key 列表"""
    available = []
    try:
        ffmpeg = get_ffmpeg_path()
        result = subprocess.run(
            [ffmpeg, '-hide_banner', '-encoders'],
            **_subprocess_kwargs(timeout=10)
        )
        output = result.stdout or ''
        for key, cfg in ENCODER_CONFIGS.items():
            if cfg['encoder'] in output:
                available.append(key)
    except Exception as e:
        logger.error(f"Failed to detect encoders: {e}")
    if not available:
        available = ['cpu_h264']
    return available


def probe_video_info(filepath):
    """获取视频信息：时长、分辨率高度、音频编码、音频码率"""
    info = {'duration': 0, 'height': 0, 'audio_codec': '', 'audio_bitrate': 0}
    try:
        ffprobe = get_ffprobe_path()
        cmd = [
            ffprobe, '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=height',
            '-show_entries', 'format=duration',
            '-of', 'json',
            filepath
        ]
        result = subprocess.run(cmd, **_subprocess_kwargs(timeout=15))
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            fmt = data.get('format', {})
            info['duration'] = float(fmt.get('duration', 0))
            streams = data.get('streams', [])
            if streams:
                info['height'] = int(streams[0].get('height', 0))

        # 获取音频信息
        cmd_audio = [
            ffprobe, '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_name,bit_rate',
            '-of', 'json',
            filepath
        ]
        result_a = subprocess.run(cmd_audio, **_subprocess_kwargs(timeout=15))
        if result_a.returncode == 0 and result_a.stdout:
            data_a = json.loads(result_a.stdout)
            a_streams = data_a.get('streams', [])
            if a_streams:
                info['audio_codec'] = a_streams[0].get('codec_name', '')
                ab = a_streams[0].get('bit_rate', '0')
                info['audio_bitrate'] = int(ab) if ab and ab.isdigit() else 0
    except Exception as e:
        logger.warning(f"Failed to probe {filepath}: {e}")
    return info


# ============ 格式化工具 ============
def fmt_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def fmt_duration(seconds):
    """格式化时长"""
    if seconds <= 0:
        return "-"
    s = int(seconds)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# ============ 结果弹窗 ============
class ResultDialog(QDialog):
    def __init__(self, parent, completed, failed, total, input_size, output_size, was_stopped=False):
        super().__init__(parent)
        title_key = 'compress_stopped' if was_stopped else 'compress_done'
        self.setWindowTitle(tr(title_key))
        self.setFixedSize(340, 260)
        self.setStyleSheet("QDialog { background: white; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        title = QLabel(tr(title_key))
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1d1d1f;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        info_data = [
            (tr('files_processed'), f"{completed}/{total}", "#333"),
        ]
        if failed > 0:
            info_data.append((tr('files_failed'), str(failed), "#ff3b30"))

        if input_size > 0 and completed > 0:
            info_data.append((tr('original_size'), fmt_size(input_size), "#333"))
            info_data.append((tr('compressed_size'), fmt_size(output_size), "#333"))
            saved = input_size - output_size
            ratio = abs(saved) / input_size * 100
            if saved > 0:
                info_data.append((tr('space_saved'), f"-{fmt_size(saved)} ({ratio:.0f}%)", "#34c759"))
            elif saved < 0:
                info_data.append((tr('size_increased'), f"+{fmt_size(abs(saved))} ({ratio:.0f}%)", "#ff9500"))

        for label, value, color in info_data:
            row = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet("font-size: 13px; color: #666;")
            v = QLabel(value)
            v.setStyleSheet(f"font-size: 13px; font-weight: 500; color: {color};")
            row.addWidget(l)
            row.addStretch()
            row.addWidget(v)
            layout.addLayout(row)

        layout.addStretch()

        ok_btn = QPushButton(tr('ok'))
        ok_btn.setFixedHeight(32)
        ok_btn.setStyleSheet("""
            QPushButton { background: #007AFF; border: none; border-radius: 6px; color: white; font-weight: 500; font-size: 13px; }
            QPushButton:hover { background: #0066d6; }
        """)
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)


# ============ 视频信息工作线程（线程池化）============
class VideoInfoPool:
    """使用线程池获取视频信息，避免无限创建 QThread"""

    def __init__(self, callback, max_workers=4):
        self.callback = callback
        self.pool = ThreadPoolExecutor(max_workers=max_workers)
        self._futures = []

    def submit(self, row, filepath):
        future = self.pool.submit(self._get_info, row, filepath)
        self._futures.append(future)

    def _get_info(self, row, filepath):
        try:
            ffprobe = get_ffprobe_path()
            cmd = [
                ffprobe, '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                filepath
            ]
            result = subprocess.run(cmd, **_subprocess_kwargs(timeout=10))
            if result.returncode == 0 and result.stdout.strip():
                dur = float(result.stdout.strip())
                self.callback(row, fmt_duration(dur))
            else:
                self.callback(row, "-")
        except Exception as e:
            logger.warning(f"Failed to get duration for row {row}: {e}")
            self.callback(row, "-")

    def shutdown(self):
        self.pool.shutdown(wait=False)


# ============ 并行压缩工作线程 ============
class CompressionWorker(QThread):
    """并行压缩 worker，使用线程池管理多个 FFmpeg 进程"""
    progress = pyqtSignal(int, int, str)      # (file_index, percent, status)
    file_done = pyqtSignal(int, bool, int)     # (file_index, success, output_size)
    all_done = pyqtSignal(int, int, int, int, int, bool)  # (completed, failed, total, total_in, total_out, was_stopped)

    def __init__(self, files, settings):
        super().__init__()
        self.files = files
        self.settings = settings
        self._lock = threading.Lock()
        self._should_stop = False
        self._processes = {}  # index -> subprocess.Popen
        self._completed = 0
        self._failed = 0
        self._total_in = 0
        self._total_out = 0

    def run(self):
        total = len(self.files)
        max_parallel = self.settings.get('parallel', 2)
        enc_key = self.settings['encoder_key']
        enc_cfg = ENCODER_CONFIGS.get(enc_key, ENCODER_CONFIGS['cpu_h264'])

        # CPU 编码时限制并行数
        if not enc_cfg.get('is_gpu', False):
            max_parallel = min(max_parallel, 2)

        threads_per_job = max(1, CPU_COUNT // max(max_parallel, 1))
        threads_per_job = max(2, min(threads_per_job, CPU_COUNT // 2))

        with ThreadPoolExecutor(max_workers=max_parallel) as pool:
            futures = []
            for i, f in enumerate(self.files):
                with self._lock:
                    if self._should_stop:
                        break
                futures.append(pool.submit(self._compress_one, i, f, enc_cfg, threads_per_job))

            # 等待所有完成
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Compression future error: {e}")

        with self._lock:
            was_stopped = self._should_stop
            self.all_done.emit(
                self._completed, self._failed, total,
                self._total_in, self._total_out, was_stopped
            )

    def _compress_one(self, index, file_info, enc_cfg, threads_per_job):
        """压缩单个文件"""
        with self._lock:
            if self._should_stop:
                self.progress.emit(index, 0, tr('cancelled'))
                return

        in_path = file_info['path']
        in_size = file_info['size']
        quality_key = self.settings['quality_key']
        speed_key = self.settings['speed_key']
        ffmpeg = get_ffmpeg_path()

        self.progress.emit(index, 0, tr('preparing'))

        if not os.path.exists(in_path):
            logger.warning(f"File not found: {in_path}")
            with self._lock:
                self._failed += 1
            self.file_done.emit(index, False, 0)
            return

        out_dir = self.settings.get('output_dir') or os.path.dirname(in_path)
        name = os.path.splitext(file_info['name'])[0]
        # 避免 _compressed_compressed 问题
        if name.endswith('_compressed'):
            name = name[:-len('_compressed')]
        out_path = os.path.join(out_dir, f"{name}_compressed.mp4")

        try:
            os.makedirs(out_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Cannot create output dir: {e}")
            with self._lock:
                self._failed += 1
            self.file_done.emit(index, False, 0)
            return

        # 探测输入视频信息
        info = probe_video_info(in_path)
        duration = info['duration']
        input_height = info['height'] or 1080

        # 确定目标分辨率
        res_setting = self.settings.get('resolution')
        target_height = res_setting if isinstance(res_setting, int) else input_height

        # 构建 FFmpeg 命令
        cmd = [ffmpeg, '-i', in_path]

        # 视频编码器
        cmd.extend(['-c:v', enc_cfg['encoder']])

        # 质量参数
        if enc_cfg['quality_map'] == 'dynamic':
            is_h265 = 'hevc' in enc_cfg['encoder']
            bitrate = compute_dynamic_bitrate(quality_key, target_height, is_h265)
            cmd.extend([enc_cfg['quality_param'], bitrate])
        else:
            q_val = enc_cfg['quality_map'].get(quality_key, '23')
            cmd.extend([enc_cfg['quality_param'], q_val])

        # preset
        if enc_cfg.get('has_preset') and enc_cfg.get('preset_map'):
            preset = enc_cfg['preset_map'].get(speed_key, 'medium')
            cmd.extend(['-preset', preset])

        # 编码器特有参数
        if enc_cfg.get('extra_params'):
            cmd.extend(enc_cfg['extra_params'])

        # 视频滤镜：分辨率 + 像素格式
        vf_parts = []
        if isinstance(res_setting, int):
            vf_parts.append(f'scale=-2:{res_setting}')
        vf_parts.append('format=yuv420p')
        cmd.extend(['-vf', ','.join(vf_parts)])

        # 音频处理：智能决定 copy 还是重编码
        audio_codec = info.get('audio_codec', '')
        audio_bitrate = info.get('audio_bitrate', 0)
        target_audio_bitrate = 48000 if quality_key == 'extreme' else 128000

        if audio_codec == 'aac' and 0 < audio_bitrate <= target_audio_bitrate:
            cmd.extend(['-c:a', 'copy'])
        else:
            cmd.extend(['-c:a', 'aac', '-b:a', f'{target_audio_bitrate // 1000}k'])

        # 流选择 + 通用参数
        # 只有 probe 成功时才用 -map 精确选择流，否则让 FFmpeg 自动选
        if info.get('height') or info.get('audio_codec'):
            cmd.extend(['-map', '0:v:0'])
            if info.get('audio_codec'):
                cmd.extend(['-map', '0:a:0'])
        cmd.extend([
            '-threads', str(threads_per_job),
            '-max_muxing_queue_size', '1024',
            '-movflags', '+faststart',
            '-y', out_path
        ])

        logger.info(f"Compressing [{index}]: {' '.join(cmd)}")

        process = None
        stderr_lines = []
        try:
            kwargs = {'stderr': subprocess.PIPE, 'universal_newlines': True}
            if IS_WIN:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(cmd, **kwargs)
            with self._lock:
                self._processes[index] = process

            for line in process.stderr:
                stderr_lines.append(line.rstrip())
                with self._lock:
                    if self._should_stop:
                        process.terminate()
                        break

                match = re.search(r'time=(\d+):(\d+):(\d+\.?\d*)', line)
                if match and duration > 0:
                    h, m, s = match.groups()
                    cur = int(h) * 3600 + int(m) * 60 + float(s)
                    pct = min(int(cur / duration * 100), 99)
                    self.progress.emit(index, pct, tr('compressing'))

            process.wait()

            with self._lock:
                self._processes.pop(index, None)
                if self._should_stop:
                    self._cleanup_file(out_path)
                    self.progress.emit(index, 0, tr('cancelled'))
                    return

            if process.returncode == 0 and os.path.exists(out_path):
                out_size = os.path.getsize(out_path)
                if out_size > 0:
                    # 检查是否比输入大
                    if out_size >= in_size:
                        logger.info(f"Output larger than input for [{index}], removing")
                        self._cleanup_file(out_path)
                        with self._lock:
                            self._total_in += in_size
                            self._total_out += in_size  # 视为无变化
                            self._completed += 1
                        self.file_done.emit(index, True, in_size)  # 标记为原始大小
                    else:
                        with self._lock:
                            self._total_in += in_size
                            self._total_out += out_size
                            self._completed += 1
                        self.file_done.emit(index, True, out_size)
                else:
                    self._cleanup_file(out_path)
                    with self._lock:
                        self._failed += 1
                    self.file_done.emit(index, False, 0)
            else:
                self._cleanup_file(out_path)
                stderr_tail = '\n'.join(stderr_lines[-10:])
                logger.error(f"FFmpeg failed for [{index}], returncode={process.returncode if process else 'N/A'}\n{stderr_tail}")
                with self._lock:
                    self._failed += 1
                self.file_done.emit(index, False, 0)

        except Exception as e:
            logger.error(f"Compression exception for [{index}]: {e}")
            if process:
                try:
                    process.terminate()
                except OSError:
                    pass
            self._cleanup_file(out_path)
            with self._lock:
                self._processes.pop(index, None)
                self._failed += 1
            self.file_done.emit(index, False, 0)

    @staticmethod
    def _cleanup_file(path):
        """安全删除文件"""
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError as e:
            logger.warning(f"Failed to cleanup {path}: {e}")

    def stop(self):
        with self._lock:
            self._should_stop = True
            for idx, proc in self._processes.items():
                try:
                    proc.terminate()
                except OSError:
                    pass


# ============ 拖放区域 ============
class DropArea(QFrame):
    files_dropped = pyqtSignal(list)
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style(False)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(4)

        label = QLabel(tr('drop_hint'))
        label.setStyleSheet("color: #666; font-size: 14px; border: none; background: transparent;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        hint = QLabel(tr('format_hint'))
        hint.setStyleSheet("color: #999; font-size: 12px; border: none; background: transparent;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

    def _update_style(self, hover):
        color = "#007AFF" if hover else "#c0c0c0"
        bg = "#f0f7ff" if hover else "#fafafa"
        self.setStyleSheet(f"QFrame {{ border: 1.5px dashed {color}; border-radius: 10px; background: {bg}; }}")

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.setAcceptDrops(enabled)
        if not enabled:
            self.setCursor(Qt.CursorShape.ForbiddenCursor)
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, e):
        if self.isEnabled():
            self.clicked.emit()

    def enterEvent(self, e):
        if self.isEnabled():
            self._update_style(True)

    def leaveEvent(self, e):
        self._update_style(False)

    def dragEnterEvent(self, e):
        if self.isEnabled() and e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._update_style(True)

    def dragLeaveEvent(self, e):
        self._update_style(False)

    def dropEvent(self, e):
        self._update_style(False)
        if not self.isEnabled():
            return
        files = []
        for url in e.mimeData().urls():
            p = url.toLocalFile()
            if os.path.isfile(p) and Path(p).suffix.lower() in VIDEO_EXTENSIONS:
                files.append(p)
            elif os.path.isdir(p):
                for f in Path(p).rglob('*'):
                    if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS:
                        files.append(str(f))
        if files:
            self.files_dropped.emit(files)


# ============ 主窗口 ============
class MainWindow(QMainWindow):
    # 线程安全的信号，用于从线程池回调更新 UI
    _video_info_signal = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.files = []
        self.worker = None
        self.available_encoder_keys = []
        self._is_compressing = False
        self._worker_file_count = 0  # worker 启动时的文件数，用于进度计算

        self._video_info_signal.connect(self._on_video_info_from_pool)
        self.info_pool = VideoInfoPool(callback=self._emit_video_info, max_workers=4)

        self.init_ui()
        QTimer.singleShot(100, self.check_environment)

    def _emit_video_info(self, row, duration_str):
        """线程池回调 → 发射信号到主线程"""
        self._video_info_signal.emit(row, duration_str)

    def _on_video_info_from_pool(self, row, duration_str):
        """主线程中更新表格"""
        if row < self.table.rowCount():
            item = self.table.item(row, 1)
            if item:
                item.setText(duration_str)

    def init_ui(self):
        self.setWindowTitle(tr('app_title'))
        self.setMinimumSize(900, 660)

        def _fix_combo(combo):
            """去掉下拉列表弹出框的顶部/底部横线"""
            container = combo.view().parentWidget()
            if container:
                container.setStyleSheet("QWidget { border: none; background: white; border-radius: 4px; }")
            return combo

        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f7; }
            QComboBox {
                padding: 5px 10px; border: 1px solid #d2d2d7; border-radius: 5px;
                background: white; color: #333; min-width: 80px; font-size: 13px;
            }
            QComboBox:hover { border-color: #007AFF; }
            QComboBox::drop-down { border: none; width: 18px; }
            QComboBox QAbstractItemView {
                background: white; color: #333; border: 1px solid #d2d2d7; border-radius: 4px;
                selection-background-color: #007AFF; selection-color: white;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px 10px; border: none;
            }
            QLineEdit {
                padding: 5px 10px; border: 1px solid #d2d2d7; border-radius: 5px;
                background: white; color: #333; font-size: 13px;
            }
            QLineEdit:focus { border-color: #007AFF; }
            QTableWidget {
                border: 1px solid #d2d2d7; border-radius: 8px; background: white;
                color: #333; font-size: 13px;
            }
            QTableWidget::item { padding: 4px 8px; color: #333; }
            QTableWidget::item:selected { background-color: #007AFF; color: white; }
            QHeaderView::section {
                background: #fafafa; border: none; border-bottom: 1px solid #e0e0e0;
                padding: 8px; font-weight: 500; font-size: 12px; color: #666;
            }
            QProgressBar { border: none; border-radius: 3px; background: #e0e0e0; height: 6px; }
            QProgressBar::chunk { background: #007AFF; border-radius: 3px; }
            QSpinBox {
                padding: 5px 10px; border: 1px solid #d2d2d7; border-radius: 5px;
                background: white; color: #333; font-size: 13px;
            }
            QSpinBox:hover { border-color: #007AFF; }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0; height: 0; border: none;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 0; height: 0;
            }
        """)

        # 菜单栏 - 语言切换
        menubar = self.menuBar()
        settings_menu = menubar.addMenu(tr('language'))
        zh_action = QAction(tr('chinese'), self)
        zh_action.triggered.connect(lambda: self.switch_language('zh'))
        settings_menu.addAction(zh_action)
        en_action = QAction(tr('english'), self)
        en_action.triggered.connect(lambda: self.switch_language('en'))
        settings_menu.addAction(en_action)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # 标题行
        title_row = QHBoxLayout()
        title = QLabel(tr('batch_compress'))
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #1d1d1f;")
        title_row.addWidget(title)
        title_row.addStretch()
        self.status_indicator = QLabel()
        self.status_indicator.setStyleSheet("font-size: 11px;")
        title_row.addWidget(self.status_indicator)
        layout.addLayout(title_row)

        # 编码模式
        encoder_frame = QFrame()
        encoder_frame.setStyleSheet(
            "QFrame { background: #e8f4ff; border-radius: 8px; }"
            " QLabel { background: transparent; color: #333; }"
        )
        encoder_layout = QHBoxLayout(encoder_frame)
        encoder_layout.setContentsMargins(14, 10, 14, 10)

        enc_label = QLabel(tr('encoder_mode'))
        enc_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #007AFF;")
        encoder_layout.addWidget(enc_label)

        self.encoder_combo = QComboBox()
        self.encoder_combo.setMinimumWidth(200)
        self.encoder_combo.currentIndexChanged.connect(self.on_encoder_changed)
        _fix_combo(self.encoder_combo)
        encoder_layout.addWidget(self.encoder_combo)

        encoder_layout.addSpacing(16)
        self.encoder_info = QLabel()
        self.encoder_info.setStyleSheet("font-size: 12px; color: #666;")
        encoder_layout.addWidget(self.encoder_info)
        encoder_layout.addStretch()

        # 参数指南按钮
        self.guide_btn = QPushButton(tr('guide_toggle'))
        self.guide_btn.setFixedHeight(26)
        self.guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.guide_btn.setCheckable(True)
        self.guide_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: 1px solid #007AFF; border-radius: 13px;
                color: #007AFF; font-size: 12px; padding: 0 10px;
            }
            QPushButton:hover { background: #007AFF; color: white; }
            QPushButton:checked { background: #007AFF; color: white; }
        """)
        self.guide_btn.clicked.connect(self._toggle_guide)
        encoder_layout.addWidget(self.guide_btn)

        layout.addWidget(encoder_frame)

        # 可折叠的参数指南面板（固定高度，可滚动）
        self.guide_panel = QFrame()
        self.guide_panel.setStyleSheet(
            "QFrame { background: #fffbf0; border: 1px solid #f0e6cc; border-radius: 8px; }"
        )
        self.guide_panel.setVisible(False)
        self.guide_panel.setFixedHeight(160)
        guide_outer = QVBoxLayout(self.guide_panel)
        guide_outer.setContentsMargins(0, 0, 0, 0)

        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            " QWidget { background: transparent; }"
            " QScrollBar:vertical { width: 6px; background: transparent; }"
            " QScrollBar::handle:vertical { background: #ccc; border-radius: 3px; min-height: 20px; }"
            " QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        )
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(16, 12, 16, 12)
        self.guide_label = QLabel(tr('guide_content'))
        self.guide_label.setWordWrap(True)
        self.guide_label.setStyleSheet("font-size: 12px; color: #555; line-height: 1.5; background: transparent; border: none;")
        inner_layout.addWidget(self.guide_label)
        scroll.setWidget(inner)
        guide_outer.addWidget(scroll)
        layout.addWidget(self.guide_panel)

        # 设置行
        settings_frame = QFrame()
        settings_frame.setStyleSheet(
            "QFrame { background: white; border-radius: 8px; border: 1px solid #e0e0e0; }"
            " QLabel { background: transparent; color: #333; }"
        )
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(14, 10, 14, 10)
        settings_layout.setSpacing(16)

        # 质量
        q_label = QLabel(tr('quality'))
        q_label.setStyleSheet("font-size: 13px; color: #666;")
        settings_layout.addWidget(q_label)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([tr(k) for k in QUALITY_TR_KEYS])
        self.quality_combo.setCurrentIndex(1)  # balanced
        _fix_combo(self.quality_combo)
        settings_layout.addWidget(self.quality_combo)

        # 速度
        s_label = QLabel(tr('speed'))
        s_label.setStyleSheet("font-size: 13px; color: #666;")
        settings_layout.addWidget(s_label)
        self.speed_combo = QComboBox()
        self.speed_combo.addItems([tr(k) for k in SPEED_TR_KEYS])
        self.speed_combo.setCurrentIndex(1)  # balanced
        _fix_combo(self.speed_combo)
        settings_layout.addWidget(self.speed_combo)

        # 分辨率
        r_label = QLabel(tr('resolution'))
        r_label.setStyleSheet("font-size: 13px; color: #666;")
        settings_layout.addWidget(r_label)
        self.resolution_combo = QComboBox()
        for tr_key, _ in RESOLUTION_OPTIONS:
            display = tr(tr_key) if tr_key == 'keep_original' else tr_key
            self.resolution_combo.addItem(display)
        _fix_combo(self.resolution_combo)
        settings_layout.addWidget(self.resolution_combo)

        # 并行数
        p_label = QLabel(tr('parallel'))
        p_label.setStyleSheet("font-size: 13px; color: #666;")
        settings_layout.addWidget(p_label)
        self.parallel_spin = QSpinBox()
        self.parallel_spin.setRange(1, 8)
        self.parallel_spin.setValue(2)
        self.parallel_spin.setToolTip(tr('parallel_tip'))
        self.parallel_spin.setFixedWidth(44)
        self.parallel_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.parallel_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        settings_layout.addWidget(self.parallel_spin)

        settings_layout.addStretch()
        layout.addWidget(settings_frame)

        # 输出目录
        output_frame = QFrame()
        output_frame.setStyleSheet(
            "QFrame { background: white; border-radius: 8px; border: 1px solid #e0e0e0; }"
            " QLabel { background: transparent; color: #333; }"
        )
        output_layout = QHBoxLayout(output_frame)
        output_layout.setContentsMargins(14, 10, 14, 10)

        out_label = QLabel(tr('output_dir'))
        out_label.setStyleSheet("font-size: 13px; color: #666;")
        output_layout.addWidget(out_label)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText(tr('output_placeholder'))
        self.output_edit.setReadOnly(True)
        output_layout.addWidget(self.output_edit, 1)

        browse_btn = QPushButton(tr('select'))
        browse_btn.setFixedSize(60, 28)
        browse_btn.setStyleSheet("""
            QPushButton { background: #f0f0f0; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; }
            QPushButton:hover { background: #e0e0e0; }
        """)
        browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(browse_btn)

        clear_out_btn = QPushButton(tr('clear'))
        clear_out_btn.setFixedSize(60, 28)
        clear_out_btn.setStyleSheet("""
            QPushButton { background: #f0f0f0; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; }
            QPushButton:hover { background: #e0e0e0; }
        """)
        clear_out_btn.clicked.connect(lambda: self.output_edit.clear())
        output_layout.addWidget(clear_out_btn)

        layout.addWidget(output_frame)

        # 拖放区域
        self.drop_area = DropArea()
        self.drop_area.files_dropped.connect(self.add_files)
        self.drop_area.clicked.connect(self.browse_files)
        layout.addWidget(self.drop_area)

        # 文件操作按钮
        btn_row = QHBoxLayout()

        self.add_file_btn = QPushButton(tr('add_files'))
        self.add_file_btn.setFixedHeight(30)
        self.add_file_btn.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; padding: 0 12px; }
            QPushButton:hover { background: #f5f5f5; border-color: #007AFF; }
        """)
        self.add_file_btn.clicked.connect(self.browse_files)
        btn_row.addWidget(self.add_file_btn)

        self.add_folder_btn = QPushButton(tr('add_folder'))
        self.add_folder_btn.setFixedHeight(30)
        self.add_folder_btn.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; padding: 0 12px; }
            QPushButton:hover { background: #f5f5f5; border-color: #007AFF; }
        """)
        self.add_folder_btn.clicked.connect(self.browse_folder)
        btn_row.addWidget(self.add_folder_btn)

        btn_row.addStretch()

        self.file_count_label = QLabel()
        self.file_count_label.setStyleSheet("font-size: 12px; color: #666;")
        btn_row.addWidget(self.file_count_label)

        btn_row.addStretch()

        self.remove_btn = QPushButton(tr('remove_selected'))
        self.remove_btn.setFixedHeight(30)
        self.remove_btn.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; padding: 0 12px; }
            QPushButton:hover { background: #fff0f0; border-color: #ff3b30; color: #ff3b30; }
        """)
        self.remove_btn.clicked.connect(self.remove_selected)
        btn_row.addWidget(self.remove_btn)

        self.clear_btn = QPushButton(tr('clear_list'))
        self.clear_btn.setFixedHeight(30)
        self.clear_btn.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; padding: 0 12px; }
            QPushButton:hover { background: #fff0f0; border-color: #ff3b30; color: #ff3b30; }
        """)
        self.clear_btn.clicked.connect(self.clear_files)
        btn_row.addWidget(self.clear_btn)

        layout.addLayout(btn_row)

        # 文件表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            tr('col_filename'), tr('col_duration'), tr('col_size'),
            tr('col_progress'), tr('col_output'), tr('col_status')
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col, width in [(1, 70), (2, 80), (3, 100), (4, 80), (5, 80)]:
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(col, width)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        # 右键菜单
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_menu)
        # Delete/Backspace 快捷键删除
        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence.StandardKey.Delete, self.table, self.remove_selected)
        QShortcut(QKeySequence(Qt.Key.Key_Backspace), self.table, self.remove_selected)
        layout.addWidget(self.table, 1)

        # 底部进度和按钮
        bottom_row = QHBoxLayout()

        self.total_progress = QProgressBar()
        self.total_progress.setFixedHeight(8)
        self.total_progress.setTextVisible(False)
        bottom_row.addWidget(self.total_progress, 1)

        self.progress_label = QLabel(tr('ready'))
        self.progress_label.setStyleSheet("font-size: 12px; color: #666; min-width: 100px;")
        bottom_row.addWidget(self.progress_label)

        self.stop_btn = QPushButton(tr('stop'))
        self.stop_btn.setFixedSize(70, 32)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton { background: #ff3b30; border: none; border-radius: 6px; color: white; font-weight: 500; font-size: 13px; }
            QPushButton:hover { background: #e0352b; }
            QPushButton:disabled { background: #ccc; }
        """)
        self.stop_btn.clicked.connect(self.stop_compression)
        bottom_row.addWidget(self.stop_btn)

        self.start_btn = QPushButton(tr('start'))
        self.start_btn.setFixedSize(100, 32)
        self.start_btn.setStyleSheet("""
            QPushButton { background: #007AFF; border: none; border-radius: 6px; color: white; font-weight: 500; font-size: 13px; }
            QPushButton:hover { background: #0066d6; }
            QPushButton:disabled { background: #ccc; }
        """)
        self.start_btn.clicked.connect(self.start_compression)
        bottom_row.addWidget(self.start_btn)

        layout.addLayout(bottom_row)

        # 初始化文件计数
        self.update_count()


    # ---- UI 状态管理 ----

    def _set_compressing(self, active):
        """统一管理压缩状态下的 UI 锁定/解锁"""
        self._is_compressing = active
        # 压缩中禁用所有可能修改文件列表的控件
        self.add_file_btn.setEnabled(not active)
        self.add_folder_btn.setEnabled(not active)
        self.remove_btn.setEnabled(not active)
        self.clear_btn.setEnabled(not active)
        self.drop_area.setEnabled(not active)
        # 压缩参数控件
        self.encoder_combo.setEnabled(not active)
        self.quality_combo.setEnabled(not active)
        self.resolution_combo.setEnabled(not active)
        self.parallel_spin.setEnabled(not active)
        # 速度需要根据编码器决定
        if active:
            self.speed_combo.setEnabled(False)
        else:
            self._update_speed_enabled()
        # 按钮
        self.start_btn.setEnabled(not active)
        self.stop_btn.setEnabled(active)

    def _update_speed_enabled(self):
        """根据当前编码器更新速度选项的可用性"""
        idx = self.encoder_combo.currentIndex()
        if 0 <= idx < len(self.available_encoder_keys):
            enc_key = self.available_encoder_keys[idx]
            cfg = ENCODER_CONFIGS.get(enc_key, {})
            has_preset = cfg.get('has_preset', False)
            self.speed_combo.setEnabled(has_preset)
            if not has_preset:
                self.speed_combo.setToolTip(tr('speed_not_available'))
                # 显示为不可用状态，让用户一眼看出
                self.speed_combo.setStyleSheet(
                    "QComboBox { background: #f0f0f0; color: #999; }"
                )
            else:
                self.speed_combo.setToolTip('')
                self.speed_combo.setStyleSheet('')  # 恢复默认样式
        else:
            self.speed_combo.setEnabled(False)

    # ---- 事件处理 ----

    def _toggle_guide(self):
        """切换参数指南面板的显示/隐藏"""
        visible = self.guide_btn.isChecked()
        self.guide_panel.setVisible(visible)

    def switch_language(self, lang):
        if lang == get_lang():
            return
        LM.save_language(lang)
        # 即时重建窗口，无需手动重启
        self._switching_language = True
        self.close()

    def on_encoder_changed(self, index):
        """编码器切换时更新提示和速度可用性"""
        if index < 0 or index >= len(self.available_encoder_keys):
            return
        enc_key = self.available_encoder_keys[index]
        cfg = ENCODER_CONFIGS.get(enc_key, {})
        self.encoder_info.setText(tr(cfg.get('info_key', 'info_cpu')))
        self._update_speed_enabled()

    def check_environment(self):
        """检查 FFmpeg 环境并初始化编码器"""
        ffmpeg = get_ffmpeg_path()
        try:
            result = subprocess.run([ffmpeg, '-version'], **_subprocess_kwargs(timeout=5))
            if result.returncode == 0:
                self.status_indicator.setText(tr('ffmpeg_ready'))
                self.status_indicator.setStyleSheet("font-size: 11px; color: #34c759;")

                self.available_encoder_keys = detect_available_encoders()
                self.encoder_combo.clear()
                for key in self.available_encoder_keys:
                    self.encoder_combo.addItem(tr(f'enc_{key}'))

                # 默认选择推荐编码器
                preferred = 'apple_h264' if IS_MAC else ('nvidia' if IS_WIN else 'cpu_h264')
                if preferred in self.available_encoder_keys:
                    self.encoder_combo.setCurrentIndex(self.available_encoder_keys.index(preferred))
            else:
                self._show_ffmpeg_error()
        except Exception as e:
            logger.error(f"FFmpeg check failed: {e}")
            self._show_ffmpeg_error()

    def _show_ffmpeg_error(self):
        self.status_indicator.setText(tr('ffmpeg_not_found'))
        self.status_indicator.setStyleSheet("font-size: 11px; color: #ff3b30;")
        self.start_btn.setEnabled(False)
        msg = tr('ffmpeg_error_mac') if IS_MAC else tr('ffmpeg_error_win')
        QMessageBox.warning(self, tr('missing_dep'), msg)

    # ---- 文件操作 ----

    def browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, tr('select_output'))
        if folder:
            self.output_edit.setText(folder)

    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, tr('select_video'), "",
            f"{tr('video_files')} ({VIDEO_FILTER_STR});;{tr('all_files')} (*)"
        )
        if files:
            self.add_files(files)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, tr('select_folder'))
        if folder:
            files = [
                str(f) for f in Path(folder).rglob('*')
                if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
            ]
            if files:
                self.add_files(files)

    def add_files(self, paths):
        """添加文件到列表"""
        if self._is_compressing:
            return
        existing = {f['path'] for f in self.files}

        for p in paths:
            if p in existing:
                continue
            try:
                size = os.path.getsize(p)
                name = os.path.basename(p)

                self.files.append({'path': p, 'name': name, 'size': size})

                row = self.table.rowCount()
                self.table.insertRow(row)

                name_item = QTableWidgetItem(name)
                name_item.setToolTip(p)
                self.table.setItem(row, 0, name_item)

                dur_item = QTableWidgetItem("...")
                dur_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 1, dur_item)

                size_item = QTableWidgetItem(fmt_size(size))
                size_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, size_item)

                progress_bar = QProgressBar()
                progress_bar.setRange(0, 100)
                progress_bar.setValue(0)
                progress_bar.setTextVisible(True)
                progress_bar.setFormat("%p%")
                progress_bar.setStyleSheet("""
                    QProgressBar { border: none; border-radius: 3px; background: #e0e0e0; height: 16px; text-align: center; font-size: 11px; color: #333; }
                    QProgressBar::chunk { background: #007AFF; border-radius: 3px; }
                """)
                self.table.setCellWidget(row, 3, progress_bar)

                out_item = QTableWidgetItem("-")
                out_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 4, out_item)

                status_item = QTableWidgetItem(tr('waiting'))
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                status_item.setForeground(QColor("#666"))
                self.table.setItem(row, 5, status_item)

                # 线程池获取时长
                self.info_pool.submit(row, p)

            except Exception as e:
                logger.warning(f"Failed to add file {p}: {e}")

        self.update_count()

    def _show_table_menu(self, pos):
        """右键菜单"""
        if self._is_compressing:
            return
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background: white; border: 1px solid #d2d2d7; border-radius: 6px; padding: 4px 0; }
            QMenu::item { padding: 6px 20px; font-size: 13px; color: #333; }
            QMenu::item:selected { background: #007AFF; color: white; border-radius: 4px; margin: 0 4px; }
        """)
        selected = self.table.selectedIndexes()
        if selected:
            remove_action = menu.addAction(tr('remove_selected'))
            remove_action.triggered.connect(self.remove_selected)
        clear_action = menu.addAction(tr('clear_list'))
        clear_action.triggered.connect(self.clear_files)
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def remove_selected(self):
        if self._is_compressing:
            return
        rows = sorted(set(idx.row() for idx in self.table.selectedIndexes()), reverse=True)
        for row in rows:
            if row < len(self.files):
                del self.files[row]
            self.table.removeRow(row)
        self.update_count()

    def clear_files(self):
        if self._is_compressing:
            return
        self.files.clear()
        self.table.setRowCount(0)
        self.update_count()

    def update_count(self):
        count = len(self.files)
        total_size = sum(f['size'] for f in self.files)
        self.file_count_label.setText(
            tr('file_count').format(count=count, size=fmt_size(total_size))
        )


    # ---- 压缩控制 ----

    def start_compression(self):
        if not self.files:
            QMessageBox.information(self, tr('hint'), tr('add_files_first'))
            return

        idx = self.encoder_combo.currentIndex()
        if idx < 0 or idx >= len(self.available_encoder_keys):
            return
        enc_key = self.available_encoder_keys[idx]

        # 获取分辨率设置
        res_idx = self.resolution_combo.currentIndex()
        if 0 <= res_idx < len(RESOLUTION_OPTIONS):
            _, res_value = RESOLUTION_OPTIONS[res_idx]
        else:
            res_value = None

        settings = {
            'encoder_key': enc_key,
            'quality_key': get_quality_internal_key(self.quality_combo.currentText()),
            'speed_key': get_speed_internal_key(self.speed_combo.currentText()),
            'resolution': res_value,
            'output_dir': self.output_edit.text() or None,
            'parallel': self.parallel_spin.value(),
        }

        # 重置表格状态
        for row in range(self.table.rowCount()):
            progress_bar = self.table.cellWidget(row, 3)
            if progress_bar:
                progress_bar.setValue(0)
                progress_bar.setStyleSheet("""
                    QProgressBar { border: none; border-radius: 3px; background: #e0e0e0; height: 16px; text-align: center; font-size: 11px; color: #333; }
                    QProgressBar::chunk { background: #007AFF; border-radius: 3px; }
                """)
            out_item = self.table.item(row, 4)
            if out_item:
                out_item.setText("-")
            status_item = self.table.item(row, 5)
            if status_item:
                status_item.setText(tr('waiting'))
                status_item.setForeground(QColor("#666"))

        self.total_progress.setValue(0)
        self.progress_label.setText(tr('preparing'))
        self._worker_file_count = len(self.files)

        # 锁定 UI
        self._set_compressing(True)

        # 启动 worker
        self.worker = CompressionWorker(self.files.copy(), settings)
        self.worker.progress.connect(self.on_progress)
        self.worker.file_done.connect(self.on_file_done)
        self.worker.all_done.connect(self.on_all_done)
        self.worker.start()

    def stop_compression(self):
        if self.worker:
            self.worker.stop()
            self.progress_label.setText(tr('stopping'))

    def on_progress(self, index, percent, status):
        if index < self.table.rowCount():
            progress_bar = self.table.cellWidget(index, 3)
            if progress_bar:
                progress_bar.setValue(percent)
            status_item = self.table.item(index, 5)
            if status_item:
                status_item.setText(status)
                status_item.setForeground(QColor("#007AFF"))

    def on_file_done(self, index, success, output_size):
        if index >= self.table.rowCount():
            return
        progress_bar = self.table.cellWidget(index, 3)
        status_item = self.table.item(index, 5)
        out_item = self.table.item(index, 4)

        if success:
            if progress_bar:
                progress_bar.setValue(100)
            if out_item:
                out_item.setText(fmt_size(output_size))
            if status_item and index < len(self.files):
                in_size = self.files[index]['size']
                if output_size >= in_size:
                    # 输出 >= 输入，已自动删除输出
                    status_item.setText("≈0%")
                    status_item.setForeground(QColor("#999"))
                else:
                    diff = in_size - output_size
                    ratio = diff / in_size * 100 if in_size > 0 else 0
                    status_item.setText(f"-{ratio:.0f}%")
                    status_item.setForeground(QColor("#34c759"))
        else:
            if progress_bar:
                progress_bar.setValue(0)
                progress_bar.setStyleSheet("""
                    QProgressBar { border: none; border-radius: 3px; background: #ffe0e0; height: 16px; text-align: center; font-size: 11px; color: #333; }
                    QProgressBar::chunk { background: #ff3b30; border-radius: 3px; }
                """)
            if status_item:
                status_item.setText(tr('failed'))
                status_item.setForeground(QColor("#ff3b30"))

        # 更新总进度（基于已完成的文件数）
        if self._worker_file_count > 0:
            # 统计已完成（成功或失败）的文件数
            done_count = 0
            for r in range(min(self._worker_file_count, self.table.rowCount())):
                si = self.table.item(r, 5)
                if si:
                    text = si.text()
                    if text not in (tr('waiting'), tr('compressing'), tr('preparing')):
                        done_count += 1
            overall = int(done_count / self._worker_file_count * 100)
            self.total_progress.setValue(min(overall, 100))
            self.progress_label.setText(
                tr('processing').format(current=done_count, total=self._worker_file_count)
            )

    def on_all_done(self, completed, failed, total, input_size, output_size, was_stopped):
        """全部完成"""
        self.total_progress.setValue(100)
        self.progress_label.setText(
            tr('done').format(completed=completed, total=total)
        )

        # 更新被取消的文件状态
        if was_stopped:
            for row in range(self.table.rowCount()):
                status_item = self.table.item(row, 5)
                if status_item and status_item.text() in (tr('waiting'), tr('compressing'), tr('preparing')):
                    status_item.setText(tr('cancelled'))
                    status_item.setForeground(QColor("#999"))

        # 解锁 UI
        self._set_compressing(False)

        # 显示结果弹窗（至少有一个文件被处理过才弹）
        if completed > 0 or failed > 0:
            dialog = ResultDialog(
                self, completed, failed, total,
                input_size, output_size, was_stopped
            )
            dialog.exec()

    # ---- 窗口关闭清理 ----

    def closeEvent(self, event):
        """关闭窗口时终止所有子进程"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(3000)  # 等待最多 3 秒
        self.info_pool.shutdown()
        event.accept()


# ============ 主函数 ============
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setOrganizationName(APP_NAME)

    while True:
        app.setApplicationName(tr('app_title'))
        window = MainWindow()
        window._switching_language = False
        window.show()
        app.exec()
        if not window._switching_language:
            break
        # 语言已切换，循环重建窗口

    sys.exit(0)


if __name__ == '__main__':
    main()
