#! /bin/bash

# Build macOS X version of pyid3tag app

source `which virtualenvwrapper.sh`
workon vlc3
python increment_version.py
python setup.py py2app
deactivate
