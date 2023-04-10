# ![wxVLCPlayer Logo](resources/wx_vlc_player.gif) wxVLCPlayer = Python + wxPython + python-vlc
© 2023 by Dave Hocker

## Contents
* [Overview](#overview)
* [Running the App](#running-the-app)
* [User Interface](#user-interface)
* [References](#references)

## Overview <a id="overview"></a>
wxVLCPlayer is a simple media player based on Python, [wxPython](https://www.wxpython.org/) 
and [libVLC](https://www.videolan.org/vlc/libvlc.html). 
It was originally intended to be a simple MP3 player for macOS, but it can play most media supported by libVLC (including video files like .mp4).

## License

This project is licensed under the GNU General Public License v3 as published 
by the Free Software Foundation, Inc..
See the LICENSE.md file for the full text of the license.

## Running the App <a id="running-the-app"></a>
### As a macOS App
The current version of wxVLCPlayer.app can be found in the releases section (as a zip file). Download
the zip file for your machine's architecture, unzip it and move wxVLCPlayer.app to the 
/Users/your-user-name/Applications folder. Then, run the wxVLCPlayer.app. You will have to go 
through the gatekeeper hurdles to get it to run.

### From Source
#### Requirements
You can use a virtual environment (hightly recommended) or you can install the 
requirements to the system Python 3. Virtual environments is out of the scope of
this discussion, but you can find out more from the [references](#references).

```
cd wx_vlc_player
pip install -r requirements.txt
```

Using this technique, you can run the app from its source directory.

```
cd wx_vlc_player
python3 wx_vlc_player.py
```
    
Or, you can build wxVLCPlayer.app by running the build_app.sh script file.

```
cd wx_vlc_player
./build_app.sh
```

## User Interface <a id="user-interface"></a>
The user interface is based on a playlist and player transport. A playlist is a standard .m3u file created with a text editor or another app like VLC. You can create a playlist with a text editor by simply adding
lines where each line is the full path to a media file.

For example, an example.m3u might look like this.

```
/Users/username/Music/artist/track1.mp3
/Users/username/Music/artist/track2.mp3
/Users/username/Music/artist/track3.mp3
```

Once you have loaded a playlist you can start a track by pressing the play button or double clicking
on the track.

## References <a id="references"></a>
* [wxPython](https://www.wxpython.org/)
* [libVLC](https://www.videolan.org/vlc/libvlc.html)
* [virtualenv on pypi](https://virtualenv.pypa.io/en/latest/)
* [virtualenvwrapper read-the-docs](https://virtualenvwrapper.readthedocs.io/en/latest/)
