# omo Music — native Android client

This is a customized GPL-3.0 derivative of [Metrolist](https://github.com/MetrolistGroup/Metrolist) with Material 3 Expressive and YouTube Music playback. The independent ReVanced appearance patches live at repo root.

## Build

Requires JDK 25 (Temurin/Adoptium), an Android SDK compatible with the upstream Android project, and configured Android licenses.

\`\`\`bash
cd native
./gradlew :androidApp:assembleDebug
\`\`\`

The debug build should output an APK under \`androidApp/build/outputs/apk/debug/\`. This import has not been proven to compile until CI succeeds.

## Defaults

- Application ID: \`dev.w0rd3r.omomusic\`
- Name and adaptive icon: omo Music
- Material 3 Expressive layout
- First launch: OLED-black, soft-blue accent, reduced gradients
- Appearance, player, typography and navigation remain customizable

The upstream automatic updater and Discord application ID are disabled because they are not controlled by omo Music.

## Licensing

Preserve attribution and GPL-3.0 license when distributing source or builds. For exact upstream revision, see [UPSTREAM.md](UPSTREAM.md).
