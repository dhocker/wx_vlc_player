#! python3
#
# increment_version.py - increment the build version
#
# command syntax
#   increment_version.py {major | minor | patch | build}
# The default is to increment the build number
#

import sys
import json

# Load the current version
fh = open("version.json", "r")
version = json.load(fh)
fh.close()

# Update the version
if len(sys.argv) == 2:
    # Accept major, minor, patch or build for the argument
    print(f"Incrementing: {sys.argv[1]}")
    if sys.argv[1] in ["major", "minor", "patch", "build"]:
        if sys.argv[1] == "major":
            version["major"] += 1
            version["minor"] = 0
            version["patch"] = 0
            version["build"] = 0
        elif sys.argv[1] == "minor":
            version["minor"] += 1
            version["patch"] = 0
            version["build"] = 0
        elif sys.argv[1] == "patch":
            version["patch"] += 1
            version["build"] = 0
        else:
            # It has to be build
            version["build"] += 1
    else:
        print(f"{sys.argv[i]} is not a recognized version component")
        exit(1)
elif len(sys.argv) == 1:
    # The default is to increment the build number
    version["build"] = version["build"] + 1
else:
    print("Command syntax:")
    print("increment_version.py {major | minor | patch | build}")
    exit(2)

# Save the new version
fh = open("version.json", "w")
json.dump(version, fh)
fh.close()

fh = open("version.py", "w")
fh.write(f"version = \"{version['major']}.{version['minor']}.{version['patch']}.{version['build']}\"\n")

print(version)
