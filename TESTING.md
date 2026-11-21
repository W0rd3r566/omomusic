# Testing and limitations

1. `python3 scripts/check_assets.py` verifies every committed vector/adaptive icon XML and patch-resource references.
2. `./gradlew build` resolves the ReVanced patch Gradle plugin and compiles the patch bundle.
3. Android runtime validation of any patched APK remains separate. This repository intentionally ships **no YouTube Music APK**, does not sign or distribute one, and does not promise all application versions are supported.

The launcher icon includes an Android 26+ adaptive/masked version, a monochrome layer for Android 13+, and a vector drawable fallback.

The Pixel 9a cannot be validated via GitHub Actions; actual login, app-package coexistence and playback must be checked using a permitted local installation. No subscription/DRM functionality is modified.
