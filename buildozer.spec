[app]

# Nom de l'application
title = Presidence

# Nom du package
package.name = presidence
package.domain = org.scoremille

# Dossier source
source.dir = .
source.include_exts = py,png,jpg,kv,json,txt,atlas

# Version
version = 0.2

# Dépendances
requirements = python3,kivy

# Orientation
orientation = portrait

# Plein écran
fullscreen = 1

# Android
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Autorisations (nécessaires pour sauvegarde locale)
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Optimisation
android.allow_backup = True

# Optionnel (si tu ajoutes plus tard)
# icon.filename = icon.png
# presplash.filename = presplash.png


[buildozer]

log_level = 2
warn_on_root = 1