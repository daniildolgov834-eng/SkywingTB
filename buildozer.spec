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
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp3,wav,ogg,mp4,ico,webm,json,txt

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,bak

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = build,dist,.git,__pycache__

# (str) Application versioning (method 1)
version = 3.4.2

# (list) Application requirements
# pygame==2.1.3 is the most stable version for python-for-android
requirements = python3,kivy==2.1.0,pygame==2.1.3,numpy,pyjnius,android

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

# (str) Android entry point, default is ok for Kivy-based app
# android.entrypoint = org.renpy.android.PythonActivity

# (list) Pattern to whitelist for the android application
# android.whitelist =

# (str) Path to a custom whitelist file
# android.whitelist_src =

# (str) Path to a custom blacklist file
# android.blacklist_src =

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 24

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 24

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) The Android arch to build for
android.archs = arm64-v8a, armeabi-v7a

# (str) The Android SDK path
# android.sdk_path =

# (str) The Android NDK path
# android.ndk_path =

# (list) The Android Activity fullscreen flag
# android.fullscreen = 1

# (str) Android app theme
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (str) Android theme color
# android.theme_color = #000000

# (str) Android presplash color
# android.presplash_color = #000000

# (str) Android permissions
# android.permissions = INTERNET

# (str) Android ABI to build for
# android.archs = arm64-v8a, armeabi-v7a

# (str) Android build type (release/debug)
# android.debug_artifact = apk

# (str) Android release keystore
# android.release_artifact = aab

# (str) Android app version
# android.numeric_version = 1

# (str) Android adaptive icon
# android.adaptive_icon = (None)

# (list) Android adaptive icon background and foreground
# android.adaptive_icon_background =
# android.adaptive_icon_foreground =

# (list) Android extra permissions
# android.extra_permissions =

# (list) Android extra manifest entries
# android.extra_manifest_entries =

# (str) Android meta-data entries
# android.meta_data =

# (str) Android intent filters
# android.intent_filters =

# (str) Android services
# android.services =

# (str) Android build resources
# android.resources =

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run in a virtual env
warn_on_root = 1
