#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SheCan Video Compressor V2.3
Cross-platform (macOS / Windows)
Auto-download FFmpeg, Bilingual UI (Chinese/English)
"""

import sys
import os
import subprocess
import re
import platform
import multiprocessing
import urllib.request
import zipfile
import shutil
import locale
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QProgressBar, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QLineEdit,
    QAbstractItemView, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QLocale
from PyQt6.QtGui import QColor

# System info
IS_MAC = platform.system() == 'Darwin'
IS_WIN = platform.system() == 'Windows'
CPU_COUNT = multiprocessing.cpu_count()

# Detect system language
def get_system_language():
    """Detect if system uses Chinese"""
    try:
        lang = QLocale.system().name()  # e.g., 'zh_CN', 'en_US'
        if lang.startswith('zh'):
            return 'zh'
    except:
        pass
    try:
        lang = locale.getdefaultlocale()[0] or ''
        if lang.startswith('zh'):
            return 'zh'
    except:
        pass
    return 'en'

LANG = get_system_language()

# Translations
TR = {
    'zh': {
        'app_title': 'SheCan 视频压缩工具',
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
        'file_count': '共 {0} 个文件，{1}',
        'start': '开始压缩',
        'stop': '停止',
        'ready': '就绪',
        'preparing': '准备中...',
        'processing': '处理中 {0}/{1}',
        'done': '完成 {0}/{1}',
        'compressing': '压缩中',
        'waiting': '等待',
        'failed': '失败',
        'stopping': '正在停止...',
        # Table headers
        'col_filename': '文件名',
        'col_duration': '时长',
        'col_size': '大小',
        'col_progress': '进度',
        'col_output': '压缩后',
        'col_status': '状态',
        # Encoder names
        'cpu_h264': 'CPU H.264 (兼容性最好)',
        'cpu_h265': 'CPU H.265 (体积更小)',
        'apple_h264': 'Apple GPU H.264 (推荐)',
        'apple_h265': 'Apple GPU H.265',
        'nvidia': 'NVIDIA GPU (N卡加速)',
        'amd': 'AMD GPU (A卡加速)',
        'intel': 'Intel GPU (核显加速)',
        # Encoder info
        'info_apple': '使用 Apple 硬件加速，速度快',
        'info_nvidia': '使用 NVIDIA GPU 加速',
        'info_amd': '使用 AMD GPU 加速',
        'info_intel': '使用 Intel 核显加速',
        'info_h265': 'H.265 编码，体积更小但兼容性稍差',
        'info_cpu': 'CPU 编码，兼容性最好',
        # Quality/Speed
        'high_quality': '高质量',
        'balanced': '平衡',
        'small_size': '小体积',
        'fast': '快速',
        'high_compress': '高压缩',
        'keep_original': '保持原始',
        # FFmpeg
        'ffmpeg_ready': '● FFmpeg 就绪',
        'ffmpeg_missing': '● FFmpeg 未安装',
        'install_ffmpeg': '安装 FFmpeg',
        'need_ffmpeg': '需要安装 FFmpeg',
        'ffmpeg_desc': 'FFmpeg 是视频压缩的核心组件\n点击下方按钮自动下载安装（约 80MB）',
        'auto_install': '自动安装',
        'cancel': '取消',
        'downloading': '正在下载 FFmpeg...',
        'extracting': '正在解压...',
        'download_failed': '下载失败: {0}',
        'install_success': 'FFmpeg 安装成功',
        'install_failed': 'FFmpeg 安装失败，请手动安装',
        'no_ffmpeg_warning': '未安装 FFmpeg，无法使用压缩功能',
        # Result dialog
        'compress_done': '压缩完成',
        'files_processed': '成功处理:',
        'original_size': '原始大小:',
        'compressed_size': '压缩后:',
        'space_saved': '节省空间:',
        'size_increased': '体积增加:',
        'ok': '确定',
        'files_unit': '{0}/{1} 个文件',
        # Dialogs
        'hint': '提示',
        'error': '错误',
        'add_files_first': '请先添加视频文件',
        'select_output': '选择输出目录',
        'select_video': '选择视频文件',
        'select_folder': '选择文件夹',
        'video_files': '视频文件',
        'all_files': '所有文件',
        'cannot_create_dir': '无法创建输出目录: {0}',
    },
    'en': {
        'app_title': 'SheCan Video Compressor',
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
        'file_count': '{0} files, {1}',
        'start': 'Start',
        'stop': 'Stop',
        'ready': 'Ready',
        'preparing': 'Preparing...',
        'processing': 'Processing {0}/{1}',
        'done': 'Done {0}/{1}',
        'compressing': 'Compressing',
        'waiting': 'Waiting',
        'failed': 'Failed',
        'stopping': 'Stopping...',
        'col_filename': 'Filename',
        'col_duration': 'Duration',
        'col_size': 'Size',
        'col_progress': 'Progress',
        'col_output': 'Output',
        'col_status': 'Status',
        'cpu_h264': 'CPU H.264 (Best Compatibility)',
        'cpu_h265': 'CPU H.265 (Smaller Size)',
        'apple_h264': 'Apple GPU H.264 (Recommended)',
        'apple_h265': 'Apple GPU H.265',
        'nvidia': 'NVIDIA GPU (Hardware Accel)',
        'amd': 'AMD GPU (Hardware Accel)',
        'intel': 'Intel GPU (Quick Sync)',
        'info_apple': 'Apple hardware acceleration, fast',
        'info_nvidia': 'NVIDIA GPU acceleration',
        'info_amd': 'AMD GPU acceleration',
        'info_intel': 'Intel Quick Sync acceleration',
        'info_h265': 'H.265 codec, smaller but less compatible',
        'info_cpu': 'CPU encoding, best compatibility',
        'high_quality': 'High Quality',
        'balanced': 'Balanced',
        'small_size': 'Small Size',
        'fast': 'Fast',
        'high_compress': 'High Compress',
        'keep_original': 'Original',
        'ffmpeg_ready': '● FFmpeg Ready',
        'ffmpeg_missing': '● FFmpeg Missing',
        'install_ffmpeg': 'Install FFmpeg',
        'need_ffmpeg': 'FFmpeg Required',
        'ffmpeg_desc': 'FFmpeg is required for video compression\nClick below to auto-download (~80MB)',
        'auto_install': 'Auto Install',
        'cancel': 'Cancel',
        'downloading': 'Downloading FFmpeg...',
        'extracting': 'Extracting...',
        'download_failed': 'Download failed: {0}',
        'install_success': 'FFmpeg installed successfully',
        'install_failed': 'FFmpeg installation failed',
        'no_ffmpeg_warning': 'FFmpeg not installed, compression unavailable',
        'compress_done': 'Compression Complete',
        'files_processed': 'Processed:',
        'original_size': 'Original:',
        'compressed_size': 'Compressed:',
        'space_saved': 'Saved:',
        'size_increased': 'Increased:',
        'ok': 'OK',
        'files_unit': '{0}/{1} files',
        'hint': 'Info',
        'error': 'Error',
        'add_files_first': 'Please add video files first',
        'select_output': 'Select Output Directory',
        'select_video': 'Select Video Files',
        'select_folder': 'Select Folder',
        'video_files': 'Video Files',
        'all_files': 'All Files',
        'cannot_create_dir': 'Cannot create output directory: {0}',
    }
}

def tr(key, *args):
    """Get translated string"""
    text = TR.get(LANG, TR['en']).get(key, key)
    if args:
        return text.format(*args)
    return text

# FFmpeg URLs
FFMPEG_URLS = {
    'Windows': 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
    'Darwin': 'https://evermeet.cx/ffmpeg/getrelease/zip'
}

def get_app_data_dir():
    if IS_WIN:
        base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        return os.path.join(base, 'SheCan', 'VideoCompressor')
    return os.path.expanduser('~/Library/Application Support/SheCan/VideoCompressor')

def get_bundled_ffmpeg_path():
    app_dir = get_app_data_dir()
    return os.path.join(app_dir, 'ffmpeg', 'ffmpeg.exe' if IS_WIN else 'ffmpeg')

def get_ffmpeg_path():
    bundled = get_bundled_ffmpeg_path()
    if os.path.exists(bundled):
        return bundled
    if IS_WIN and getattr(sys, 'frozen', False):
        ffmpeg = os.path.join(sys._MEIPASS, 'ffmpeg', 'ffmpeg.exe')
        if os.path.exists(ffmpeg):
            return ffmpeg
    if IS_WIN:
        return 'ffmpeg'
    for p in [os.path.expanduser('~/bin/ffmpeg'), '/usr/local/bin/ffmpeg', '/opt/homebrew/bin/ffmpeg']:
        if os.path.exists(p):
            return p
    return 'ffmpeg'

def get_ffprobe_path():
    ffmpeg = get_ffmpeg_path()
    return ffmpeg.replace('ffmpeg.exe', 'ffprobe.exe') if IS_WIN else ffmpeg.replace('ffmpeg', 'ffprobe')

def is_ffmpeg_available():
    try:
        kwargs = {'capture_output': True, 'timeout': 5}
        if IS_WIN:
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        return subprocess.run([get_ffmpeg_path(), '-version'], **kwargs).returncode == 0
    except:
        return False


# Encoder configurations
def get_encoders_config():
    encoders = {
        tr('cpu_h264'): {
            'encoder': 'libx264', 'quality_param': '-crf',
            'quality_map': {tr('high_quality'): '18', tr('balanced'): '23', tr('small_size'): '30'},
            'has_preset': True, 'preset_map': {tr('fast'): 'veryfast', tr('balanced'): 'medium', tr('high_compress'): 'slow'}
        },
        tr('cpu_h265'): {
            'encoder': 'libx265', 'quality_param': '-crf',
            'quality_map': {tr('high_quality'): '22', tr('balanced'): '28', tr('small_size'): '35'},
            'has_preset': True, 'preset_map': {tr('fast'): 'veryfast', tr('balanced'): 'medium', tr('high_compress'): 'slow'}
        }
    }
    if IS_MAC:
        encoders[tr('apple_h264')] = {
            'encoder': 'h264_videotoolbox', 'quality_param': '-b:v',
            'quality_map': {tr('high_quality'): '8M', tr('balanced'): '4M', tr('small_size'): '2M'},
            'has_preset': False, 'preset_map': {}
        }
        encoders[tr('apple_h265')] = {
            'encoder': 'hevc_videotoolbox', 'quality_param': '-b:v',
            'quality_map': {tr('high_quality'): '6M', tr('balanced'): '3M', tr('small_size'): '1.5M'},
            'has_preset': False, 'preset_map': {}
        }
    if IS_WIN:
        encoders[tr('nvidia')] = {
            'encoder': 'h264_nvenc', 'quality_param': '-cq',
            'quality_map': {tr('high_quality'): '19', tr('balanced'): '23', tr('small_size'): '28'},
            'has_preset': True, 'preset_map': {tr('fast'): 'fast', tr('balanced'): 'medium', tr('high_compress'): 'slow'}
        }
        encoders[tr('amd')] = {
            'encoder': 'h264_amf', 'quality_param': '-qp_i',
            'quality_map': {tr('high_quality'): '18', tr('balanced'): '23', tr('small_size'): '28'},
            'has_preset': False, 'preset_map': {}
        }
        encoders[tr('intel')] = {
            'encoder': 'h264_qsv', 'quality_param': '-global_quality',
            'quality_map': {tr('high_quality'): '20', tr('balanced'): '25', tr('small_size'): '30'},
            'has_preset': True, 'preset_map': {tr('fast'): 'veryfast', tr('balanced'): 'medium', tr('high_compress'): 'slow'}
        }
    return encoders

ENCODERS = get_encoders_config()

def detect_available_encoders():
    available = []
    try:
        kwargs = {'capture_output': True, 'text': True, 'timeout': 10}
        if IS_WIN:
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        output = subprocess.run([get_ffmpeg_path(), '-hide_banner', '-encoders'], **kwargs).stdout
        for name, cfg in ENCODERS.items():
            if cfg['encoder'] in output:
                available.append(name)
    except:
        pass
    return available or [tr('cpu_h264')]


class FFmpegDownloader(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def run(self):
        try:
            self.progress.emit(0, tr('downloading'))
            app_dir = get_app_data_dir()
            os.makedirs(app_dir, exist_ok=True)
            url = FFMPEG_URLS.get(platform.system())
            if not url:
                self.finished.emit(False, "Unsupported OS")
                return
            
            if IS_MAC:
                zip_path = os.path.join(app_dir, 'ffmpeg.zip')
                self._download(url, zip_path)
                self.progress.emit(50, tr('extracting'))
                ffmpeg_dir = os.path.join(app_dir, 'ffmpeg')
                os.makedirs(ffmpeg_dir, exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    for m in zf.namelist():
                        if 'ffmpeg' in m.lower():
                            zf.extract(m, ffmpeg_dir)
                            src = os.path.join(ffmpeg_dir, m)
                            dst = os.path.join(ffmpeg_dir, 'ffmpeg')
                            if src != dst: shutil.move(src, dst)
                            os.chmod(dst, 0o755)
                self.progress.emit(60, tr('downloading'))
                probe_zip = os.path.join(app_dir, 'ffprobe.zip')
                self._download('https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip', probe_zip)
                self.progress.emit(80, tr('extracting'))
                with zipfile.ZipFile(probe_zip, 'r') as zf:
                    for m in zf.namelist():
                        if 'ffprobe' in m.lower():
                            zf.extract(m, ffmpeg_dir)
                            src = os.path.join(ffmpeg_dir, m)
                            dst = os.path.join(ffmpeg_dir, 'ffprobe')
                            if src != dst: shutil.move(src, dst)
                            os.chmod(dst, 0o755)
                os.remove(zip_path)
                os.remove(probe_zip)
            else:
                zip_path = os.path.join(app_dir, 'ffmpeg.zip')
                self._download(url, zip_path)
                self.progress.emit(60, tr('extracting'))
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(app_dir)
                for item in os.listdir(app_dir):
                    item_path = os.path.join(app_dir, item)
                    if os.path.isdir(item_path) and 'ffmpeg' in item.lower():
                        bin_dir = os.path.join(item_path, 'bin')
                        if os.path.exists(bin_dir):
                            target = os.path.join(app_dir, 'ffmpeg')
                            if os.path.exists(target): shutil.rmtree(target)
                            shutil.move(bin_dir, target)
                            shutil.rmtree(item_path)
                            break
                os.remove(zip_path)
            
            self.progress.emit(100, "Done")
            self.finished.emit(is_ffmpeg_available(), tr('install_success') if is_ffmpeg_available() else tr('install_failed'))
        except Exception as e:
            self.finished.emit(False, tr('download_failed', str(e)))
    
    def _download(self, url, path):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as r, open(path, 'wb') as f:
            f.write(r.read())


class FFmpegSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('install_ffmpeg'))
        self.setFixedSize(400, 200)
        self.setStyleSheet("QDialog { background: white; }")
        self.downloader = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        title = QLabel(tr('need_ffmpeg'))
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1d1d1f;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel(tr('ffmpeg_desc'))
        desc.setStyleSheet("font-size: 13px; color: #666;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("QProgressBar { border: none; border-radius: 4px; background: #e0e0e0; height: 8px; } QProgressBar::chunk { background: #007AFF; border-radius: 4px; }")
        layout.addWidget(self.progress)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 12px; color: #666;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        btn_row = QHBoxLayout()
        self.cancel_btn = QPushButton(tr('cancel'))
        self.cancel_btn.setFixedSize(100, 32)
        self.cancel_btn.setStyleSheet("QPushButton { background: #f0f0f0; border: none; border-radius: 6px; color: #333; font-size: 13px; } QPushButton:hover { background: #e0e0e0; }")
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()
        
        self.install_btn = QPushButton(tr('auto_install'))
        self.install_btn.setFixedSize(100, 32)
        self.install_btn.setStyleSheet("QPushButton { background: #007AFF; border: none; border-radius: 6px; color: white; font-weight: 500; font-size: 13px; } QPushButton:hover { background: #0066d6; } QPushButton:disabled { background: #ccc; }")
        self.install_btn.clicked.connect(self.start_download)
        btn_row.addWidget(self.install_btn)
        layout.addLayout(btn_row)
    
    def start_download(self):
        self.install_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.downloader = FFmpegDownloader()
        self.downloader.progress.connect(lambda p, s: (self.progress.setValue(p), self.status_label.setText(s)))
        self.downloader.finished.connect(self.on_finished)
        self.downloader.start()
    
    def on_finished(self, success, message):
        if success:
            self.accept()
        else:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("font-size: 12px; color: #ff3b30;")
            self.install_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)


class ResultDialog(QDialog):
    def __init__(self, parent, completed, total, input_size, output_size):
        super().__init__(parent)
        self.setWindowTitle(tr('compress_done'))
        self.setFixedSize(320, 220)
        self.setStyleSheet("QDialog { background: white; }")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        title = QLabel(tr('compress_done'))
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1d1d1f;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        saved = input_size - output_size
        ratio = abs(saved) / input_size * 100 if input_size > 0 else 0
        
        info = [
            (tr('files_processed'), tr('files_unit', completed, total), "#333"),
            (tr('original_size'), self._fmt(input_size), "#333"),
            (tr('compressed_size'), self._fmt(output_size), "#333"),
        ]
        if saved > 0:
            info.append((tr('space_saved'), f"-{self._fmt(saved)} ({ratio:.0f}%)", "#34c759"))
        elif saved < 0:
            info.append((tr('size_increased'), f"+{self._fmt(abs(saved))} ({ratio:.0f}%)", "#ff9500"))
        
        for label, value, color in info:
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
        ok_btn.setStyleSheet("QPushButton { background: #007AFF; border: none; border-radius: 6px; color: white; font-weight: 500; font-size: 13px; } QPushButton:hover { background: #0066d6; }")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
    
    def _fmt(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024: return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"


class VideoInfoWorker(QThread):
    info_ready = pyqtSignal(int, str)
    def __init__(self, row, filepath):
        super().__init__()
        self.row, self.filepath = row, filepath
    def run(self):
        dur_str = "-"
        try:
            cmd = [get_ffprobe_path(), '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', self.filepath]
            kwargs = {'capture_output': True, 'text': True, 'timeout': 10}
            if IS_WIN: kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            r = subprocess.run(cmd, **kwargs)
            if r.returncode == 0 and r.stdout.strip():
                dur = float(r.stdout.strip())
                m, s = divmod(int(dur), 60)
                h, m = divmod(m, 60)
                dur_str = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
        except: pass
        self.info_ready.emit(self.row, dur_str)


class CompressionWorker(QThread):
    progress = pyqtSignal(int, int, str)
    file_done = pyqtSignal(int, bool, int)
    all_done = pyqtSignal(int, int, int, int)
    error = pyqtSignal(str)
    
    def __init__(self, files, settings):
        super().__init__()
        self.files, self.settings = files, settings
        self.should_stop = False
        self.process = None

    def run(self):
        total, completed, total_in, total_out = len(self.files), 0, 0, 0
        enc_cfg = ENCODERS.get(self.settings['encoder_name'], list(ENCODERS.values())[0])
        threads = max(2, CPU_COUNT // 2)
        ffmpeg = get_ffmpeg_path()
        
        for i, f in enumerate(self.files):
            if self.should_stop: break
            in_path, in_size = f['path'], f['size']
            total_in += in_size
            out_dir = self.settings.get('output_dir') or os.path.dirname(in_path)
            out_path = os.path.join(out_dir, f"{os.path.splitext(f['name'])[0]}_compressed.mp4")
            
            self.progress.emit(i, 0, tr('preparing'))
            if not os.path.exists(in_path):
                self.file_done.emit(i, False, 0)
                continue
            try:
                os.makedirs(out_dir, exist_ok=True)
            except Exception as e:
                self.error.emit(tr('cannot_create_dir', str(e)))
                self.file_done.emit(i, False, 0)
                continue
            
            q_val = enc_cfg['quality_map'].get(self.settings['quality'], '23')
            cmd = [ffmpeg, '-i', in_path, '-c:v', enc_cfg['encoder'], enc_cfg['quality_param'], q_val]
            if enc_cfg.get('has_preset'):
                cmd.extend(['-preset', enc_cfg['preset_map'].get(self.settings['speed'], 'medium')])
            res = self.settings.get('resolution', tr('keep_original'))
            if res == '1080p': cmd.extend(['-vf', 'scale=-2:1080'])
            elif res == '720p': cmd.extend(['-vf', 'scale=-2:720'])
            elif res == '480p': cmd.extend(['-vf', 'scale=-2:480'])
            cmd.extend(['-threads', str(threads), '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', '-y', out_path])
            
            duration = self._get_duration(in_path)
            try:
                kwargs = {'stderr': subprocess.PIPE, 'universal_newlines': True}
                if IS_WIN: kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                self.process = subprocess.Popen(cmd, **kwargs)
                for line in self.process.stderr:
                    if self.should_stop:
                        self.process.terminate()
                        break
                    m = re.search(r'time=(\d+):(\d+):(\d+\.?\d*)', line)
                    if m and duration > 0:
                        cur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
                        self.progress.emit(i, min(int(cur / duration * 100), 99), tr('compressing'))
                self.process.wait()
                if self.process.returncode == 0 and os.path.exists(out_path):
                    out_size = os.path.getsize(out_path)
                    if out_size > 0:
                        total_out += out_size
                        self.file_done.emit(i, True, out_size)
                        completed += 1
                    else:
                        os.remove(out_path)
                        self.file_done.emit(i, False, 0)
                else:
                    self.file_done.emit(i, False, 0)
            except:
                self.file_done.emit(i, False, 0)
        self.all_done.emit(completed, total, total_in, total_out)
    
    def _get_duration(self, path):
        try:
            cmd = [get_ffprobe_path(), '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', path]
            kwargs = {'capture_output': True, 'text': True, 'timeout': 30}
            if IS_WIN: kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            r = subprocess.run(cmd, **kwargs)
            return float(r.stdout.strip()) if r.stdout.strip() else 0
        except: return 0
    
    def stop(self):
        self.should_stop = True
        if self.process:
            try: self.process.terminate()
            except: pass


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
        for text, style in [(tr('drop_hint'), "color: #666; font-size: 14px;"), (tr('format_hint'), "color: #999; font-size: 12px;")]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"{style} border: none; background: transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)
    
    def _update_style(self, hover):
        c, bg = ("#007AFF", "#f0f7ff") if hover else ("#c0c0c0", "#fafafa")
        self.setStyleSheet(f"QFrame {{ border: 1.5px dashed {c}; border-radius: 10px; background: {bg}; }}")
    
    def mousePressEvent(self, e): self.clicked.emit()
    def enterEvent(self, e): self._update_style(True)
    def leaveEvent(self, e): self._update_style(False)
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): e.acceptProposedAction(); self._update_style(True)
    def dragLeaveEvent(self, e): self._update_style(False)
    def dropEvent(self, e):
        self._update_style(False)
        exts = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.ts'}
        files = []
        for url in e.mimeData().urls():
            p = url.toLocalFile()
            if os.path.isfile(p) and Path(p).suffix.lower() in exts: files.append(p)
            elif os.path.isdir(p):
                files.extend(str(f) for f in Path(p).rglob('*') if f.is_file() and f.suffix.lower() in exts)
        if files: self.files_dropped.emit(files)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.files, self.worker, self.info_workers, self.available_encoders = [], None, [], []
        self.init_ui()
        # Delay environment check to after window is shown
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.check_environment)
    
    def init_ui(self):
        self.setWindowTitle(tr('app_title'))
        self.setMinimumSize(900, 660)
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f7; }
            QComboBox { padding: 5px 10px; border: 1px solid #d2d2d7; border-radius: 5px; background: white; color: #333; min-width: 80px; font-size: 13px; }
            QComboBox:hover { border-color: #007AFF; }
            QComboBox::drop-down { border: none; width: 18px; }
            QComboBox QAbstractItemView { background: white; color: #333; border: 1px solid #d2d2d7; selection-background-color: #007AFF; selection-color: white; }
            QLineEdit { padding: 5px 10px; border: 1px solid #d2d2d7; border-radius: 5px; background: white; color: #333; font-size: 13px; }
            QTableWidget { border: 1px solid #d2d2d7; border-radius: 8px; background: white; color: #333; font-size: 13px; }
            QTableWidget::item { padding: 4px 8px; color: #333; }
            QTableWidget::item:selected { background-color: #007AFF; color: white; }
            QHeaderView::section { background: #fafafa; border: none; border-bottom: 1px solid #e0e0e0; padding: 8px; font-weight: 500; font-size: 12px; color: #666; }
            QProgressBar { border: none; border-radius: 3px; background: #e0e0e0; height: 6px; }
            QProgressBar::chunk { background: #007AFF; border-radius: 3px; }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)
        
        # Title
        title_row = QHBoxLayout()
        title = QLabel(tr('batch_compress'))
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #1d1d1f;")
        title_row.addWidget(title)
        title_row.addStretch()
        self.status_indicator = QLabel()
        self.status_indicator.setStyleSheet("font-size: 11px;")
        title_row.addWidget(self.status_indicator)
        layout.addLayout(title_row)
        
        # Encoder
        enc_frame = QFrame()
        enc_frame.setStyleSheet("QFrame { background: #e8f4ff; border-radius: 8px; } QLabel { background: transparent; color: #333; }")
        enc_layout = QHBoxLayout(enc_frame)
        enc_layout.setContentsMargins(14, 10, 14, 10)
        enc_lbl = QLabel(tr('encoder_mode'))
        enc_lbl.setStyleSheet("font-size: 13px; font-weight: 500; color: #007AFF;")
        enc_layout.addWidget(enc_lbl)
        self.encoder_combo = QComboBox()
        self.encoder_combo.setMinimumWidth(200)
        self.encoder_combo.currentTextChanged.connect(self.on_encoder_changed)
        enc_layout.addWidget(self.encoder_combo)
        enc_layout.addSpacing(16)
        self.encoder_info = QLabel()
        self.encoder_info.setStyleSheet("font-size: 12px; color: #666;")
        enc_layout.addWidget(self.encoder_info)
        enc_layout.addStretch()
        layout.addWidget(enc_frame)
        
        # Settings
        settings_frame = QFrame()
        settings_frame.setStyleSheet("QFrame { background: white; border-radius: 8px; border: 1px solid #e0e0e0; } QLabel { background: transparent; color: #333; }")
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(14, 10, 14, 10)
        settings_layout.setSpacing(20)
        
        quality_items = [tr('high_quality'), tr('balanced'), tr('small_size')]
        speed_items = [tr('fast'), tr('balanced'), tr('high_compress')]
        res_items = [tr('keep_original'), '1080p', '720p', '480p']
        
        for lbl_text, items, default in [(tr('quality'), quality_items, tr('balanced')),
                                          (tr('speed'), speed_items, tr('balanced')),
                                          (tr('resolution'), res_items, tr('keep_original'))]:
            l = QLabel(lbl_text)
            l.setStyleSheet("font-size: 13px; color: #666;")
            settings_layout.addWidget(l)
            combo = QComboBox()
            combo.addItems(items)
            combo.setCurrentText(default)
            settings_layout.addWidget(combo)
            if lbl_text == tr('quality'): self.quality_combo = combo
            elif lbl_text == tr('speed'): self.speed_combo = combo
            else: self.resolution_combo = combo
        settings_layout.addStretch()
        layout.addWidget(settings_frame)
        
        # Output
        out_frame = QFrame()
        out_frame.setStyleSheet("QFrame { background: white; border-radius: 8px; border: 1px solid #e0e0e0; } QLabel { background: transparent; color: #333; }")
        out_layout = QHBoxLayout(out_frame)
        out_layout.setContentsMargins(14, 10, 14, 10)
        out_lbl = QLabel(tr('output_dir'))
        out_lbl.setStyleSheet("font-size: 13px; color: #666;")
        out_layout.addWidget(out_lbl)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText(tr('output_placeholder'))
        self.output_edit.setReadOnly(True)
        out_layout.addWidget(self.output_edit, 1)
        for text, slot in [(tr('select'), self.browse_output), (tr('clear'), lambda: self.output_edit.clear())]:
            btn = QPushButton(text)
            btn.setFixedSize(60, 28)
            btn.setStyleSheet("QPushButton { background: #f0f0f0; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; } QPushButton:hover { background: #e0e0e0; }")
            btn.clicked.connect(slot)
            out_layout.addWidget(btn)
        layout.addWidget(out_frame)
        
        # Drop area
        self.drop_area = DropArea()
        self.drop_area.files_dropped.connect(self.add_files)
        self.drop_area.clicked.connect(self.browse_files)
        layout.addWidget(self.drop_area)
        
        # Buttons
        btn_row = QHBoxLayout()
        for text, slot in [(tr('add_files'), self.browse_files), (tr('add_folder'), self.browse_folder)]:
            btn = QPushButton(text)
            btn.setFixedHeight(30)
            btn.setStyleSheet("QPushButton { background: white; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; padding: 0 12px; } QPushButton:hover { background: #f5f5f5; border-color: #007AFF; }")
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        self.file_count_label = QLabel(tr('file_count', 0, '0 B'))
        self.file_count_label.setStyleSheet("font-size: 12px; color: #666;")
        btn_row.addWidget(self.file_count_label)
        btn_row.addStretch()
        for text, slot in [(tr('remove_selected'), self.remove_selected), (tr('clear_list'), self.clear_files)]:
            btn = QPushButton(text)
            btn.setFixedHeight(30)
            btn.setStyleSheet("QPushButton { background: white; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; padding: 0 12px; } QPushButton:hover { background: #fff0f0; border-color: #ff3b30; color: #ff3b30; }")
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([tr('col_filename'), tr('col_duration'), tr('col_size'), tr('col_progress'), tr('col_output'), tr('col_status')])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i, w in [(1, 70), (2, 80), (3, 100), (4, 80), (5, 80)]:
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(i, w)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table, 1)
        
        # Bottom
        bottom = QHBoxLayout()
        self.total_progress = QProgressBar()
        self.total_progress.setFixedHeight(8)
        self.total_progress.setTextVisible(False)
        bottom.addWidget(self.total_progress, 1)
        self.progress_label = QLabel(tr('ready'))
        self.progress_label.setStyleSheet("font-size: 12px; color: #666; min-width: 100px;")
        bottom.addWidget(self.progress_label)
        self.stop_btn = QPushButton(tr('stop'))
        self.stop_btn.setFixedSize(70, 32)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton { background: #ff3b30; border: none; border-radius: 6px; color: white; font-weight: 500; font-size: 13px; } QPushButton:hover { background: #e0352b; } QPushButton:disabled { background: #ccc; }")
        self.stop_btn.clicked.connect(self.stop_compression)
        bottom.addWidget(self.stop_btn)
        self.start_btn = QPushButton(tr('start'))
        self.start_btn.setFixedSize(100, 32)
        self.start_btn.setStyleSheet("QPushButton { background: #007AFF; border: none; border-radius: 6px; color: white; font-weight: 500; font-size: 13px; } QPushButton:hover { background: #0066d6; } QPushButton:disabled { background: #ccc; }")
        self.start_btn.clicked.connect(self.start_compression)
        bottom.addWidget(self.start_btn)
        layout.addLayout(bottom)
    
    def on_encoder_changed(self, name):
        if name in ENCODERS:
            enc = ENCODERS[name]['encoder']
            info_map = {'videotoolbox': tr('info_apple'), 'nvenc': tr('info_nvidia'), 'amf': tr('info_amd'), 'qsv': tr('info_intel'), 'libx265': tr('info_h265')}
            self.encoder_info.setText(next((v for k, v in info_map.items() if k in enc), tr('info_cpu')))
            self.speed_combo.setEnabled(ENCODERS[name].get('has_preset', False))
    
    def check_environment(self):
        if is_ffmpeg_available():
            self.status_indicator.setText(tr('ffmpeg_ready'))
            self.status_indicator.setStyleSheet("font-size: 11px; color: #34c759;")
            self.available_encoders = detect_available_encoders()
            self.encoder_combo.clear()
            self.encoder_combo.addItems(self.available_encoders)
            if IS_MAC and tr('apple_h264') in self.available_encoders:
                self.encoder_combo.setCurrentText(tr('apple_h264'))
            elif IS_WIN and tr('nvidia') in self.available_encoders:
                self.encoder_combo.setCurrentText(tr('nvidia'))
            self.start_btn.setEnabled(True)
        else:
            self.status_indicator.setText(tr('ffmpeg_missing'))
            self.status_indicator.setStyleSheet("font-size: 11px; color: #ff9500;")
            self.start_btn.setEnabled(False)
            # Add default encoder option even without FFmpeg
            self.encoder_combo.clear()
            self.encoder_combo.addItems([tr('cpu_h264')])
            # Show install dialog
            dialog = FFmpegSetupDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.check_environment()
    
    def browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, tr('select_output'))
        if folder: self.output_edit.setText(folder)
    
    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, tr('select_video'), "",
            f"{tr('video_files')} (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v *.mpg *.mpeg *.ts);;{tr('all_files')} (*)")
        if files: self.add_files(files)
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, tr('select_folder'))
        if folder:
            exts = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.ts'}
            self.add_files([str(f) for f in Path(folder).rglob('*') if f.is_file() and f.suffix.lower() in exts])
    
    def add_files(self, paths):
        existing = {f['path'] for f in self.files}
        for p in paths:
            if p in existing: continue
            try:
                size, name = os.path.getsize(p), os.path.basename(p)
                self.files.append({'path': p, 'name': name, 'size': size})
                row = self.table.rowCount()
                self.table.insertRow(row)
                item = QTableWidgetItem(name)
                item.setToolTip(p)
                self.table.setItem(row, 0, item)
                for col, text in [(1, "..."), (2, self._fmt(size)), (4, "-"), (5, tr('waiting'))]:
                    it = QTableWidgetItem(text)
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if col == 5: it.setForeground(QColor("#666"))
                    self.table.setItem(row, col, it)
                pb = QProgressBar()
                pb.setRange(0, 100)
                pb.setTextVisible(True)
                pb.setFormat("%p%")
                pb.setStyleSheet("QProgressBar { border: none; border-radius: 3px; background: #e0e0e0; height: 16px; text-align: center; font-size: 11px; color: #333; } QProgressBar::chunk { background: #007AFF; border-radius: 3px; }")
                self.table.setCellWidget(row, 3, pb)
                w = VideoInfoWorker(row, p)
                w.info_ready.connect(lambda r, d: self.table.item(r, 1).setText(d) if r < self.table.rowCount() else None)
                self.info_workers.append(w)
                w.start()
            except: pass
        self._update_count()
    
    def remove_selected(self):
        for row in sorted(set(i.row() for i in self.table.selectedIndexes()), reverse=True):
            if row < len(self.files): del self.files[row]
            self.table.removeRow(row)
        self._update_count()
    
    def clear_files(self):
        self.files.clear()
        self.table.setRowCount(0)
        self._update_count()
    
    def _update_count(self):
        self.file_count_label.setText(tr('file_count', len(self.files), self._fmt(sum(f['size'] for f in self.files))))
    
    def _fmt(self, size):
        for u in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024: return f"{size:.1f} {u}"
            size /= 1024
        return f"{size:.1f} PB"
    
    def start_compression(self):
        if not self.files:
            QMessageBox.information(self, tr('hint'), tr('add_files_first'))
            return
        settings = {'encoder_name': self.encoder_combo.currentText(), 'quality': self.quality_combo.currentText(),
                    'speed': self.speed_combo.currentText(), 'resolution': self.resolution_combo.currentText(),
                    'output_dir': self.output_edit.text() or None}
        for row in range(self.table.rowCount()):
            pb = self.table.cellWidget(row, 3)
            if pb: pb.setValue(0)
            for col, text in [(4, "-"), (5, tr('waiting'))]:
                it = self.table.item(row, col)
                if it: it.setText(text); it.setForeground(QColor("#666")) if col == 5 else None
        self.total_progress.setValue(0)
        self.progress_label.setText(tr('preparing'))
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        for c in [self.encoder_combo, self.quality_combo, self.speed_combo, self.resolution_combo]: c.setEnabled(False)
        self.worker = CompressionWorker(self.files.copy(), settings)
        self.worker.progress.connect(self._on_progress)
        self.worker.file_done.connect(self._on_file_done)
        self.worker.all_done.connect(self._on_all_done)
        self.worker.error.connect(lambda m: QMessageBox.warning(self, tr('error'), m))
        self.worker.start()
    
    def stop_compression(self):
        if self.worker: self.worker.stop(); self.progress_label.setText(tr('stopping'))
    
    def _on_progress(self, idx, pct, status):
        if idx < self.table.rowCount():
            pb = self.table.cellWidget(idx, 3)
            if pb: pb.setValue(pct)
            it = self.table.item(idx, 5)
            if it: it.setText(status); it.setForeground(QColor("#007AFF"))
        total = len(self.files)
        if total: self.total_progress.setValue(int((idx * 100 + pct) / total)); self.progress_label.setText(tr('processing', idx + 1, total))
    
    def _on_file_done(self, idx, ok, out_size):
        if idx >= self.table.rowCount(): return
        pb, st, out = self.table.cellWidget(idx, 3), self.table.item(idx, 5), self.table.item(idx, 4)
        if ok:
            if pb: pb.setValue(100)
            if out: out.setText(self._fmt(out_size))
            if st:
                diff = self.files[idx]['size'] - out_size
                ratio = abs(diff) / self.files[idx]['size'] * 100 if self.files[idx]['size'] else 0
                st.setText(f"-{ratio:.0f}%" if diff > 0 else f"+{ratio:.0f}%")
                st.setForeground(QColor("#34c759" if diff > 0 else "#ff9500"))
        else:
            if pb: pb.setValue(0); pb.setStyleSheet("QProgressBar { border: none; border-radius: 3px; background: #ffe0e0; height: 16px; text-align: center; font-size: 11px; color: #333; } QProgressBar::chunk { background: #ff3b30; border-radius: 3px; }")
            if st: st.setText(tr('failed')); st.setForeground(QColor("#ff3b30"))
    
    def _on_all_done(self, completed, total, in_size, out_size):
        self.total_progress.setValue(100)
        self.progress_label.setText(tr('done', completed, total))
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        for c in [self.encoder_combo, self.quality_combo, self.resolution_combo]: c.setEnabled(True)
        if self.encoder_combo.currentText() in ENCODERS:
            self.speed_combo.setEnabled(ENCODERS[self.encoder_combo.currentText()].get('has_preset', False))
        if completed: ResultDialog(self, completed, total, in_size, out_size).exec()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName(tr('app_title'))
    app.setOrganizationName("SheCan")
    MainWindow().show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
