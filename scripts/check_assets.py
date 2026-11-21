#!/usr/bin/env python3
"""Static project checks, using only the standard library."""
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "patches/src/main/kotlin/dev/w0rd3r/omo/patches"
RESOURCE_ROOT = ROOT / "patches/src/main/resources/omo"
RESOURCES = [
    "drawable/omo_foreground.xml",
    "drawable/omo_monochrome.xml",
    "mipmap-anydpi/omo_launcher.xml",
    "mipmap-anydpi-v26/omo_launcher.xml",
    "values/omo_colors.xml",
]
ANDROID = "{http://schemas.android.com/apk/res/android}"

for relative in RESOURCES:
    path = RESOURCE_ROOT / relative
    assert path.is_file(), f"Missing icon resource: {relative}"
    root = ET.parse(path).getroot()
    if relative.endswith("v26/omo_launcher.xml"):
        assert root.tag == "adaptive-icon", root.tag
        assert root.find("background") is not None
        assert root.find("foreground") is not None
        assert root.find("monochrome") is not None
    elif "omo_colors" in relative:
        assert root.find("color").attrib["name"] == "omo_black"
    else:
        assert root.tag == "vector", root.tag
        assert root.find("path") is not None
        assert root.attrib[ANDROID + "viewportWidth"] == "108"

source = (SOURCE / "OmoBrandingPatch.kt").read_text(encoding="utf-8")
for reference in RESOURCES:
    assert reference in source, "Resource not copied: " + reference
assert "com.google.android.apps.youtube.music" in source
assert "@mipmap/omo_launcher" in source
assert "activity-alias" in source

theme = (SOURCE / "OmoBlackThemePatch.kt").read_text(encoding="utf-8")
assert "yt_black3" in theme
assert (ROOT / "gradle/wrapper/gradle-wrapper.jar").is_file()
assert (ROOT / "assets/omo-icon.svg").exists()
ET.parse(ROOT / "assets/omo-icon.svg")
print("PASS: 5 valid Android XML resources, launcher fallback, vector logo and patch references")
