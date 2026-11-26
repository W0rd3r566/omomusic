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
        replace(app, 'versionName = "0.12.11"', 'versionName = "0.2.8"')
        replace(app, 'versionCode = 103', 'versionCode = 10')
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
                "import com.dd3boh.outertune.ui.omo.OmoArtwork\n")
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
            start += len(marker)
            artwork = text[start:end].rstrip()
            enabled = "state.isExpanded && !showLyrics"
            if layout == "3.2b":
                enabled += " && (!compactPlayer || compactCoverFits(maxHeight))"
            wrapper = f"                        OmoArtwork(mediaMetadata, playerConnection.player, {enabled}) {{\n"
            wrapped = "\n".join("    " + line if line.strip() else "" for line in artwork.splitlines())
            player.write_text(text[:start] + wrapper + wrapped + "\n                        }\n" + text[end:], encoding="utf-8")

        innertube = DEST / "innertube/src/main/java/com/zionhuang/innertube"
        shutil.copy2(ROOT / "scripts/android17/OmoVideoLookup.kt", innertube / "OmoVideoLookup.kt")
        replace(innertube / "InnerTube.kt", "    /** What a next (",
                """    internal suspend fun videoWatchNext(client: YouTubeClient, videoId: String) = httpClient.post("next") {
        ytClient(client, setLogin = true)
        setBody(kotlinx.serialization.json.buildJsonObject {
            put("context", kotlinx.serialization.json.Json.encodeToJsonElement(Context.serializer(),
                client.toContext(locale, visitorData, accountId)))
            put("videoId", kotlinx.serialization.json.JsonPrimitive(videoId))
            put("playlistId", kotlinx.serialization.json.JsonPrimitive("RDAMVM$videoId"))
            put("enablePersistentPlaylistPanel", kotlinx.serialization.json.JsonPrimitive(true))
            put("isAudioOnly", kotlinx.serialization.json.JsonPrimitive(true))
            put("tunerSettingValue", kotlinx.serialization.json.JsonPrimitive("AUTOMIX_SETTING_NORMAL"))
            put("watchEndpointMusicSupportedConfigs", kotlinx.serialization.json.buildJsonObject {
                put("watchEndpointMusicConfig", kotlinx.serialization.json.buildJsonObject {
                    put("hasPersistentPlaylistPanel", kotlinx.serialization.json.JsonPrimitive(true))
                    put("musicVideoType", kotlinx.serialization.json.JsonPrimitive("MUSIC_VIDEO_TYPE_ATV"))
                })
            })
        })
    }

    /** What a next (""")
        replace(innertube / "YouTube.kt", "    /** The queue a watch-next answer holds:",
                """    suspend fun videoCounterpart(videoId: String, title: String, artists: List<String>): String? {
        val match = try {
            kotlinx.coroutines.withTimeoutOrNull(4_000) {
                findVideoMatch(innerTube.videoWatchNext(WEB_REMIX, videoId).body<kotlinx.serialization.json.JsonObject>(), videoId)
            }
        } catch (cancelled: kotlinx.coroutines.CancellationException) {
            throw cancelled
        } catch (_: Exception) {
            null
        }
        match?.id?.let { return it }
        if (artists.isNotEmpty()) {
            val result = kotlinx.coroutines.withTimeoutOrNull(4_000) {
                val searchResult = search("$title ${artists.first()}", SearchFilter.FILTER_VIDEO)
                val failure = searchResult.exceptionOrNull()
                if (failure is kotlinx.coroutines.CancellationException || (failure != null && match?.audioTrack == true)) {
                    throw failure
                }
                searchResult.getOrNull()
            }
            val candidate = result?.items?.filterIsInstance<SongItem>()?.firstOrNull { song ->
                song.title.equals(title, ignoreCase = true) &&
                    song.artists.any { artist -> artists.any { it.equals(artist.name, ignoreCase = true) } } &&
                    (match?.audioTrack != true || song.id != videoId)
            }
            candidate?.let { return it.id }
        }
        return videoId.takeUnless { match?.audioTrack == true }
    }

    /** The queue a watch-next answer holds:""")

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

        shutil.copy2(ROOT / "scripts/android17/OmoShapes.kt", new_hero.parent / "OmoShapes.kt")
        thumbnail = DEST / ui_root / "player/Thumbnail.kt"
        replace(thumbnail, "contentDescription = null,\n                            modifier = Modifier.fillMaxSize()",
                "contentDescription = null,\n                            contentScale = androidx.compose.ui.layout.ContentScale.Crop,\n                            modifier = Modifier.fillMaxSize()")
        main_package = DEST / ui_root.parent
        shape_import = "import com.dd3boh.outertune.ui.omo.OmoShape\nimport com.dd3boh.outertune.ui.omo.omoShape\n"
        for target in (main_package / "MainActivity.kt", player):
            replace(target, "import androidx.compose.foundation.shape.RoundedCornerShape",
                    shape_import + "import androidx.compose.foundation.shape.RoundedCornerShape")
        replace(main_package / "MainActivity.kt", "RoundedCornerShape(if (slimNav) 26.dp else 28.dp)", "omoShape(OmoShape.Dock)")
        replace(player, "    val glassIntensity by", "    val controlsShape = omoShape(OmoShape.Buttons)\n    val glassIntensity by")
        replace(player, "RoundedCornerShape(32.dp)", "controlsShape")
        replace(player, ".clip(RoundedCornerShape(playPauseRoundness))", ".clip(controlsShape)")
        replace(DEST / ui_root / "screens/settings/LookAndFeelSettings.kt", "            ThemeAppFrag()",
                "            ThemeAppFrag()\n            com.dd3boh.outertune.ui.omo.OmoShapeSettings()")
        replace(main_package / "constants/Unreleased.kt", "val WIDGETS_PAGE = BuildConfig.DEBUG", "val WIDGETS_PAGE = true")
        cover_loader = main_package / "utils/SessionBitmapLoader.kt"
        replace(cover_loader, "    systemCoverSize(bitmap.width, bitmap.height, px)?.let { (w, h) -> Bitmap.createScaledBitmap(bitmap, w, h, true) } ?: bitmap",
                """    minOf(bitmap.width, bitmap.height).let { side ->
        val square = if (bitmap.width == bitmap.height) bitmap else Bitmap.createBitmap(
            bitmap, (bitmap.width - side) / 2, (bitmap.height - side) / 2, side, side)
        if (px > 0 && side > px) Bitmap.createScaledBitmap(square, px, px, true) else square
    }""")
        for locale, labels in (("values", ("Navigation bar roundness", "Player button roundness")),
                               ("values-ru", ("Скругление нижней панели", "Скругление кнопок плеера"))):
            strings = DEST / "app/src/main/res" / locale / "omo_strings.xml"
            replace(strings, "</resources>", "".join(
                f'    <string name="{key}">{label} · %1$d%%</string>\n'
                for key, label in zip(("omo_dock_shape", "omo_controls_shape"), labels)
            ) + "</resources>")

        import re
        for xml in resources.glob("values*/*.xml"):
            original = xml.read_text(encoding="utf-8")
            # Keep external links, file paths, preference keys and third-party credits intact.
            def brand(match):
                value = match.group()
                if any(word in value.lower() for word in ("copyright", "licensed", "fork of", "based on", "credits")):
                    return value
                return re.sub(r"(^|\\n|(?<=[^\w./]))(?:InterTune|OuterTune|InnerTune)(?![\w/]|\.[a-zA-Z])", r"\1Omo music", value)
            changed = re.sub(r"(?<=>)[^<>]+(?=<)", brand, original)
            if changed != original:
                xml.write_text(changed, encoding="utf-8")
        for file, old in (("ui/component/LyricsCard.kt", 'APP_NAME = "InterTune"'),
                          ("ui/screens/settings/SettingsIndex.kt", 'appName: String = "InterTune"'),
                          ("playback/CastProbe.kt", 'Sender(Build.MODEL, "InterTune"')):
            replace(main_package / file, old, old.replace("InterTune", "Omo music"))
        for name in ("launcher_monochrome", "launcher_foreground"):
            shutil.copy2(resources / "drawable/small_icon.xml", resources / f"drawable/{name}.xml")
        for image in resources.glob("mipmap-*/ic_launcher*.png"):
            shutil.copy2(resources / "drawable-nodpi/omo_wordmark.png", image)
        about = DEST / ui_root / "screens/settings/AboutScreen.kt"
        page = about.read_text(encoding="utf-8")
        start = page.index("        // A fork's build")
        end = page.index("        Row(verticalAlignment = Alignment.CenterVertically)", start)
        about.write_text(page[:start] + """        Image(
            painter = painterResource(R.drawable.omo_wordmark),
            contentDescription = stringResource(R.string.app_name),
            modifier = Modifier.size(96.dp).clip(CircleShape)
        )
        Text(stringResource(R.string.app_name), style = MaterialTheme.typography.headlineMedium)

""" + page[end:], encoding="utf-8")
        if "import androidx.compose.foundation.layout.size" not in about.read_text() and "import androidx.compose.foundation.layout.*" not in about.read_text():
            replace(about, "import androidx.compose.runtime.Composable", "import androidx.compose.foundation.layout.size\nimport androidx.compose.runtime.Composable")
        widgets = main_package / "widget/WidgetConfigActivity.kt"
        replace(widgets, "            // The style first:", """            Section(stringResource(R.string.omo_presets))
            TextButton(onClick = { s = WidgetSettings(style = WidgetStyle.COVER,
                buttons = WidgetButtons.PLAY_ONLY, background = WidgetBackground.SYSTEM,
                showArtwork = false, showLike = false) }) { Text(stringResource(R.string.omo_mini)) }
            TextButton(onClick = { s = WidgetSettings(style = WidgetStyle.SHELF, look = ShelfLook.RECORDS,
                list = WidgetList.RECENT) }) { Text(stringResource(R.string.omo_records)) }
            // The style first:""")
        for locale, labels in (("values", ("Widget presets", "Compact player", "Recent records")),
                               ("values-ru", ("Варианты виджета", "Компактный плеер", "Недавние пластинки"))):
            target = resources / locale / "omo_strings.xml"
            replace(target, "</resources>", "".join(
                f'<string name="{key}">{label}</string>\n' for key, label in
                zip(("omo_presets", "omo_mini", "omo_records"), labels)) + "</resources>")
        # Separate launcher entries. All three use the same playback snapshot and per-widget settings.
        widget_dir = main_package / "widget"
        receiver = widget_dir / "MusicWidgetReceiver.kt"
        replace(receiver, "class MusicWidgetReceiver :", "open class MusicWidgetReceiver :")
        with receiver.open("a") as kt:
            kt.write("\nclass OmoMiniReceiver : MusicWidgetReceiver()\nclass OmoRecordsReceiver : MusicWidgetReceiver()\n")
        store = widget_dir / "WidgetStore.kt"
        replace(store, """AppWidgetManager.getInstance(context)
            .getAppWidgetIds(ComponentName(context, MusicWidgetReceiver::class.java))
            .isNotEmpty()""", "placed(context).isNotEmpty()")
        replace(store, "manager.getAppWidgetIds(ComponentName(context, MusicWidgetReceiver::class.java)).any", "placed(context).any")
        replace(store, "AppWidgetManager.getInstance(context).getAppWidgetIds(ComponentName(context, MusicWidgetReceiver::class.java)).sorted()",
                """val manager = AppWidgetManager.getInstance(context)
        listOf(MusicWidgetReceiver::class.java, OmoMiniReceiver::class.java, OmoRecordsReceiver::class.java)
            .flatMap { manager.getAppWidgetIds(ComponentName(context, it)).asList() }.sorted()""")
        replace(store, "MusicWidget().updateAll(context)", "refreshPlaced(context)")
        replace(store, "    private val settingsLock", """    private suspend fun widgetIds(context: Context) = placed(context).map {
        GlanceAppWidgetManager(context).getGlanceIdBy(it)
    }

    private suspend fun refreshPlaced(context: Context) {
        for (id in widgetIds(context)) MusicWidget().update(context, id)
    }

    private val settingsLock""")
        replace(store, "GlanceAppWidgetManager(context).getGlanceIds(MusicWidget::class.java)", "widgetIds(context)")
        replace(store, "WidgetKeys.read(getAppWidgetState(context, PreferencesGlanceStateDefinition, glanceId))",
                """val prefs = getAppWidgetState(context, PreferencesGlanceStateDefinition, glanceId)
                if (prefs.asMap().isNotEmpty()) WidgetKeys.read(prefs)
                else when (AppWidgetManager.getInstance(context).getAppWidgetInfo(appWidgetId)?.provider?.className) {
                    OmoMiniReceiver::class.java.name -> omoMiniWidget()
                    OmoRecordsReceiver::class.java.name -> omoRecordsWidget()
                    else -> WidgetSettings()
                }""")
        mini = "WidgetSettings(style = WidgetStyle.COVER,\n                buttons = WidgetButtons.PLAY_ONLY, background = WidgetBackground.SYSTEM,\n                showArtwork = false, showLike = false)"
        records = "WidgetSettings(style = WidgetStyle.SHELF, look = ShelfLook.RECORDS,\n                list = WidgetList.RECENT)"
        for function, body in (("omoMiniWidget", mini), ("omoRecordsWidget", records)):
            replace(widgets, body, function + "()")
            with (widget_dir / "WidgetOptions.kt").open("a") as kt:
                kt.write(f"\ninternal fun {function}() = {body}\n")
        manifest_text = manifest.read_text()
        at = manifest_text.index('android:name=".widget.MusicWidgetReceiver"')
        receiver_xml = manifest_text[manifest_text.rindex("<receiver", 0, at):manifest_text.index("</receiver>", at) + 11]
        for receiver_name, label, name, width, height in (
            ("OmoMiniReceiver", "omo_mini", "omo_mini_widget", 3, 1),
            ("OmoRecordsReceiver", "omo_records", "omo_records_widget", 4, 3),
        ):
            provider = (resources / "xml/music_widget_info.xml").read_text()
            provider = provider.replace('android:targetCellWidth="4"', f'android:targetCellWidth="{width}"').replace(
                'android:targetCellHeight="2"', f'android:targetCellHeight="{height}"').replace(
                'android:minWidth="180dp"', f'android:minWidth="{width * 48}dp"').replace(
                'android:minHeight="110dp"', f'android:minHeight="{height * 48}dp"').replace(
                '@string/widget_description', '@string/' + label)
            (resources / f"xml/{name}.xml").write_text(provider)
            extra = receiver_xml.replace("MusicWidgetReceiver", receiver_name).replace("widget_label", label).replace("music_widget_info", name)
            replace(manifest, receiver_xml, receiver_xml + "\n        " + extra)
            picker = widget_dir / "WidgetPicker.kt"
            replace(picker, "    RECOGNITION(", f"    {label.upper()}({receiver_name}::class.java, R.layout.widget_preview, {width}, {height}, {width*70}, {height*70}),\n    RECOGNITION(")
            screen = DEST / ui_root / "screens/settings/WidgetsSettings.kt"
            marker = "            WidgetAddRow(\n                title = stringResource(R.string.recognise),"
            replace(screen, marker, f"""            WidgetAddRow(
                title = stringResource(R.string.{label}),
                widget = OfferedWidget.{label.upper()},
                onAdd = if (canPin) {{ {{ add(OfferedWidget.{label.upper()}) }} }} else null,
                modifier = Modifier.settingRow(R.string.{label}),
            )
            WidgetsRowLine()
""" + marker)
        service = main_package / "playback/MusicService.kt"
        controls = main_package / "playback/MediaControlButtons.kt"
        replace(controls, "    const val SLOTS = 2", """    const val SLOTS = 2
    val showExtrasKey = androidx.datastore.preferences.core.booleanPreferencesKey("omo_notification_extras")""")
        replace(service, "    private var mediaControlButtons =", "    private var showExtraButtons = true\n    private var mediaControlButtons =")
        replace(service, "        mediaControlButtons = MediaControlButtons.parse(dataStore[MediaControlButtonsKey])",
                """        showExtraButtons = dataStore[MediaControlButtons.showExtrasKey] ?: true
        dataStore.data.map { it[MediaControlButtons.showExtrasKey] ?: true }.distinctUntilChanged()
            .collect(scope) { show ->
                if (show != showExtraButtons) {
                    showExtraButtons = show
                    updateNotification()
                }
            }
        mediaControlButtons = MediaControlButtons.parse(dataStore[MediaControlButtonsKey])""")
        replace(service, "if (inCar) MediaControlButtons.CAR else MediaControlButtons.layout(mediaControlButtons)",
                "if (inCar) MediaControlButtons.CAR else if (showExtraButtons) MediaControlButtons.layout(mediaControlButtons) else emptyList()")
        frag = DEST / ui_root / "screens/settings/fragments/MediaControlButtonsFrag.kt"
        replace(frag, "    val chosen = remember(saved)", """    val (showExtras, setShowExtras) = rememberPreference(MediaControlButtons.showExtrasKey, true)
    com.dd3boh.outertune.ui.component.SwitchPreference(
        title = { Text(stringResource(R.string.omo_extra_buttons)) },
        checked = showExtras, onCheckedChange = setShowExtras,
        icon = { Icon(Icons.Rounded.ScreenLockPortrait, null) },
    )
    if (!showExtras) return
    val chosen = remember(saved)""")
        for locale, label in (("values", "Extra media notification buttons"), ("values-ru", "Дополнительные кнопки в уведомлении")):
            replace(resources / locale / "omo_strings.xml", "</resources>",
                    f'<string name="omo_extra_buttons">{label}</string>\n</resources>')
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
