#!/usr/bin/env python3
"""Import a complete Android-capable GPL-3.0 Metrolist source snapshot.

Run in a GitHub Actions runner with network access. Unlike a WebView mockup,
this imports the real InnerTube/Media3 player and Compose UI into native/.
The older ReVanced resource patches remain untouched at repository root.
"""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "native"
UPSTREAM = "https://github.com/MetrolistGroup/Metrolist.git"

# Android source + supporting Kotlin/Gradle modules. Non-Android targets,
# marketing screenshots and third-party CI are not required for the APK.
DIRECTORIES = (
    "androidApp", "shared", "listenTogetherProto", "opusDecoder",
    "metroproto", "gradle", "scripts"
)
FILES = (
    "build.gradle.kts", "settings.gradle.kts", "gradle.properties",
    "gradlew", "gradlew.bat", "LICENSE", ".editorconfig", ".gitattributes",
)
SKIP = (".git", ".gradle", ".idea", "build", "node_modules", ".DS_Store")


def run(*args, cwd=None):
    print("+", " ".join(args), flush=True)
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def ignore(directory, names):
    return {name for name in names if name in SKIP}


def main():
    if TARGET.exists():
        raise SystemExit("native/ already exists: refusing to replace local changes.")
    with tempfile.TemporaryDirectory(prefix="omo-upstream-") as temp:
        source = Path(temp) / "metrolist"
        run(
            "git", "clone", "--depth", "1", "--recurse-submodules",
            "--shallow-submodules", UPSTREAM, str(source)
        )
        revision = run("git", "rev-parse", "HEAD", cwd=source)
        for directory in DIRECTORIES:
            if not (source / directory).is_dir():
                raise RuntimeError(f"Missing upstream module: {directory}")
        TARGET.mkdir()
        try:
            for directory in DIRECTORIES:
                shutil.copytree(
                    source / directory, TARGET / directory, ignore=ignore,
                    symlinks=False
                )
            for filename in FILES:
                if (source / filename).is_file():
                    shutil.copy2(source / filename, TARGET / filename)
            (TARGET / "UPSTREAM.md").write_text(
                "# Source provenance\n\n"
                f"Base project: [Metrolist]({UPSTREAM})\n\n"
                f"Imported commit: \`{revision}\`\n\n"
                "License: GNU GPL v3, copied as [LICENSE](LICENSE).\n"
                "The original authors retain attribution. Changes are documented "
                "in the parent omo Music repository.\n\n"
                "omo Music is an independent derivative, not an official Metrolist "
                "or YouTube Music build.\n",
                encoding="utf-8",
            )
            (TARGET / "README.md").write_text(
                "# omo Music — native Android client\n\n"
                "This is a customized GPL-3.0 derivative of "
                "[Metrolist](https://github.com/MetrolistGroup/Metrolist) "
                "with Material 3 Expressive and YouTube Music playback. "
                "The independent ReVanced appearance patches live at repo root.\n\n"
                "## Build\n\n"
                "Requires JDK 25 (Temurin/Adoptium), an Android SDK compatible "
                "with the upstream Android project, and configured Android licenses.\n\n"
                "\`\`\`bash\n"
                "cd native\n"
                "./gradlew :androidApp:assembleDebug\n"
                "\`\`\`\n\n"
                "The debug build should output an APK under "
                "\`androidApp/build/outputs/apk/debug/\`. "
                "This import has not been proven to compile until CI succeeds.\n\n"
                "## Defaults\n\n"
                "- Application ID: \`dev.w0rd3r.omomusic\`\n"
                "- Name and adaptive icon: omo Music\n"
                "- Material 3 Expressive layout\n"
                "- First launch: OLED-black, soft-blue accent, reduced gradients\n"
                "- Appearance, player, typography and navigation remain customizable\n\n"
                "The upstream automatic updater and Discord application ID are "
                "disabled because they are not controlled by omo Music.\n\n"
                "## Licensing\n\n"
                "Preserve attribution and GPL-3.0 license when distributing "
                "source or builds. For exact upstream revision, see "
                "[UPSTREAM.md](UPSTREAM.md).\n",
                encoding="utf-8",
            )
            run("python3", str(ROOT / "scripts/brand_native.py"), cwd=ROOT)
        except BaseException:
            shutil.rmtree(TARGET)
            raise

    print(f"Imported and branded Metrolist revision {revision}")


if __name__ == "__main__":
    main()
