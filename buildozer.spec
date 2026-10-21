[app]

# (str) Title of your application
title = Skywing

# (str) Package name
package.name = skywing

# (str) Package domain (needed for android/ios packaging)
package.domain = org.skywing

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp3,wav,ogg,ico,webm,json,txt

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,bak

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = build,dist,.git,__pycache__,tv_tapes,tv_videos

# (str) Application versioning (method 1)
version = 3.4.2

# (list) Application requirements
# We pin numpy to a stable version and removed opencv and cython for stability
requirements = python3,kivy==2.1.0,pygame==2.1.3,numpy==1.23.5,pyjnius,android

# (str) Presplash of the Application
# presplash.filename = %(source.dir)s/icons/game_icon.png

# (str) Icon of the Application
icon.filename = %(source.dir)s/icons/game_icon.png

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 24

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use.
android.ndk_api = 24

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) The Android arch to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Accept licenses automatically
android.accept_sdk_license = True

# (bool) Skip update of SDK/NDK
android.skip_update = False

# (str) Android entry point
# android.entrypoint = org.renpy.android.PythonActivity

# (list) Pattern to whitelist for the android application
# android.whitelist =

# (str) Path to a custom whitelist file
# android.whitelist_src =

# (str) Path to a custom blacklist file
# android.blacklist_src =

# (list) Android extra permissions
# android.extra_permissions =

# (list) Android extra manifest entries
# android.extra_manifest_entries =

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run in a virtual env
warn_on_root = 1
