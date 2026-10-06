[app]

title = Nobat
package.name = nobat
package.domain = ir.nobat

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf

version = 1.0

requirements = python3,kivy,pillow,jdatetime,arabic-reshaper,python-bidi

orientation = portrait
fullscreen = 0

android.api = 34
android.minapi = 23
android.archs = arm64-v8a

android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

[buildozer]

log_level = 2
warn_on_root = 1
