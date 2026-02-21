# Nom de l'application
title = Presidence

# Package (important : tout en minuscule)
package.name = presidence
package.domain = org.scoremille

# Dossier source
source.dir = .
source.include_exts = py,png,jpg,kv,json,txt,atlas

# Version
version = 0.2

# Dépendances
requirements = python3,kivy

# Orientation écran
orientation = portrait

# Plein écran
fullscreen = 1

# --- Configuration Android STABLE (corrige ton erreur GitHub) ---
android.api = 31
android.minapi = 21
android.sdk = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

# Permissions pour sauvegarde
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Optionnel (tu peux ajouter plus tard)
# icon.filename = icon.png
# presplash.filename = presplash.png


[buildozer]

log_level = 2
warn_on_root = 1
