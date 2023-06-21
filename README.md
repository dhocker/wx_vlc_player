# ![wxVLCPlayer Logo](resources/wx_vlc_player.gif) wxVLCPlayer<p><b>Python + wxPython + python-vlc</b></p>

**© 2023 by Dave Hocker (athomex10@gmail.com)**

## Contents
* [Overview](#overview)
* [Running the App](#running-the-app)
* [User Interface](#user-interface)
* [References](#references)

## Overview <a id="overview"></a>
wxVLCPlayer is a simple media player based on Python, [wxPython](https://www.wxpython.org/) 
and [libVLC via python-vlc](https://www.videolan.org/vlc/libvlc.html). 
It was originally intended to be a simple MP3 player for macOS, but it can play most media supported 
by libVLC. The following list covers the more common media files.

* .mp3
* .wav
* .aac
* .mp4
* .mkv

wxVLCPlayer also supports nested .m3u playlist files. That is, a .m3u can include
other .m3u files. Beware of recursion!

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
You can use a virtual environment (highly recommended) or you can install the 
requirements to the system Python 3. Virtual environments is out of the scope of
this discussion, but you can find out more from the [references](#references).

```
cd wx_vlc_player
pip install -r requirements.txt
```

if you are using virtualenv/virtualenvwrapper, you can do the following.

```
cd wx_vlc_player
mkvirtualenv -p python3 -r requirements.txt venv-name
```
The choice of venv-name is yours.

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
The user interface is based on a playlist and player transport. 
A playlist file is a standard .m3u file created with wxVLCPlayer, a text editor or another app like VLC. 
You can create a playlist file with a text editor by simply adding
lines where each line is the full path to a media file. The active playlist can contain
one or more playlist files.

For example, an example.m3u might look like this.

```
/Users/username/Music/artist/track1.mp3
/Users/username/Music/artist/track2.mp3
/Users/username/Music/artist/track3.mp3
```

Once you have loaded one or more playlist files you can start a track by pressing 
the play button or double-clicking on the track.

### Using the Menu Bar

#### Adding Playlist Files to the Playlist
Use the **Playlist | Add/Append** menu item to select one or more playlist files
to be added to the end of the playlist.

#### Adding Media Files to the Playlist
Use the **Edit | Add files** menu item to select one or more media files
to be added to the end of the playlist.

#### Play a Media File
To play a media file, click on the item and then click the Play button. Or, simply 
double-click the item.

#### Saving the Playlist as a Playlist File
Use the **Playlist | Save playlist** menu item to save the current playlist 
in the **last loaded** playlist file (as shown in the playlist title).
Use the **Playlist | Save playlist as** menu item to save the current playlist in
a new playlist file.

#### Delete Playlist Items
Use the **Edit | Delete from playlist** menu item to delete all selected playlist items.

#### Clearing the Playlist
Use the **Edit | Clear playlist** menu item to remove all of the items from the current playlist.

### Using Drag and Drop

Drag and Drop (DnD) can be used is two ways.

1. You can drag files from Finder, Explorer or File Manager and drop them onto the playlist.
2. You can manipulate the playlist by dragging and dropping rows (files) of the playlist.

#### DnD from Finder, Explorer or File Manager

To DnD files, select one or more from your file manager app and drop them onto the playlist.
The files will be dropped in front of the playlist row where you release the mouse button.
All supported media files and playlist (.m3u) files can by DnDed this way.

#### DnD within the Playlist

You can use DnD to order the playlist. Simply scatter-select rows to be moved.
Drag them to the row where you want to insert them. The rows will be moved
in front of the row you are on when you release the mouse button.

## References <a id="references"></a>
* [wxPython](https://www.wxpython.org/)
* [libVLC](https://www.videolan.org/vlc/libvlc.html)
* [virtualenv on pypi](https://virtualenv.pypa.io/en/latest/)
* [virtualenvwrapper read-the-docs](https://virtualenvwrapper.readthedocs.io/en/latest/)
