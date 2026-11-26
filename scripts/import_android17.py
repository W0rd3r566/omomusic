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
            "taglib", "innertubex", "gradle", "prebuilt", "config",
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
        replace(app, 'versionName = "0.12.11"', 'versionName = "0.2.4"')
        replace(app, 'versionCode = 103', 'versionCode = 6')
        replace(app, 'var outputFileName = "InterTune-', 'var outputFileName = "omoMusic-')
        replace(DEST / "app/src/main/res/values/app_name.xml",
                'name="app_name">InterTune<', 'name="app_name">Omo music<')
        replace(DEST / "app/src/debug/res/values/app_name.xml",
                "InterTune Debug", "Omo music")

        resources = DEST / "app/src/main/res"
        for icon in (ROOT / "scripts/android17/res").glob("*/*"):
            target = resources / icon.parent.name / icon.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(icon, target)
        manifest = DEST / "app/src/main/AndroidManifest.xml"
        replace(manifest, 'android:icon="@mipmap/ic_launcher"', 'android:icon="@mipmap/omo_launcher"')
        replace(manifest, 'android:roundIcon="@mipmap/ic_launcher_round"',
                'android:roundIcon="@mipmap/omo_launcher"')
        replace(
            DEST / "app/src/main/java/com/dd3boh/outertune/ui/theme/Theme.kt",
            "val DefaultThemeColor = Color(0xFFED5564)",
            "val DefaultThemeColor = Color(0xFFA7D7FF)",
        )
        replace(DEST / "gradle/libs.versions.toml",
                'material3 = "1.4.0"', 'material3 = "1.5.0-alpha10"')
        ui_root = Path("app/src/main/java/com/dd3boh/outertune/ui")
        theme = DEST / ui_root / "theme/Theme.kt"
        replace(theme, "import androidx.compose.material3.MaterialTheme",
                "import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi\n"
                "import androidx.compose.material3.MaterialExpressiveTheme\n"
                "import androidx.compose.material3.MaterialTheme\n"
                "import androidx.compose.material3.MotionScheme")
        replace(theme, "@Composable\nfun OuterTuneTheme(",
                "@OptIn(ExperimentalMaterial3ExpressiveApi::class)\n@Composable\nfun OuterTuneTheme(")
        replace(theme, "    MaterialTheme(\n        colorScheme = colorScheme,",
                "    MaterialExpressiveTheme(\n        colorScheme = colorScheme,\n"
                "        motionScheme = MotionScheme.expressive(),")

        new_hero = DEST / ui_root / "omo/OmoHero.kt"
        new_hero.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "scripts/android17/OmoHero.kt", new_hero)
        shutil.copy2(ROOT / "scripts/android17/OmoVideo.kt", new_hero.parent / "OmoVideo.kt")
        player = DEST / ui_root / "player/Player.kt"
        replace(player, "import com.dd3boh.outertune.playback.PlayerConnection\n",
                "import com.dd3boh.outertune.playback.PlayerConnection\n"
                "import com.dd3boh.outertune.ui.omo.OmoVideoAction\n")
        for layout in ("3.2a", "3.2b"):
            marker = (
                "                        Log.v(TAG, \"PLR-" + layout + "\")\n"
            )
            text = player.read_text(encoding="utf-8")
            start = text.index(marker)
            if layout == "3.2a":
                end = text.index("\n                    }\n\n                    Column(", start)
            else:
                end = text.index("\n                        // Laid over the empty top right corner", start)
            action = """
                        if (state.isExpanded) {
                            OmoVideoAction(
                                metadata = mediaMetadata,
                                player = playerConnection.player,
                                modifier = Modifier.align(Alignment.TopCenter)
                                    .windowInsetsPadding(WindowInsets.systemBars.only(WindowInsetsSides.Top)),
                            )
                        }
"""
            player.write_text(text[:end] + action + text[end:], encoding="utf-8")

        innertube = DEST / "innertube/src/main/java/com/zionhuang/innertube"
        replace(innertube / "models/PlaylistPanelRenderer.kt",
                "        val automixPreviewVideoRenderer: AutomixPreviewVideoRenderer?,\n    )",
                """        val automixPreviewVideoRenderer: AutomixPreviewVideoRenderer?,
        val playlistPanelVideoWrapperRenderer: VideoWrapper? = null,
    )

    @Serializable
    data class VideoWrapper(
        val primaryRenderer: VideoRenderer? = null,
        val counterpart: List<Counterpart> = emptyList(),
    )

    @Serializable
    data class Counterpart(val counterpartRenderer: VideoRenderer? = null)

    @Serializable
    data class VideoRenderer(val playlistPanelVideoRenderer: VideoIdentity? = null)

    @Serializable
    data class VideoIdentity(val videoId: String? = null, val navigationEndpoint: NavigationEndpoint? = null)
""".rstrip())
        replace(innertube / "YouTube.kt",
                "    /** The queue a watch-next answer holds:",
                """    suspend fun videoCounterpart(videoId: String): String? {
        val response = innerTube.next(WEB_REMIX, videoId, null, null, null, null).body<NextResponse>()
        val rows = queueIn(response)?.contents.orEmpty()
        val direct = rows.firstNotNullOfOrNull { it.playlistPanelVideoRenderer?.takeIf { song -> song.videoId == videoId } }
        val directType = direct?.musicVideoType
        if (directType != null && directType != MUSIC_VIDEO_TYPE_ATV) return videoId
        val wrapper = rows
            .firstNotNullOfOrNull { row ->
                row.playlistPanelVideoWrapperRenderer?.takeIf {
                    it.primaryRenderer?.playlistPanelVideoRenderer?.videoId == videoId
                }
            } ?: return null
        val primary = wrapper.primaryRenderer?.playlistPanelVideoRenderer
        val primaryType = primary?.navigationEndpoint?.watchEndpoint?.musicVideoType
        if (primaryType != null && primaryType != MUSIC_VIDEO_TYPE_ATV) return videoId
        return wrapper.counterpart.firstNotNullOfOrNull { candidate ->
            val video = candidate.counterpartRenderer?.playlistPanelVideoRenderer
            val type = video?.navigationEndpoint?.watchEndpoint?.musicVideoType
            video?.videoId?.takeIf { type != MUSIC_VIDEO_TYPE_ATV }
        }
    }

    /** The queue a watch-next answer holds:""")
        replace(innertube / "YouTube.kt",
                "import com.zionhuang.innertube.models.WatchEndpoint\n",
                "import com.zionhuang.innertube.models.WatchEndpoint\n"
                "import com.zionhuang.innertube.models.musicVideoType\n")

        for locale in ("values", "values-ru"):
            source_strings = ROOT / "client/app/src/main/res" / locale / "omo_strings.xml"
            target_strings = DEST / "app/src/main/res" / locale / "omo_strings.xml"
            target_strings.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_strings, target_strings)
            song, youtube = (
                ("Песня", "Открыть в YouTube") if locale == "values-ru"
                else ("Song", "Open in YouTube")
            )
            replace(target_strings, "</resources>",
                    f'    <string name="omo_return_to_song">{song}</string>\n'
                    f'    <string name="omo_open_youtube">{youtube}</string>\n'
                    '</resources>')

        shutil.copy2(ROOT / "scripts/android17/OmoChannels.kt", new_hero.parent / "OmoChannels.kt")
        shutil.copy2(ROOT / "scripts/android17/OmoChannel.kt", innertube / "OmoChannel.kt")
        account = DEST / ui_root / "screens/settings/fragments/AccountFrag.kt"
        replace(account, "    // The row used to snap", """    if (isLoggedIn) {
        com.dd3boh.outertune.ui.omo.OmoChannels(innerTubeCookie, accountChannelHandle)
    }
    // The row used to snap""")
        body = innertube / "models/body/OmoChannelsBody.kt"
        body.write_text("""package com.zionhuang.innertube.models.body

import com.zionhuang.innertube.models.Context
import kotlinx.serialization.Serializable

@Serializable
internal data class OmoChannelsBody(
    val context: Context,
    val requestType: String = "ACCOUNTS_LIST_REQUEST_TYPE_CHANNEL_SWITCHER",
    val callCircumstance: String = "SWITCHING_USERS_FULL",
)
""", encoding="utf-8")
        inner = innertube / "InnerTube.kt"
        replace(inner, "fun HttpRequestBuilder.ytClient(client: YouTubeClient, setLogin: Boolean = false)",
                "fun HttpRequestBuilder.ytClient(client: YouTubeClient, setLogin: Boolean = false, "
                "origin: String = YouTubeClient.ORIGIN_YOUTUBE_MUSIC)")
        replace(inner, 'append("X-Origin", YouTubeClient.ORIGIN_YOUTUBE_MUSIC)',
                'append("X-Origin", origin)')
        replace(inner, 'append("Referer", YouTubeClient.REFERER_YOUTUBE_MUSIC)',
                'append("Referer", "$origin/")')
        replace(inner, '${YouTubeClient.ORIGIN_YOUTUBE_MUSIC}")', '$origin")')
        replace(inner, "    suspend fun accountMenu(client: YouTubeClient)", """    suspend fun omoAccounts() = httpClient.post("https://www.youtube.com/youtubei/v1/account/accounts_list") {
        val client = YouTubeClient.WEB.copy(loginSupported = true)
        ytClient(client, setLogin = true, origin = "https://www.youtube.com")
        header("Origin", "https://www.youtube.com")
        setBody(OmoChannelsBody(client.toContext(locale, visitorData, null)))
    }

    suspend fun accountMenu(client: YouTubeClient, identity: String? = accountId)""")
        replace(inner, "setBody(AccountMenuBody(client.toContext(locale, visitorData, accountId)))",
                "setBody(AccountMenuBody(client.toContext(locale, visitorData, identity)))")
        replace(innertube / "YouTube.kt", "    suspend fun accountInfo(): Result<AccountInfo> = runCatching {",
                """    suspend fun omoChannels(): List<OmoChannel> =
        innerTube.omoAccounts().body<kotlinx.serialization.json.JsonObject>()
            .parseAccountsListFallback().distinct()

    suspend fun omoIdentity(channel: OmoChannel): Pair<String, AccountInfo> {
        val raw = channel.dataSyncId.orEmpty()
        val ids = listOfNotNull(raw.substringBefore("||"), raw.substringAfter("||", ""), channel.pageId, "")
            .map(String::trim).distinct()
        val expected = channel.channelHandle ?: channel.byline?.takeIf { it.startsWith("@") }
        // With no handle the displayed name must identify just one row.
        require(expected != null || omoChannels().count { it.name == channel.name } == 1)
        for (id in ids.filter(String::isNotEmpty) + "") {
            val info = accountInfo(id.ifEmpty { null }).getOrNull() ?: continue
            if (expected?.equals(info.channelHandle, ignoreCase = true) ?: (channel.name == info.name)) {
                return id to info
            }
        }
        error("YouTube did not confirm the selected channel")
    }

    suspend fun accountInfo(identity: String? = innerTube.accountId): Result<AccountInfo> = runCatching {""")
        replace(innertube / "YouTube.kt", "innerTube.accountMenu(WEB_REMIX).body<AccountMenuResponse>()",
                "innerTube.accountMenu(WEB_REMIX, identity).body<AccountMenuResponse>()")
        replace(player, """                    if (buttonsBesideTitle) {
                        actionButtons()
                    }
                }

                PlaybackOrder""", """                }
                if (buttonsBesideTitle) {
                    Row(Modifier.fillMaxWidth().padding(horizontal = hPadding),
                        horizontalArrangement = Arrangement.End) { actionButtons() }
                }

                PlaybackOrder""")
        updates = DEST / ui_root.parent / "utils/UpdateChecker.kt"
        replace(updates, "if (!BuiltInKeys.official) return@withContext null",
                'if (BuildConfig.APPLICATION_ID != "dev.w0rd3r.omomusic") return@withContext null')
        replace(updates, "ItzSkyeYT/InterTune", "W0rd3r566/omomusic")
        replace(updates, 'Regex("""-release-', 'Regex("""^Omo-music-release-')
        for locale, labels in (
            ("values", ("YouTube channels", "Could not verify this channel. Try again.", "No music video is available for this song.", "Could not load the video.")),
            ("values-ru", ("Каналы YouTube", "Не удалось подтвердить канал. Попробуй ещё раз.", "Для этой песни нет доступного клипа.", "Не удалось загрузить клип.")),
        ):
            strings = DEST / "app/src/main/res" / locale / "omo_strings.xml"
            names = ("omo_channels", "omo_channel_error", "omo_no_clip", "omo_clip_error")
            replace(strings, "</resources>", "".join(
                f'    <string name="{key}">{value}</string>\n' for key, value in zip(names, labels)
            ) + "</resources>")

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
            "# Omo music 0.2.2\n\n"
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
            "## Updatable releases\n\n"
            "On a machine logged in as the repository maintainer with GitHub CLI, "
            "run `bash scripts/android17/setup-release-signing.sh` from the repository root. "
            "Keep a private backup of the generated signing files. "
            "Run the Omo Music Android workflow with `signed_release=true` to publish "
            "an `Omo-music-release` build artifact signed with that key. Future releases "
            "must reuse the key and increase Android's version code.\n\n"
            "GPL-3.0 source attribution: see UPSTREAM.md and LICENSE.\n",
            encoding="utf-8",
        )
        print("Imported InterTune", TAG, commit)

if __name__ == "__main__":
    main()
