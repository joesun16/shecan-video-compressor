#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SheCan 视频批量压缩工具 V2.8
跨平台支持 (macOS / Windows)
FFmpeg 内置，双语界面
"""

import sys
import os
import subprocess
import re
import platform
import multiprocessing
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QProgressBar, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QLineEdit,
    QAbstractItemView, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QLocale
from PyQt6.QtGui import QColor, QAction

# 系统信息
IS_MAC = platform.system() == 'Darwin'
IS_WIN = platform.system() == 'Windows'
CPU_COUNT = multiprocessing.cpu_count()


# ============ 语言管理 ============
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
            return os.path.join(base, 'SheCan', 'VideoCompressor', 'config.json')
        return os.path.expanduser('~/Library/Application Support/SheCan/VideoCompressor/config.json')

    def _load_saved_language(self):
        config_path = self._get_config_path()
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if 'language' in config:
                        self.current = config['language']
                        return
        except:
            pass
        self._detect_system_language()
    
    def _detect_system_language(self):
        try:
            if IS_MAC:
                result = subprocess.run(['defaults', 'read', '-g', 'AppleLanguages'],
                                       capture_output=True, text=True, timeout=2)
                if 'zh' in result.stdout.lower():
                    self.current = 'zh'
                    return
        except:
            pass
        try:
            locale_name = QLocale.system().name()
            if locale_name.startswith('zh'):
                self.current = 'zh'
                return
        except:
            pass
        self.current = 'en'
    
    def save_language(self, lang):
        self.current = lang
        config_path = self._get_config_path()
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            config['language'] = lang
            with open(config_path, 'w') as f:
                json.dump(config, f)
        except:
            pass
    
    def get(self):
        return self.current


LM = LanguageManager()

def get_lang():
    return LM.get()

def tr(key):
    """翻译函数"""
    texts = {
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
            'start': '开始压缩',
            'stop': '停止',
            'ready': '就绪',
            'preparing': '准备中...',
            'compressing': '压缩中',
            'waiting': '等待',
            'failed': '失败',
            'stopping': '正在停止...',
            'col_filename': '文件名',
            'col_duration': '时长',
            'col_size': '大小',
            'col_progress': '进度',
            'col_output': '压缩后',
            'col_status': '状态',
            'high_quality': '高质量',
            'balanced': '平衡',
            'small_size': '小体积',
            'fast': '快速',
            'high_compress': '高压缩',
            'keep_original': '保持原始',
            'compress_done': '压缩完成',
            'files_processed': '成功处理:',
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
            # 编码器名称
            'cpu_h264': 'CPU H.264 (兼容性最好)',
            'cpu_h265': 'CPU H.265 (体积更小)',
            'apple_h264': 'Apple GPU H.264 (推荐)',
            'apple_h265': 'Apple GPU H.265',
            'nvidia': 'NVIDIA GPU (N卡加速)',
            'amd': 'AMD GPU (A卡加速)',
            'intel': 'Intel GPU (核显加速)',
            # 编码器提示
            'info_apple': '使用 Apple 硬件加速，速度快',
            'info_nvidia': '使用 NVIDIA GPU 加速',
            'info_amd': '使用 AMD GPU 加速',
            'info_intel': '使用 Intel 核显加速',
            'info_h265': 'H.265 编码，体积更小但兼容性稍差',
            'info_cpu': 'CPU 编码，兼容性最好',
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
            'start': 'Start',
            'stop': 'Stop',
            'ready': 'Ready',
            'preparing': 'Preparing...',
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
            'high_quality': 'High Quality',
            'balanced': 'Balanced',
            'small_size': 'Small Size',
            'fast': 'Fast',
            'high_compress': 'High Compress',
            'keep_original': 'Original',
            'compress_done': 'Compression Complete',
            'files_processed': 'Processed:',
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
            # Encoder names
            'cpu_h264': 'CPU H.264 (Best Compatibility)',
            'cpu_h265': 'CPU H.265 (Smaller Size)',
            'apple_h264': 'Apple GPU H.264 (Recommended)',
            'apple_h265': 'Apple GPU H.265',
            'nvidia': 'NVIDIA GPU (Hardware Accel)',
            'amd': 'AMD GPU (Hardware Accel)',
            'intel': 'Intel GPU (Quick Sync)',
            # Encoder info
            'info_apple': 'Apple hardware acceleration, fast',
            'info_nvidia': 'NVIDIA GPU acceleration',
            'info_amd': 'AMD GPU acceleration',
            'info_intel': 'Intel Quick Sync acceleration',
            'info_h265': 'H.265 codec, smaller but less compatible',
            'info_cpu': 'CPU encoding, best compatibility',
        }
    }
    return texts.get(get_lang(), texts['zh']).get(key, key)


# ============ FFmpeg 路径 ============
def get_ffmpeg_path():
    """获取 FFmpeg 路径 - 优先使用内置版本"""
    if getattr(sys, 'frozen', False):
        # 打包后的应用
        if IS_WIN:
            # Windows: PyInstaller 打包，FFmpeg 在 _MEIPASS/ffmpeg/
            bundled = os.path.join(sys._MEIPASS, 'ffmpeg', 'ffmpeg.exe')
            if os.path.exists(bundled):
                return bundled
        else:
            # macOS: py2app 打包，FFmpeg 在 Contents/Resources/ffmpeg/
            exe_dir = os.path.dirname(sys.executable)  # Contents/MacOS
            contents_dir = os.path.dirname(exe_dir)     # Contents
            bundled = os.path.join(contents_dir, 'Resources', 'ffmpeg', 'ffmpeg')
            if os.path.exists(bundled):
                return bundled
    
    # 开发模式或内置版本不存在时，查找系统 FFmpeg
    if IS_WIN:
        return 'ffmpeg'
    else:
        paths = [
            '/opt/homebrew/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            os.path.expanduser('~/bin/ffmpeg'),
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return 'ffmpeg'


def get_ffprobe_path():
    """获取 FFprobe 路径"""
    ffmpeg = get_ffmpeg_path()
    if IS_WIN:
        return ffmpeg.replace('ffmpeg.exe', 'ffprobe.exe')
    return ffmpeg.replace('ffmpeg', 'ffprobe')


# ============ 编码器配置 ============
def get_encoders_config():
    """根据系统返回编码器配置"""
    lang = get_lang()
    
    # 质量映射 key
    q_high = tr('high_quality')
    q_bal = tr('balanced')
    q_small = tr('small_size')
    
    # 速度映射 key
    s_fast = tr('fast')
    s_bal = tr('balanced')
    s_high = tr('high_compress')
    
    encoders = {
        tr('cpu_h264'): {
            'encoder': 'libx264',
            'quality_param': '-crf',
            'quality_map': {q_high: '18', q_bal: '23', q_small: '30'},
            'has_preset': True,
            'preset_map': {s_fast: 'veryfast', s_bal: 'medium', s_high: 'slow'}
        },
        tr('cpu_h265'): {
            'encoder': 'libx265',
            'quality_param': '-crf',
            'quality_map': {q_high: '22', q_bal: '28', q_small: '35'},
            'has_preset': True,
            'preset_map': {s_fast: 'veryfast', s_bal: 'medium', s_high: 'slow'}
        }
    }
    
    if IS_MAC:
        encoders[tr('apple_h264')] = {
            'encoder': 'h264_videotoolbox',
            'quality_param': '-b:v',
            'quality_map': {q_high: '8M', q_bal: '4M', q_small: '2M'},
            'has_preset': False,
            'preset_map': {}
        }
        encoders[tr('apple_h265')] = {
            'encoder': 'hevc_videotoolbox',
            'quality_param': '-b:v',
            'quality_map': {q_high: '6M', q_bal: '3M', q_small: '1.5M'},
            'has_preset': False,
            'preset_map': {}
        }
    
    if IS_WIN:
        encoders[tr('nvidia')] = {
            'encoder': 'h264_nvenc',
            'quality_param': '-cq',
            'quality_map': {q_high: '19', q_bal: '23', q_small: '28'},
            'has_preset': True,
            'preset_map': {s_fast: 'fast', s_bal: 'medium', s_high: 'slow'}
        }
        encoders[tr('amd')] = {
            'encoder': 'h264_amf',
            'quality_param': '-qp_i',
            'quality_map': {q_high: '18', q_bal: '23', q_small: '28'},
            'has_preset': False,
            'preset_map': {}
        }
        encoders[tr('intel')] = {
            'encoder': 'h264_qsv',
            'quality_param': '-global_quality',
            'quality_map': {q_high: '20', q_bal: '25', q_small: '30'},
            'has_preset': True,
            'preset_map': {s_fast: 'veryfast', s_bal: 'medium', s_high: 'slow'}
        }
    
    return encoders


def detect_available_encoders(encoders):
    """检测可用的编码器"""
    available = []
    try:
        ffmpeg = get_ffmpeg_path()
        kwargs = {'capture_output': True, 'text': True, 'timeout': 10}
        if IS_WIN:
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        result = subprocess.run([ffmpeg, '-hide_banner', '-encoders'], **kwargs)
        output = result.stdout
        
        for name, cfg in encoders.items():
            if cfg['encoder'] in output:
                available.append(name)
    except Exception as e:
        print(f"检测编码器失败: {e}")
    
    if not available:
        available = [tr('cpu_h264')]
    
    return available


# ============ 结果弹窗 ============
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
        
        info_data = [
            (tr('files_processed'), f"{completed}/{total}", "#333"),
            (tr('original_size'), self._fmt(input_size), "#333"),
            (tr('compressed_size'), self._fmt(output_size), "#333"),
        ]
        
        if saved > 0:
            info_data.append((tr('space_saved'), f"-{self._fmt(saved)} ({ratio:.0f}%)", "#34c759"))
        elif saved < 0:
            info_data.append((tr('size_increased'), f"+{self._fmt(abs(saved))} ({ratio:.0f}%)", "#ff9500"))
        
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
    
    def _fmt(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"


# ============ 视频信息工作线程 ============
class VideoInfoWorker(QThread):
    info_ready = pyqtSignal(int, str)
    
    def __init__(self, row, filepath):
        super().__init__()
        self.row = row
        self.filepath = filepath
    
    def run(self):
        dur_str = "-"
        try:
            ffprobe = get_ffprobe_path()
            cmd = [ffprobe, '-v', 'error', '-show_entries', 'format=duration',
                   '-of', 'default=noprint_wrappers=1:nokey=1', self.filepath]
            
            kwargs = {'capture_output': True, 'text': True, 'timeout': 10}
            if IS_WIN:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            result = subprocess.run(cmd, **kwargs)
            if result.returncode == 0 and result.stdout.strip():
                dur = float(result.stdout.strip())
                m, s = divmod(int(dur), 60)
                h, m = divmod(m, 60)
                dur_str = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
        except Exception as e:
            print(f"获取时长失败: {e}")
        
        self.info_ready.emit(self.row, dur_str)


# ============ 压缩工作线程 ============
class CompressionWorker(QThread):
    progress = pyqtSignal(int, int, str)
    file_done = pyqtSignal(int, bool, int)
    all_done = pyqtSignal(int, int, int, int)
    error = pyqtSignal(str)
    
    def __init__(self, files, settings, encoders):
        super().__init__()
        self.files = files
        self.settings = settings
        self.encoders = encoders
        self.should_stop = False
        self.process = None

    def get_duration(self, path):
        try:
            ffprobe = get_ffprobe_path()
            cmd = [ffprobe, '-v', 'error', '-show_entries', 'format=duration',
                   '-of', 'default=noprint_wrappers=1:nokey=1', path]
            kwargs = {'capture_output': True, 'text': True, 'timeout': 30}
            if IS_WIN:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            r = subprocess.run(cmd, **kwargs)
            return float(r.stdout.strip()) if r.stdout.strip() else 0
        except:
            return 0
    
    def run(self):
        total = len(self.files)
        completed = 0
        total_in = 0
        total_out = 0
        
        enc_name = self.settings['encoder_name']
        enc_cfg = self.encoders.get(enc_name, list(self.encoders.values())[0])
        quality = self.settings['quality']
        speed = self.settings['speed']
        threads = max(2, CPU_COUNT // 2)
        ffmpeg = get_ffmpeg_path()
        
        for i, f in enumerate(self.files):
            if self.should_stop:
                break
            
            in_path = f['path']
            in_size = f['size']
            total_in += in_size
            
            out_dir = self.settings.get('output_dir') or os.path.dirname(in_path)
            name = os.path.splitext(f['name'])[0]
            out_path = os.path.join(out_dir, f"{name}_compressed.mp4")
            
            self.progress.emit(i, 0, tr('preparing'))
            
            if not os.path.exists(in_path):
                self.file_done.emit(i, False, 0)
                continue
            
            try:
                os.makedirs(out_dir, exist_ok=True)
            except Exception as e:
                self.error.emit(f"{tr('cannot_create_dir')}: {e}")
                self.file_done.emit(i, False, 0)
                continue
            
            q_val = enc_cfg['quality_map'].get(quality, '23')
            cmd = [ffmpeg, '-i', in_path, '-c:v', enc_cfg['encoder'],
                   enc_cfg['quality_param'], q_val]
            
            if enc_cfg.get('has_preset') and enc_cfg.get('preset_map'):
                preset = enc_cfg['preset_map'].get(speed, 'medium')
                cmd.extend(['-preset', preset])
            
            res = self.settings.get('resolution', tr('keep_original'))
            if res == '1080p':
                cmd.extend(['-vf', 'scale=-2:1080'])
            elif res == '720p':
                cmd.extend(['-vf', 'scale=-2:720'])
            elif res == '480p':
                cmd.extend(['-vf', 'scale=-2:480'])
            
            cmd.extend([
                '-threads', str(threads),
                '-c:a', 'aac', '-b:a', '128k',
                '-movflags', '+faststart',
                '-y', out_path
            ])
            
            duration = self.get_duration(in_path)
            
            try:
                kwargs = {'stderr': subprocess.PIPE, 'universal_newlines': True}
                if IS_WIN:
                    kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                
                self.process = subprocess.Popen(cmd, **kwargs)
                
                for line in self.process.stderr:
                    if self.should_stop:
                        self.process.terminate()
                        break
                    
                    match = re.search(r'time=(\d+):(\d+):(\d+\.?\d*)', line)
                    if match and duration > 0:
                        h, m, s = match.groups()
                        cur = int(h) * 3600 + int(m) * 60 + float(s)
                        pct = min(int(cur / duration * 100), 99)
                        self.progress.emit(i, pct, tr('compressing'))
                
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
                    
            except Exception as e:
                print(f"压缩异常: {e}")
                self.file_done.emit(i, False, 0)
        
        self.all_done.emit(completed, total, total_in, total_out)
    
    def stop(self):
        self.should_stop = True
        if self.process:
            try:
                self.process.terminate()
            except:
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
    
    def mousePressEvent(self, e):
        self.clicked.emit()
    
    def enterEvent(self, e):
        self._update_style(True)
    
    def leaveEvent(self, e):
        self._update_style(False)
    
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._update_style(True)
    
    def dragLeaveEvent(self, e):
        self._update_style(False)
    
    def dropEvent(self, e):
        self._update_style(False)
        files = []
        exts = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.ts'}
        
        for url in e.mimeData().urls():
            p = url.toLocalFile()
            if os.path.isfile(p) and Path(p).suffix.lower() in exts:
                files.append(p)
            elif os.path.isdir(p):
                for f in Path(p).rglob('*'):
                    if f.is_file() and f.suffix.lower() in exts:
                        files.append(str(f))
        
        if files:
            self.files_dropped.emit(files)


# ============ 主窗口 ============
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.files = []
        self.worker = None
        self.info_workers = []
        self.encoders = {}
        self.available_encoders = []
        self.init_ui()
        # 延迟检查环境，确保 UI 已完全初始化
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.check_environment)
    
    def init_ui(self):
        self.setWindowTitle(tr('app_title'))
        self.setMinimumSize(900, 660)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f7; }
            QComboBox {
                padding: 5px 10px; border: 1px solid #d2d2d7; border-radius: 5px;
                background: white; color: #333; min-width: 80px; font-size: 13px;
            }
            QComboBox:hover { border-color: #007AFF; }
            QComboBox::drop-down { border: none; width: 18px; }
            QComboBox QAbstractItemView {
                background: white; color: #333; border: 1px solid #d2d2d7;
                selection-background-color: #007AFF; selection-color: white;
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
        encoder_frame.setStyleSheet("QFrame { background: #e8f4ff; border-radius: 8px; } QLabel { background: transparent; color: #333; }")
        encoder_layout = QHBoxLayout(encoder_frame)
        encoder_layout.setContentsMargins(14, 10, 14, 10)
        
        enc_label = QLabel(tr('encoder_mode'))
        enc_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #007AFF;")
        encoder_layout.addWidget(enc_label)
        
        self.encoder_combo = QComboBox()
        self.encoder_combo.setMinimumWidth(200)
        self.encoder_combo.currentTextChanged.connect(self.on_encoder_changed)
        encoder_layout.addWidget(self.encoder_combo)
        
        encoder_layout.addSpacing(16)
        self.encoder_info = QLabel()
        self.encoder_info.setStyleSheet("font-size: 12px; color: #666;")
        encoder_layout.addWidget(self.encoder_info)
        encoder_layout.addStretch()
        layout.addWidget(encoder_frame)
        
        # 设置行
        settings_frame = QFrame()
        settings_frame.setStyleSheet("QFrame { background: white; border-radius: 8px; border: 1px solid #e0e0e0; } QLabel { background: transparent; color: #333; }")
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(14, 10, 14, 10)
        settings_layout.setSpacing(20)
        
        # 质量
        q_label = QLabel(tr('quality'))
        q_label.setStyleSheet("font-size: 13px; color: #666;")
        settings_layout.addWidget(q_label)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([tr('high_quality'), tr('balanced'), tr('small_size')])
        self.quality_combo.setCurrentText(tr('balanced'))
        settings_layout.addWidget(self.quality_combo)
        
        # 速度
        s_label = QLabel(tr('speed'))
        s_label.setStyleSheet("font-size: 13px; color: #666;")
        settings_layout.addWidget(s_label)
        self.speed_combo = QComboBox()
        self.speed_combo.addItems([tr('fast'), tr('balanced'), tr('high_compress')])
        self.speed_combo.setCurrentText(tr('balanced'))
        settings_layout.addWidget(self.speed_combo)
        
        # 分辨率
        r_label = QLabel(tr('resolution'))
        r_label.setStyleSheet("font-size: 13px; color: #666;")
        settings_layout.addWidget(r_label)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([tr('keep_original'), '1080p', '720p', '480p'])
        settings_layout.addWidget(self.resolution_combo)
        
        settings_layout.addStretch()
        layout.addWidget(settings_frame)
        
        # 输出目录
        output_frame = QFrame()
        output_frame.setStyleSheet("QFrame { background: white; border-radius: 8px; border: 1px solid #e0e0e0; } QLabel { background: transparent; color: #333; }")
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
        
        add_file_btn = QPushButton(tr('add_files'))
        add_file_btn.setFixedHeight(30)
        add_file_btn.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; padding: 0 12px; }
            QPushButton:hover { background: #f5f5f5; border-color: #007AFF; }
        """)
        add_file_btn.clicked.connect(self.browse_files)
        btn_row.addWidget(add_file_btn)
        
        add_folder_btn = QPushButton(tr('add_folder'))
        add_folder_btn.setFixedHeight(30)
        add_folder_btn.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; padding: 0 12px; }
            QPushButton:hover { background: #f5f5f5; border-color: #007AFF; }
        """)
        add_folder_btn.clicked.connect(self.browse_folder)
        btn_row.addWidget(add_folder_btn)
        
        btn_row.addStretch()
        
        self.file_count_label = QLabel(f"{tr('col_filename')}: 0")
        self.file_count_label.setStyleSheet("font-size: 12px; color: #666;")
        btn_row.addWidget(self.file_count_label)
        
        btn_row.addStretch()
        
        remove_btn = QPushButton(tr('remove_selected'))
        remove_btn.setFixedHeight(30)
        remove_btn.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; padding: 0 12px; }
            QPushButton:hover { background: #fff0f0; border-color: #ff3b30; color: #ff3b30; }
        """)
        remove_btn.clicked.connect(self.remove_selected)
        btn_row.addWidget(remove_btn)
        
        clear_btn = QPushButton(tr('clear_list'))
        clear_btn.setFixedHeight(30)
        clear_btn.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #d0d0d0; border-radius: 5px; color: #333; font-size: 12px; padding: 0 12px; }
            QPushButton:hover { background: #fff0f0; border-color: #ff3b30; color: #ff3b30; }
        """)
        clear_btn.clicked.connect(self.clear_files)
        btn_row.addWidget(clear_btn)
        
        layout.addLayout(btn_row)
        
        # 文件表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            tr('col_filename'), tr('col_duration'), tr('col_size'),
            tr('col_progress'), tr('col_output'), tr('col_status')
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 70)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 80)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
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
    
    def switch_language(self, lang):
        """切换语言"""
        LM.save_language(lang)
        QMessageBox.information(self, tr('hint'), tr('restart_hint'))
    
    def on_encoder_changed(self, name):
        """编码器切换时更新提示"""
        if name in self.encoders:
            cfg = self.encoders[name]
            encoder = cfg['encoder']
            if 'videotoolbox' in encoder:
                self.encoder_info.setText(tr('info_apple'))
            elif 'nvenc' in encoder:
                self.encoder_info.setText(tr('info_nvidia'))
            elif 'amf' in encoder:
                self.encoder_info.setText(tr('info_amd'))
            elif 'qsv' in encoder:
                self.encoder_info.setText(tr('info_intel'))
            elif 'libx265' in encoder:
                self.encoder_info.setText(tr('info_h265'))
            else:
                self.encoder_info.setText(tr('info_cpu'))
            
            # 更新速度选项可用性
            has_preset = cfg.get('has_preset', False)
            self.speed_combo.setEnabled(has_preset)
            if not has_preset:
                self.speed_combo.setCurrentText(tr('balanced'))

    def check_environment(self):
        """检查环境"""
        # 初始化编码器配置
        self.encoders = get_encoders_config()
        
        ffmpeg = get_ffmpeg_path()
        try:
            kwargs = {'capture_output': True, 'timeout': 5}
            if IS_WIN:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            result = subprocess.run([ffmpeg, '-version'], **kwargs)
            if result.returncode == 0:
                self.status_indicator.setText(tr('ffmpeg_ready'))
                self.status_indicator.setStyleSheet("font-size: 11px; color: #34c759;")
                
                # 检测可用编码器
                self.available_encoders = detect_available_encoders(self.encoders)
                self.encoder_combo.clear()
                self.encoder_combo.addItems(self.available_encoders)
                
                # 默认选择推荐编码器
                if IS_MAC and tr('apple_h264') in self.available_encoders:
                    self.encoder_combo.setCurrentText(tr('apple_h264'))
                elif IS_WIN and tr('nvidia') in self.available_encoders:
                    self.encoder_combo.setCurrentText(tr('nvidia'))
            else:
                self._show_ffmpeg_error()
        except Exception as e:
            print(f"FFmpeg 检查失败: {e}")
            self._show_ffmpeg_error()
    
    def _show_ffmpeg_error(self):
        self.status_indicator.setText(tr('ffmpeg_not_found'))
        self.status_indicator.setStyleSheet("font-size: 11px; color: #ff3b30;")
        self.start_btn.setEnabled(False)
        
        msg = tr('ffmpeg_error_mac') if IS_MAC else tr('ffmpeg_error_win')
        QMessageBox.warning(self, tr('missing_dep'), msg)
    
    def browse_output(self):
        """选择输出目录"""
        folder = QFileDialog.getExistingDirectory(self, tr('select_output'))
        if folder:
            self.output_edit.setText(folder)
    
    def browse_files(self):
        """选择文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self, tr('select_video'), "",
            f"{tr('video_files')} (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v *.mpg *.mpeg *.ts);;{tr('all_files')} (*)"
        )
        if files:
            self.add_files(files)
    
    def browse_folder(self):
        """选择文件夹"""
        folder = QFileDialog.getExistingDirectory(self, tr('select_folder'))
        if folder:
            exts = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.ts'}
            files = []
            for f in Path(folder).rglob('*'):
                if f.is_file() and f.suffix.lower() in exts:
                    files.append(str(f))
            if files:
                self.add_files(files)
    
    def add_files(self, paths):
        """添加文件到列表"""
        existing = {f['path'] for f in self.files}
        
        for p in paths:
            if p in existing:
                continue
            
            try:
                size = os.path.getsize(p)
                name = os.path.basename(p)
                
                self.files.append({
                    'path': p,
                    'name': name,
                    'size': size
                })
                
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # 文件名
                name_item = QTableWidgetItem(name)
                name_item.setToolTip(p)
                self.table.setItem(row, 0, name_item)
                
                # 时长 (异步获取)
                dur_item = QTableWidgetItem("...")
                dur_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 1, dur_item)
                
                # 大小
                size_item = QTableWidgetItem(self.fmt(size))
                size_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, size_item)
                
                # 进度
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
                
                # 压缩后大小
                out_item = QTableWidgetItem("-")
                out_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 4, out_item)
                
                # 状态
                status_item = QTableWidgetItem(tr('waiting'))
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                status_item.setForeground(QColor("#666"))
                self.table.setItem(row, 5, status_item)
                
                # 异步获取时长
                worker = VideoInfoWorker(row, p)
                worker.info_ready.connect(self.on_video_info)
                self.info_workers.append(worker)
                worker.start()
                
            except Exception as e:
                print(f"添加文件失败: {e}")
        
        self.update_count()
    
    def on_video_info(self, row, duration):
        """更新视频时长"""
        if row < self.table.rowCount():
            item = self.table.item(row, 1)
            if item:
                item.setText(duration)
    
    def remove_selected(self):
        """移除选中的文件"""
        rows = sorted(set(idx.row() for idx in self.table.selectedIndexes()), reverse=True)
        for row in rows:
            if row < len(self.files):
                del self.files[row]
            self.table.removeRow(row)
        self.update_count()
    
    def clear_files(self):
        """清空文件列表"""
        self.files.clear()
        self.table.setRowCount(0)
        self.update_count()
    
    def update_count(self):
        """更新文件计数"""
        count = len(self.files)
        total_size = sum(f['size'] for f in self.files)
        lang = get_lang()
        if lang == 'zh':
            self.file_count_label.setText(f"共 {count} 个文件，{self.fmt(total_size)}")
        else:
            self.file_count_label.setText(f"{count} files, {self.fmt(total_size)}")
    
    def fmt(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    def start_compression(self):
        """开始压缩"""
        if not self.files:
            QMessageBox.information(self, tr('hint'), tr('add_files_first'))
            return
        
        settings = {
            'encoder_name': self.encoder_combo.currentText(),
            'quality': self.quality_combo.currentText(),
            'speed': self.speed_combo.currentText(),
            'resolution': self.resolution_combo.currentText(),
            'output_dir': self.output_edit.text() or None
        }
        
        # 重置状态
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
        
        # 禁用控件
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.encoder_combo.setEnabled(False)
        self.quality_combo.setEnabled(False)
        self.speed_combo.setEnabled(False)
        self.resolution_combo.setEnabled(False)
        
        # 启动工作线程
        self.worker = CompressionWorker(self.files.copy(), settings, self.encoders)
        self.worker.progress.connect(self.on_progress)
        self.worker.file_done.connect(self.on_file_done)
        self.worker.all_done.connect(self.on_all_done)
        self.worker.error.connect(lambda msg: QMessageBox.warning(self, tr('error'), msg))
        self.worker.start()
    
    def stop_compression(self):
        """停止压缩"""
        if self.worker:
            self.worker.stop()
            self.progress_label.setText(tr('stopping'))
    
    def on_progress(self, index, percent, status):
        """更新进度"""
        if index < self.table.rowCount():
            progress_bar = self.table.cellWidget(index, 3)
            if progress_bar:
                progress_bar.setValue(percent)
            
            status_item = self.table.item(index, 5)
            if status_item:
                status_item.setText(status)
                status_item.setForeground(QColor("#007AFF"))
        
        # 更新总进度
        total = len(self.files)
        if total > 0:
            overall = int((index * 100 + percent) / total)
            self.total_progress.setValue(overall)
            lang = get_lang()
            if lang == 'zh':
                self.progress_label.setText(f"处理中 {index + 1}/{total}")
            else:
                self.progress_label.setText(f"Processing {index + 1}/{total}")
    
    def on_file_done(self, index, success, output_size):
        """单个文件完成"""
        if index < self.table.rowCount():
            progress_bar = self.table.cellWidget(index, 3)
            status_item = self.table.item(index, 5)
            out_item = self.table.item(index, 4)
            
            if success:
                if progress_bar:
                    progress_bar.setValue(100)
                
                if out_item:
                    out_item.setText(self.fmt(output_size))
                
                if status_item:
                    # 计算压缩比
                    in_size = self.files[index]['size']
                    diff = in_size - output_size
                    if in_size > 0:
                        ratio = abs(diff) / in_size * 100
                        if diff > 0:
                            status_item.setText(f"-{ratio:.0f}%")
                            status_item.setForeground(QColor("#34c759"))
                        else:
                            status_item.setText(f"+{ratio:.0f}%")
                            status_item.setForeground(QColor("#ff9500"))
                    else:
                        status_item.setText("OK")
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
    
    def on_all_done(self, completed, total, input_size, output_size):
        """全部完成"""
        self.total_progress.setValue(100)
        lang = get_lang()
        if lang == 'zh':
            self.progress_label.setText(f"完成 {completed}/{total}")
        else:
            self.progress_label.setText(f"Done {completed}/{total}")
        
        # 恢复控件
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.encoder_combo.setEnabled(True)
        self.quality_combo.setEnabled(True)
        
        enc_name = self.encoder_combo.currentText()
        if enc_name in self.encoders:
            has_preset = self.encoders[enc_name].get('has_preset', False)
            self.speed_combo.setEnabled(has_preset)
        
        self.resolution_combo.setEnabled(True)
        
        # 显示结果弹窗
        if completed > 0:
            dialog = ResultDialog(self, completed, total, input_size, output_size)
            dialog.exec()


# ============ 主函数 ============
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName(tr('app_title'))
    app.setOrganizationName("SheCan")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
