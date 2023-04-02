#! /bin/bash

# Adapt this for creating an app icon set
# https://stackoverflow.com/questions/12306223/how-to-manually-create-icns-files-using-iconutil

mkdir MyIcon.iconset
sips -z 16 16     logo-512.png --out MyIcon.iconset/icon_16x16.png
sips -z 32 32     logo-512.png --out MyIcon.iconset/icon_16x16@2x.png
sips -z 32 32     logo-512.png --out MyIcon.iconset/icon_32x32.png
sips -z 64 64     logo-512.png --out MyIcon.iconset/icon_32x32@2x.png
sips -z 128 128   logo-512.png --out MyIcon.iconset/icon_128x128.png
sips -z 256 256   logo-512.png --out MyIcon.iconset/icon_128x128@2x.png
sips -z 256 256   logo-512.png --out MyIcon.iconset/icon_256x256.png
sips -z 512 512   logo-512.png --out MyIcon.iconset/icon_256x256@2x.png
sips -z 512 512   logo-512.png --out MyIcon.iconset/icon_512x512.png
# In the original script, the base icon was 1024x1024. The online
# icon creator couldn't produce a 1024x1024 file, so 512x512 had to be used.
# See https://www.iconfinder.com/search/?q=icns%20file
cp logo-512.png MyIcon.iconset/icon_512x512@2x.png

iconutil -c icns MyIcon.iconset
cp MyIcon.icns wx_vlc_player.icns
rm -R MyIcon.iconset
rm MyIcon.icns