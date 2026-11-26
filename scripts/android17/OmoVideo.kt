/*
 * Copyright (C) 2026 W0rd3r566
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
package com.dd3boh.outertune.ui.omo

import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.draw.clip
import androidx.compose.runtime.key
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.runtime.LaunchedEffect
import kotlinx.coroutines.delay
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.media3.common.Player
import com.dd3boh.outertune.R
import com.dd3boh.outertune.models.MediaMetadata
import com.zionhuang.innertube.YouTube
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.withTimeoutOrNull

private val youtubeId = Regex("[A-Za-z0-9_-]{11}")

@Composable
internal fun OmoArtwork(
    metadata: MediaMetadata?, player: Player, expanded: Boolean, artwork: @Composable () -> Unit,
) {
    val id = metadata?.takeUnless { it.isLocal }?.id
    if (!expanded || id == null || !youtubeId.matches(id)) {
        artwork()
        return
    }
    key(player, id) { InlineArtwork(id, requireNotNull(metadata), player, artwork) }
}

@Composable
private fun InlineArtwork(
    videoId: String, metadata: MediaMetadata, player: Player, artwork: @Composable () -> Unit,
) {
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    val uriHandler = LocalUriHandler.current
    var video by remember { mutableStateOf<VideoSession?>(null) }
    var clipPosition by remember { mutableStateOf<Long?>(null) }
    fun close(resume: Boolean) {
        val session = video ?: return
        video = null
        if (player.currentMediaItem?.mediaId == session.mediaId) {
            clipPosition?.let { player.seekTo(it) }
            if (resume && session.resumeAudio) player.play()
        }
        clipPosition = null
    }
    DisposableEffect(player, lifecycle) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_STOP) close(false)
        }
        val listener = object : Player.Listener {
            override fun onPlayWhenReadyChanged(playWhenReady: Boolean, reason: Int) {
                if (playWhenReady) close(false)
            }
        }
        lifecycle.addObserver(observer)
        player.addListener(listener)
        onDispose {
            lifecycle.removeObserver(observer)
            player.removeListener(listener)
            close(lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED))
        }
    }
    Column(Modifier.fillMaxSize().statusBarsPadding(), horizontalAlignment = Alignment.CenterHorizontally) {
        SingleChoiceSegmentedButtonRow {
            SegmentedButton(selected = video == null, onClick = { close(true) },
                shape = SegmentedButtonDefaults.itemShape(0, 2), icon = {}) {
                Text(stringResource(R.string.omo_return_to_song))
            }
            SegmentedButton(selected = video != null, onClick = {
                if (video == null && player.currentMediaItem?.mediaId == videoId) {
                    clipPosition = null
                    video = VideoSession(videoId, player.currentPosition.coerceAtLeast(0) / 1000, player.playWhenReady)
                    player.pause()
                }
            }, shape = SegmentedButtonDefaults.itemShape(1, 2), icon = {}) {
                Text(stringResource(R.string.filter_videos))
            }
        }
        Box(Modifier.fillMaxWidth().weight(1f), contentAlignment = Alignment.Center) {
            val session = video
            if (session == null) artwork()
            else {
                var attempt by remember(session) { mutableStateOf(0) }
                var lookupFailed by remember(session) { mutableStateOf(false) }
                val targetId by produceState<String?>(null, session, attempt) {
                    value = null
                    lookupFailed = false
                    val counterpart = try {
                        withTimeoutOrNull(9_500) {
                            YouTube.videoCounterpart(videoId, metadata.title, metadata.artists.map { it.name }).orEmpty()
                        }
                            ?: throw java.io.IOException("Video lookup timed out")
                    } catch (cancelled: CancellationException) {
                        throw cancelled
                    } catch (_: Exception) {
                        lookupFailed = true
                        null
                    }
                    value = counterpart?.takeIf(youtubeId::matches).orEmpty()
                }
                val target = targetId
                // Album tracks and their official videos can have different intros and cuts.
                val clipStart = if (target == videoId) session.startSeconds else 0L
                var web by remember(session) { mutableStateOf<WebView?>(null) }

                var embedFailed by remember(attempt, target) { mutableStateOf(false) }
                var embedReady by remember(attempt, target) { mutableStateOf(false) }
                LaunchedEffect(web, target, attempt) {
                    val view = web ?: return@LaunchedEffect
                    var emptyChecks = 0
                    while (true) {
                        view.evaluateJavascript(
                            "window.omoPlaybackStatus ? window.omoPlaybackStatus() : -1",
                        ) { result ->
                            val time = result.toLongOrNull() ?: -1L
                            if (time >= 0) {
                                embedReady = true
                                emptyChecks = 0
                                if (target == videoId && time > 0) clipPosition = time
                            } else if (time == -2L || ++emptyChecks >= 40) embedFailed = true
                        }
                        delay(500)
                    }
                }
                Column(Modifier.fillMaxWidth().padding(horizontal = 12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center) {
                    if (target == null) {
                        CircularProgressIndicator(
                            Modifier.align(Alignment.CenterHorizontally).padding(24.dp),
                        )
                    } else if (target.isEmpty() || embedFailed) {
                        if (lookupFailed || embedFailed) {
                            Text(stringResource(R.string.omo_clip_error), Modifier.padding(horizontal = 20.dp))
                            TextButton(onClick = { attempt++ }) { Text(stringResource(R.string.retry)) }
                        } else Text(stringResource(R.string.omo_no_clip), Modifier.padding(20.dp))
                        TextButton(onClick = { close(false); uriHandler.openUri("https://www.youtube.com/watch?v=${target.ifEmpty { videoId }}") }) {
                            Text(stringResource(R.string.omo_open_youtube))
                        }
                    } else Box(contentAlignment = Alignment.Center) {
                        AndroidView(
                        modifier = Modifier.fillMaxWidth().aspectRatio(16f / 9f).clip(RoundedCornerShape(16.dp)),
                        factory = { context ->
                            WebView(context).apply {
                                web = this
                                setBackgroundColor(android.graphics.Color.BLACK)
                                settings.javaScriptEnabled = true
                                settings.domStorageEnabled = true
                                settings.allowFileAccess = false
                                settings.allowContentAccess = false
                                settings.mediaPlaybackRequiresUserGesture = false
                                webViewClient = object : WebViewClient() {
                                    override fun onReceivedError(view: WebView, request: WebResourceRequest,
                                        error: android.webkit.WebResourceError) {
                                        if (request.isForMainFrame) embedFailed = true
                                    }
                                    override fun onReceivedHttpError(view: WebView, request: WebResourceRequest,
                                        response: android.webkit.WebResourceResponse) {
                                        if (request.isForMainFrame) embedFailed = true
                                    }
                                    override fun shouldOverrideUrlLoading(
                                        view: WebView,
                                        request: WebResourceRequest,
                                    ): Boolean = request.isForMainFrame
                                }
                                val origin = "https://${context.packageName}"
                                loadDataWithBaseURL(origin, playerPage(origin, target, clipStart), "text/html", "UTF-8", null)
                            }
                        },
                        onRelease = { view ->
                            web = null
                            view.stopLoading()
                            view.onPause()
                            view.destroy()
                        },
                        )
                        if (!embedReady) CircularProgressIndicator()
                    }
                }
            }
        }
    }
}

private fun playerPage(origin: String, id: String, seconds: Long) = """
    <!doctype html><html><head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <meta name="referrer" content="strict-origin-when-cross-origin">
      <style>html,body,#clip{margin:0;width:100%;height:100%;background:#000}iframe{border:0}</style>
    </head><body>
      <iframe id="clip" title="YouTube" allow="autoplay; encrypted-media; picture-in-picture"
        src="https://www.youtube.com/embed/$id?enablejsapi=1&amp;origin=$origin&amp;start=$seconds&amp;playsinline=1&amp;autoplay=1&amp;fs=0"></iframe>
      <script>
        let player, ready = false, failed = false;
        function onYouTubeIframeAPIReady() {
          player = new YT.Player('clip', {events: {
            onReady: () => { ready = true; },
            onError: () => { failed = true; }
          }});
        }
        function omoPlaybackStatus() {
          if (failed) return -2;
          return ready ? Math.floor((player.getCurrentTime() || 0) * 1000) : -1;
        }
      </script>
      <script src="https://www.youtube.com/iframe_api"></script>
    </body></html>
""".trimIndent()

private data class VideoSession(
    val mediaId: String,
    val startSeconds: Long,
    val resumeAudio: Boolean,
)
