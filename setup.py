from setuptools import setup

APP = ['video_compressor.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'SheCan视频压缩工具',
        'CFBundleDisplayName': 'SheCan视频压缩工具',
        'CFBundleIdentifier': 'com.shecan.videocompressor',
        'CFBundleVersion': '2.7',
        'CFBundleShortVersionString': '2.7',
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
