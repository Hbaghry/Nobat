[app]
title = Nobat
package.name = nobat
package.domain = ir.nobat

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,otf,json
source.include_patterns = fonts/*,assets/*

version = 1.0.0

requirements = python3,kivy==2.3.0,pillow,pyjnius,arabic-reshaper,python-bidi,jdatetime

orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,WRITE_EXTERNAL_STORAGE,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

android.versionCode = 1

android.logcat_filters = *:S python:D
android.debug = 1
android.enable_androidx = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1