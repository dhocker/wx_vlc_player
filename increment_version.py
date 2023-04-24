#
# increment_version.py - increment the build version
#

import json

fh = open("version.json", "r")
version = json.load(fh)
fh.close()

version["build"] = version["build"] + 1

fh = open("version.json", "w")
json.dump(version, fh)
fh.close()

fh = open("version.py", "w")
fh.write(f"version = \"{version['major']}.{version['minor']}.{version['patch']}.{version['build']}\"\n")

print(version)
