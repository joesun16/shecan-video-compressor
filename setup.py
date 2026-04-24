from setuptools import setup

APP = ['video_compressor.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'EllaPuede视频压缩工具',
        'CFBundleDisplayName': 'EllaPuede视频压缩工具',
        'CFBundleIdentifier': 'com.ellapuede.videocompressor',
        'CFBundleVersion': '3.0',
        'CFBundleShortVersionString': '3.0',
        'NSHighResolutionCapable': True,
    },
    'packages': ['PyQt6'],
    'includes': ['PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
