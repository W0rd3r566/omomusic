#!/usr/bin/env python3
"""Rebrand the imported GPL-3.0 Metrolist Android source as omo Music.

Only change known integration points. Fail loudly if upstream changes instead of
silently shipping a Metrolist-branded APK or breaking its Kotlin package names.
"""
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "native"
APP = NATIVE / "androidApp"
SHARED = NATIVE / "shared"


def replace_exact(relative, old, new):
    path = NATIVE / relative
    data = path.read_text(encoding="utf-8")
    occurrences = data.count(old)
    if occurrences == 0:
        raise RuntimeError(f"{relative}: upstream marker not found: {old!r}")
    path.write_text(data.replace(old, new), encoding="utf-8")
    print(f"Updated {relative}: {occurrences} occurrence(s)")


def main():
    if not APP.is_dir() or not SHARED.is_dir():
        raise SystemExit("First import the upstream Android sources into native/.")

    replace_exact("settings.gradle.kts", 'rootProject.name = "Metrolist"', 'rootProject.name = "omo Music"')
    # The project is Android-first; omit the unused desktop module from Gradle.
    settings = NATIVE / "settings.gradle.kts"
    settings.write_text(settings.read_text().replace('include(":desktopApp")', ""), encoding="utf-8")

    replace_exact("androidApp/build.gradle.kts",
                  'applicationId = "com.metrolist.music"',
                  'applicationId = "dev.w0rd3r.omomusic"')
    replace_exact("androidApp/build.gradle.kts",
                  'manifestPlaceholders["appLabel"] = "Metrolist KMP Debug"',
                  'manifestPlaceholders["appLabel"] = "omo Music (debug)"')
    replace_exact("androidApp/build.gradle.kts",
                  'manifestPlaceholders["appLabel"] = "Metrolist"',
                  'manifestPlaceholders["appLabel"] = "omo Music"')
    # Do not fetch/install official Metrolist releases as updates for omo.
    replace_exact("androidApp/build.gradle.kts",
                  'buildConfigField("Boolean", "UPDATER_ENABLED", "true")',
                  'buildConfigField("Boolean", "UPDATER_ENABLED", "false")')
    # Original Discord app ID is owned by the upstream project.
    build_file = APP / "build.gradle.kts"
    build_text = build_file.read_text(encoding="utf-8")
    build_text, count = re.subn(
        r'buildConfigField\("Long", "DISCORD_APP_ID", "\d+L"\)',
        'buildConfigField("Long", "DISCORD_APP_ID", "0L")',
        build_text
    )
    if count != 1:
        raise RuntimeError("Could not disable upstream Discord application ID.")
    build_file.write_text(build_text, encoding="utf-8")

    # First-run defaults. All remain changeable in the existing Appearance UI.
    preferences = "shared/src/commonMain/kotlin/com/metrolist/shared/settings/Settings.kt"
    for old, new in (
        ("var dynamicTheme by preference(true)", "var dynamicTheme by preference(false)"),
        ("var themeMode by preference(ThemeMode.AUTO)", "var themeMode by preference(ThemeMode.PURE_BLACK)"),
        ("var selectedThemeColor by preference(0L)", "var selectedThemeColor by preference(0xFFA7D7FFL)"),
        ("var animatedGradient by preference(true)", "var animatedGradient by preference(false)"),
    ):
        replace_exact(preferences, old, new)

    # Reuse the user's original logo, which is already present in the ReVanced patches.
    source = ROOT / "patches/src/main/resources/omo/drawable"
    dest = APP / "src/main/res/drawable"
    for original, target in (
        ("omo_foreground.xml", "ic_launcher_foreground.xml"),
        ("omo_monochrome.xml", "ic_launcher_monochrome.xml"),
    ):
        ET.parse(source / original)
        shutil.copy2(source / original, dest / target)

    background = dest / "app_icon_original_background.xml"
    background.write_text(
        '<vector xmlns:android="http://schemas.android.com/apk/res/android" '
        'android:width="108dp" android:height="108dp" '
        'android:viewportWidth="108" android:viewportHeight="108">'
        '<path android:fillColor="#FF000000" '
        'android:pathData="M0,0h108v108h-108z"/></vector>\n',
        encoding="utf-8"
    )

    # Replace user-facing names only in translation catalogs, not Kotlin
    # package names or API endpoints. Existing translations remain available.
    catalog_root = SHARED / "src/commonMain/composeResources"
    edited = 0
    for path in catalog_root.rglob("strings.xml"):
        if path.parent.name.startswith("values"):
            original = path.read_text(encoding="utf-8")
            rewritten = original.replace("Metrolist", "omo Music")
            if rewritten != original:
                path.write_text(rewritten, encoding="utf-8")
                edited += 1
    print(f"Updated visible product name in {edited} translation catalogs")
    print("omo Music branding and editable Material 3 Expressive defaults applied.")


if __name__ == "__main__":
    main()
