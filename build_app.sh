#! /bin/bash

# Build macOS X version of wxVLCPlayer app

source `which virtualenvwrapper.sh`
workon vlc3

if [[ $# == 1 ]] && [[ $1 == "-incr" ]]; then
  echo "Increment build number"
  python increment_version.py
fi

python setup.py py2app
deactivate
