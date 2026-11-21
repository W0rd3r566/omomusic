#!/usr/bin/env python3
"""One-time source import for omo Music Android.

The Android player is based on OuterTune (GPL-3.0), with a distinct application
ID, original omo artwork, original home header and graphite Material 3 skin.
No Google or YouTube application binaries are copied or patched.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "client"
SOURCE_URL = "https://github.com/OuterTune/OuterTune.git"
SOURCE_SHA = "1b91406d758a95271e53c44ddfd9ce88b50a904e"

def must_replace(path: Path, old: str, new: str) -> None:
    content = path.read_text()
    if old not in content:
        raise RuntimeError(f"Expected text missing from {path}: {old!r}")
    path.write_text(content.replace(old, new))

def add_import(path: Path, source: str, addition: str) -> None:
    must_replace(path, source, source + "\n" + addition)

def main() -> None:
    if DEST.exists():
        raise SystemExit("client/ already exists; refusing to overwrite source changes")
    with tempfile.TemporaryDirectory(prefix="omo-outertune-") as temp:
        cloned = Path(temp) / "OuterTune"
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", "lite", SOURCE_URL, str(cloned)],
            check=True,
        )
        actual_sha = subprocess.check_output(["git", "-C", str(cloned), "rev-parse", "HEAD"], text=True).strip()
        if actual_sha != SOURCE_SHA:
            # Fetch the exact audited revision, rather than silently moving upstream.
            subprocess.run(["git", "-C", str(cloned), "fetch", "--depth", "1", "origin", SOURCE_SHA], check=True)
            subprocess.run(["git", "-C", str(cloned), "checkout", "--detach", SOURCE_SHA], check=True)
            actual_sha = SOURCE_SHA

        DEST.mkdir(parents=True)
        for directory in ("app", "material-color-utilities", "gradle"):
            shutil.copytree(cloned / directory, DEST / directory,
                            ignore=shutil.ignore_patterns(".git", "build", ".gradle", ".idea"))
        for filename in ("gradlew", "gradlew.bat", "settings.gradle.kts", "build.gradle.kts",
                         "gradle.properties", "LICENSE", ".gitignore"):
            file = cloned / filename
            if file.exists():
                shutil.copy2(file, DEST / filename)

        must_replace(DEST / "settings.gradle.kts", 'rootProject.name = "OuterTune"', 'rootProject.name = "omoMusic"')
        app_build = DEST / "app/build.gradle.kts"
        must_replace(app_build, "    compileSdk = 37",
                     "    compileSdk {\n        version = release(37) {\n            minorApiLevel = 0\n        }\n    }")
        must_replace(app_build, "        targetSdk = 37", "        targetSdk = 36")
        must_replace(app_build, 'applicationId = "com.dd3boh.outertune"', 'applicationId = "dev.w0rd3r.omomusic"')
        must_replace(app_build, 'versionCode = 73', 'versionCode = 1')
        must_replace(app_build, 'versionName = "0.11.1"', 'versionName = "0.1.0"')
        must_replace(app_build, 'var outputFileName = "OuterTune-', 'var outputFileName = "omoMusic-')
        must_replace(DEST / "app/src/main/res/values/app_name.xml", "OuterTune Lite", "omo Music")
        must_replace(DEST / "app/src/debug/res/values/app_name.xml", "OuterTune Debug", "omo Music Debug")

        main_activity = DEST / "app/src/main/java/com/dd3boh/outertune/MainActivity.kt"
        must_replace(main_activity, 'rememberPreference(DynamicThemeKey, defaultValue = true)',
                     'rememberPreference(DynamicThemeKey, defaultValue = false)')
        must_replace(main_activity, 'rememberEnumPreference(DarkModeKey, defaultValue = DarkMode.AUTO)',
                     'rememberEnumPreference(DarkModeKey, defaultValue = DarkMode.ON)')
        must_replace(main_activity, 'rememberPreference(PureBlackKey, defaultValue = false)',
                     'rememberPreference(PureBlackKey, defaultValue = true)')

        # Preserve OuterTune implementation and all upstream copyright notices.
        theme = DEST / "app/src/main/java/com/dd3boh/outertune/ui/theme/Theme.kt"
        must_replace(theme, 'val DefaultThemeColor = Color(0xFFED5564)', 'val DefaultThemeColor = Color(0xFFA7D7FF)')
        add_import(theme, 'import androidx.compose.material3.MaterialTheme',
                   'import androidx.compose.material3.darkColorScheme\n'
                   'import androidx.compose.material3.Shapes\n'
                   'import androidx.compose.foundation.shape.RoundedCornerShape\n'
                   'import androidx.compose.ui.unit.dp')
        must_replace(theme,
                     'val colorScheme = remember(darkTheme, pureBlack, themeColor) {',
                     'val colorScheme = remember(darkTheme, pureBlack, themeColor, enableDynamicTheme) {')
        must_replace(theme,
                     'if (themeColor == DefaultThemeColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {',
                     '''if (!enableDynamicTheme && darkTheme) {
            darkColorScheme(
                primary = Color(0xFFA7D7FF),
                onPrimary = Color(0xFF00344D),
                primaryContainer = Color(0xFF17465D),
                onPrimaryContainer = Color(0xFFD0EAFF),
                secondary = Color(0xFFB9C8D3),
                background = Color(0xFF000000),
                onBackground = Color(0xFFF1F3F6),
                surface = Color(0xFF000000),
                onSurface = Color(0xFFF1F3F6),
                surfaceContainer = Color(0xFF16191E),
                surfaceContainerLow = Color(0xFF0E1014),
                surfaceContainerHigh = Color(0xFF22262C),
                surfaceContainerHighest = Color(0xFF2B3038),
                outline = Color(0xFF737D89),
            )
        } else if (themeColor == DefaultThemeColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {''')
        must_replace(theme,
                     'typography = MaterialTheme.typography,\n        content = content',
                     '''typography = MaterialTheme.typography,
        shapes = Shapes(
            small = RoundedCornerShape(12.dp),
            medium = RoundedCornerShape(20.dp),
            large = RoundedCornerShape(28.dp),
            extraLarge = RoundedCornerShape(36.dp),
        ),
        content = content''')

        foreground = ROOT / "patches/src/main/resources/omo/drawable/omo_foreground.xml"
        monochrome = ROOT / "patches/src/main/resources/omo/drawable/omo_monochrome.xml"
        drawable = DEST / "app/src/main/res/drawable"
        shutil.copy2(foreground, drawable / "launcher_foreground.xml")
        shutil.copy2(monochrome, drawable / "launcher_monochrome.xml")
        must_replace(DEST / "app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml",
                     '@color/ic_launcher_background', '@android:color/black')
        # Existing OuterTune app name and Kotlin namespaces remain for code compatibility;
        # the application ID and all user-facing primary branding are independent.

        home = DEST / "app/src/main/java/com/dd3boh/outertune/ui/screens/HomeScreen.kt"
        add_import(home, 'import androidx.compose.foundation.layout.Row',
                   'import androidx.compose.foundation.layout.Column\n'
                   'import androidx.compose.foundation.layout.Arrangement\n'
                   'import androidx.compose.material3.Text\n'
                   'import androidx.compose.ui.text.font.FontWeight\n'
                   'import androidx.compose.ui.unit.sp\n')
        must_replace(home,
                     '''        LazyColumn(
            state = lazylistState,
            contentPadding = LocalPlayerAwareWindowInsets.current.asPaddingValues()
        ) {
            item {''',
                     '''        LazyColumn(
            state = lazylistState,
            contentPadding = LocalPlayerAwareWindowInsets.current.asPaddingValues()
        ) {
            item(key = "omo-hero") {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 24.dp, vertical = 20.dp),
                    verticalArrangement = Arrangement.spacedBy(2.dp),
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "omo",
                            color = MaterialTheme.colorScheme.onBackground,
                            style = MaterialTheme.typography.displayLarge.copy(
                                fontWeight = FontWeight.Black,
                                letterSpacing = (-3).sp,
                            ),
                        )
                        Text(
                            text = " ▶",
                            color = MaterialTheme.colorScheme.primary,
                            style = MaterialTheme.typography.titleLarge,
                        )
                    }
                    Text(
                        text = "Your music. Your way.",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
            item {''')

        (DEST / "UPSTREAM.md").write_text(
            "# Source attribution\n\n"
            "omo Music 0.1.0 uses the playback, search, library and settings implementation "
            "from [OuterTune](https://github.com/OuterTune/OuterTune) at "
            f"commit \`{actual_sha}\` (branch \`lite\`). "
            "OuterTune and InnerTune-derived source files retain their GPL-3.0 notices. "
            "Changes: distinct app ID, logo, colors, default black theme, expressive shapes, "
            "home composition, application name. LICENSE is kept verbatim.\n"
        )
        (DEST / "README.md").write_text(
            "# omo Music — Android\n\n"
            "Native Android application, built from open-source OuterTune playback/search "
            "and library internals with its own omo UI direction, not ReVanced patches.\n\n"
            "## Build\n\n"
            "JDK 21, Android SDK 37, and Android Gradle Plugin dependencies required.\n\n"
            "\`\`\`bash\ncd client\n./gradlew :app:assembleCoreDebug\n\`\`\`\n\n"
            "APK: \`app/build/outputs/apk/core/debug/\`.\n"
            "Upstream license: GPL-3.0; see LICENSE and UPSTREAM.md.\n"
        )

    print("Imported native omo Music Android code from", SOURCE_SHA)

if __name__ == "__main__":
    main()
