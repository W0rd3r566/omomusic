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
        # Reuse the original omo Compose home component rather than just rebadging InterTune.
        ui_root = Path("app/src/main/java/com/dd3boh/outertune/ui")
        old_hero = ROOT / "client" / ui_root / "omo/OmoHero.kt"
        new_hero = DEST / ui_root / "omo/OmoHero.kt"
        new_hero.parent.mkdir(parents=True, exist_ok=True)
        hero = old_hero.read_text(encoding="utf-8")
        hero = hero.replace(
            "import androidx.compose.material3.Text\n",
            "import androidx.compose.material3.Text\nimport androidx.compose.material3.TextButton\n"
        )
        hero = hero.replace(
            "import com.dd3boh.outertune.R\n",
            "import com.dd3boh.outertune.R\n"
            "import com.dd3boh.outertune.constants.InnerTubeCookieKey\n"
            "import com.dd3boh.outertune.utils.rememberPreference\n"
        )
        hero = hero.replace(
            "fun OmoHero(navController: NavController) {",
            "fun OmoHero(navController: NavController) {\n"
            '    val (loginCookie) = rememberPreference(InnerTubeCookieKey, defaultValue = "")'
        )
        marker = "            }\n        }\n    }\n}\n"
        if marker not in hero:
            raise RuntimeError("Original omo hero layout changed")
        hero = hero.replace(marker, '''            }
            TextButton(
                onClick = {
                    navController.navigate(if (loginCookie.isBlank()) "login" else "account")
                },
            ) {
                Text(
                    text = stringResource(
                        if (loginCookie.isBlank()) R.string.login else R.string.account
                    ),
                )
            }
        }
    }
}
''', 1)
        new_hero.write_text(hero, encoding="utf-8")

        for locale in ("values", "values-ru"):
            source_strings = ROOT / "client/app/src/main/res" / locale / "omo_strings.xml"
            target_strings = DEST / "app/src/main/res" / locale / "omo_strings.xml"
            target_strings.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_strings, target_strings)

        home = DEST / ui_root / "screens/HomeScreen.kt"
        text = home.read_text(encoding="utf-8")
        needle = "import com.dd3boh.outertune.LocalPlayerAwareWindowInsets"
        if needle not in text:
            raise RuntimeError("InterTune HomeScreen imports have changed")
        text = text.replace(needle, needle + "\nimport com.dd3boh.outertune.ui.omo.OmoHero")
        needle = '            item(key = "tiles", contentType = "tiles") {'
        if needle not in text:
            raise RuntimeError("InterTune HomeScreen feed layout changed")
        text = text.replace(
            needle,
            '            item(key = "omo-hero", contentType = "omo-hero") {\n'
            '                OmoHero(navController)\n'
            '            }\n' + needle
        )
        home.write_text(text, encoding="utf-8")

        (DEST / "UPSTREAM.md").write_text(
            "# Source attribution\n\n"
            "The YouTube Music engine is InterTune " + TAG + " at commit " + commit +
            " (https://github.com/ItzSkyeYT/InterTune). InterTune is a fork of "
            "OuterTune/InnerTune. Original source copyright and LICENSE files "
            "are retained. omo Music changes application identity and artwork. "
            "Licensing: GPL-3.0.\n", encoding="utf-8"
        )
        (DEST / "README.md").write_text(
            "# omo Music 0.2.0\n\n"
            "A native Kotlin / Jetpack Compose Android client with YouTube Music "
            "search, streaming, library and background playback provided by "
            "InterTune v0.12.11.\n\n"
            "## Google account\n\n"
            "Open the Home card and tap Sign in, or open Account in the app. "
            "The app uses Android's Google account picker (where available) "
            "and Google's sign-in page in WebView, retaining the authenticated "
            "YouTube Music session cookie. This is not official Google OAuth. "
            "Google can decline embedded browser sign-in; no passwords should "
            "be supplied outside Google's verified site.\n\n"
            "## Build\n\n"
            "JDK 21, Android SDK 36, NDK 29.0.13113456 and CMake 3.31.6.\n\n"
            "    ./gradlew :app:assembleCoreDebug\n\n"
            "Choose an arm64-v8a or universal APK for a Pixel 9a. Device runtime "
            "and account sign-in require testing; compiling is not proof.\n\n"
            "GPL-3.0 source attribution: see UPSTREAM.md and LICENSE.\n",
            encoding="utf-8",
        )
        print("Imported InterTune", TAG, commit)

if __name__ == "__main__":
    main()
