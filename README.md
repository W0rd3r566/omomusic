# omo Music

**omo** is an independent, open-source set of **ReVanced resource patches for YouTube Music**, with a minimal black-and-white identity and a small pastel-blue Play symbol.

This is **a working source repository for patch development, not a finished YouTube Music client APK**. No target APK, proprietary Google assets, Google credentials, patches for Premium access, or bypasses of DRM/payment checks are distributed here.

## Implemented in v0.1.0

- **omo Branding:** replaces the Android launcher app label and launcher activity-alias label with `omo`, adds the white rounded logo with the light-blue ▶.
- A true **Android adaptive icon**, circular on Pixel, with monochrome layer and a legacy vector fallback.
- **omo Black:** optional restrained dark palette affecting supported existing YouTube Music color resources.
- Official Gradle wrapper, build CI and static icon/resource tests.
- The resource patches only modify appearance. Your music, recommendations and Google account data are handled by the original YouTube Music app, subject to its own terms and platform compatibility.

## Build patch bundle

Requirements: **JDK 17**; dependencies and GitHub Packages credentials may be needed for the ReVanced Gradle plugin (see the upstream [ReVanced template](https://github.com/ReVanced/revanced-patches-template)).

```bash
git clone https://github.com/W0rd3r566/omomusic.git
cd omomusic
python3 scripts/check_assets.py
./gradlew build
```

The patch project uses the ReVanced Patches Gradle plugin (`app.revanced.patches`) and Patcher APIs from the official template. Once built, the output is a **patch bundle**, not an APK. For use with a legally obtained YouTube Music installation, choose compatible patcher and app versions. **This source does not include or automate modifying an APK**, and current runtime compatibility has not yet been confirmed.

GitHub Actions → **Build omo patches** checks the project and uploads build outputs if compilation succeeds.

## Structure

```text
assets/omo-icon.svg            original vector logo
patches/src/main/kotlin/...    branding + dark-theme Kotlin patches
patches/src/main/resources/omo/  adaptive/monochrome icon resources
scripts/check_assets.py        no-dependency resource and source validation
.github/workflows/build.yml    tests + Gradle compilation + patch artifacts
```

## Roadmap (not implemented)

- Compatibility tests against a current locally supplied YouTube Music APK.
- Verify a separate application ID so it can coexist with a user's existing player.
- Optional layout customization and animations where the target app's implementation permits them.
- Media player visual customization, but only after version-specific feasibility testing.

A ReVanced patch does **not** automatically enable premium/subscription features, provide a Google login mechanism, or give full control of the closed-source UI.

## Credits and license

Original project by **W0rd3r566**. Build conventions were taken from [ReVanced Patches Template](https://github.com/ReVanced/revanced-patches-template); that project and its authors are credited. Licensed **GPL-3.0-or-later**. `omo` is not affiliated with Google, YouTube, YouTube Music or ReVanced. All third-party trademarks belong to their respective owners.
