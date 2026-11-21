#!/usr/bin/env python3
"""Import a YouTube Music-capable, GPL-3.0 Kotlin engine for omo Music.

OuterTune 0.11.x is local-only. InterTune 0.12.11 is used instead.
This script is a one-time importer and never overwrites project edits.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "client-next"
UPSTREAM = "https://github.com/ItzSkyeYT/InterTune.git"
TAG = "v0.12.11"

def replace(file, original, replacement):
    text = file.read_text(encoding="utf-8")
    if original not in text:
        raise RuntimeError("Could not find expected content in " + str(file) + ": " + original)
    file.write_text(text.replace(original, replacement), encoding="utf-8")

def main():
    if DEST.exists():
        raise SystemExit("client-next already exists; refusing to overwrite sources")
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp) / "intertune"
        subprocess.run(
            ["git", "clone", "--depth", "1", "--recurse-submodules", "--shallow-submodules",
             "--branch", TAG, UPSTREAM, str(source)],
            check=True,
        )
        commit = subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip()
        DEST.mkdir(parents=True)
        for folder in (
            "app", "innertube", "sabr", "kugou", "lrclib", "lastfm",
            "fingerprint", "material-color-utilities", "ffMetadataEx",
            "taglib", "innertubex", "gradle", "prebuilt",
        ):
            path = source / folder
            if path.is_dir():
                shutil.copytree(path, DEST / folder, ignore=shutil.ignore_patterns(
                    ".git", ".gradle", "build", ".idea", "*.apk", "*.aab"
                ))
        for file in (
            "gradlew", "gradlew.bat", "settings.gradle.kts",
            "build.gradle.kts", "gradle.properties", "LICENSE",
            ".gitignore", "services.properties",
        ):
            path = source / file
            if path.is_file():
                shutil.copy2(path, DEST / file)

        replace(DEST / "settings.gradle.kts",
                'rootProject.name = "OuterTune"', 'rootProject.name = "omoMusic"')
        app = DEST / "app/build.gradle.kts"
        replace(app, 'applicationId = "dev.skye.intertune"',
                'applicationId = "dev.w0rd3r.omomusic"')
        replace(app, 'versionName = "0.12.11"', 'versionName = "0.2.0"')
        replace(app, 'versionCode = 103', 'versionCode = 2')
        replace(app, 'var outputFileName = "InterTune-', 'var outputFileName = "omoMusic-')
        replace(DEST / "app/src/main/res/values/app_name.xml",
                'name="app_name">InterTune<', 'name="app_name">omo Music<')
        replace(DEST / "app/src/debug/res/values/app_name.xml",
                "InterTune Debug", "omo Music Debug")

        drawable = DEST / "app/src/main/res/drawable"
        omo_assets = ROOT / "patches/src/main/resources/omo/drawable"
        shutil.copy2(omo_assets / "omo_foreground.xml", drawable / "launcher_foreground.xml")
        shutil.copy2(omo_assets / "omo_monochrome.xml", drawable / "launcher_monochrome.xml")
        replace(DEST / "app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml",
                "@color/ic_launcher_background", "@android:color/black")
        replace(
            DEST / "app/src/main/java/com/dd3boh/outertune/ui/theme/Theme.kt",
            "val DefaultThemeColor = Color(0xFFED5564)",
            "val DefaultThemeColor = Color(0xFFA7D7FF)",
        )
        (DEST / "UPSTREAM.md").write_text(
            "# Source attribution\n\n"
            "The YouTube Music engine is InterTune " + TAG + " at commit " + commit +
            " (https://github.com/ItzSkyeYT/InterTune). InterTune is a fork of "
            "OuterTune/InnerTune. Original source copyright and LICENSE files "
            "are retained. omo Music changes application identity and artwork. "
            "Licensing: GPL-3.0.\n", encoding="utf-8"
        )
        print("Imported InterTune", TAG, commit)

if __name__ == "__main__":
    main()
