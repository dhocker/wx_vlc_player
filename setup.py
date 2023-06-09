"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app

https://bitbucket.org/ronaldoussoren/py2app/issues/219/new-mach-o-header-is-too-large-to-relocate
"""

from setuptools import setup

APP = ['wx_vlc_app.py']
DATA_FILES = [
    ("images", [
        "resources/wx_vlc_player.gif",
        "resources/next-track-2.png",
        "resources/pause.png",
        "resources/play-solid.png",
        "resources/previous-track-2.png",
        "resources/stop.png",
        "resources/muted.png",
        "resources/unmuted.png",
        "resources/random.png"
    ])
]
OPTIONS = {
    "iconfile": "resources/wx_vlc_player.icns",
    "packages": ["PIL"]
}

setup(
    app=APP,
    name="wxVLCPlayer",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
