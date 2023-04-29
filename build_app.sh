#! /bin/bash

# Build macOS X version of wxVLCPlayer app

source `which virtualenvwrapper.sh`
workon vlc3

if [[ $# == 1 ]] && [[ $1 == "-incr" ]]; then
  python increment_version.py build
fi

python setup.py py2app
deactivate
