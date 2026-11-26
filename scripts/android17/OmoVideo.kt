/*
 * Copyright (C) 2026 W0rd3r566
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
package com.dd3boh.outertune.ui.omo

import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.media3.common.Player
import com.dd3boh.outertune.R
import com.dd3boh.outertune.models.MediaMetadata

private val youtubeId = Regex("[A-Za-z0-9_-]{11}")

@Composable
internal fun OmoVideoAction(metadata: MediaMetadata?, player: Player, modifier: Modifier = Modifier) {
    val videoId = metadata?.takeUnless { it.isLocal }?.id?.takeIf(youtubeId::matches) ?: return
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    val uriHandler = LocalUriHandler.current
    var video by remember(player, videoId) { mutableStateOf<VideoSession?>(null) }

    DisposableEffect(lifecycle, player, videoId) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_STOP) video = null
        }
        val playerListener = object : Player.Listener {
            override fun onPlayWhenReadyChanged(playWhenReady: Boolean, reason: Int) {
                if (playWhenReady) video = null
            }
        }
        lifecycle.addObserver(observer)
        player.addListener(playerListener)
        onDispose {
            lifecycle.removeObserver(observer)
            player.removeListener(playerListener)
        }
    }

    FilledTonalButton(
        onClick = {
            val item = player.currentMediaItem ?: return@FilledTonalButton
            video = VideoSession(
                mediaId = item.mediaId,
                startSeconds = player.currentPosition.coerceAtLeast(0) / 1000,
                resumeAudio = player.playWhenReady,
            )
            player.pause()
        },
        modifier = modifier,
    ) {
        Text(stringResource(R.string.filter_videos))
    }

    video?.let { session ->
        fun returnToSong() {
            video = null
            if (session.resumeAudio && player.currentMediaItem?.mediaId == session.mediaId) {
                player.play()
            }
        }

        Dialog(
            onDismissRequest = ::returnToSong,
            properties = DialogProperties(usePlatformDefaultWidth = false),
        ) {
            Surface(
                modifier = Modifier.widthIn(max = 640.dp).fillMaxWidth().padding(horizontal = 12.dp),
                shape = MaterialTheme.shapes.extraLarge,
            ) {
                Column(Modifier.padding(vertical = 8.dp)) {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        TextButton(onClick = ::returnToSong) {
                            Text(stringResource(R.string.omo_return_to_song))
                        }
                        TextButton(onClick = {
                            video = null
                            uriHandler.openUri("https://www.youtube.com/watch?v=$videoId&t=${session.startSeconds}s")
                        }) {
                            Text(stringResource(R.string.omo_open_youtube))
                        }
                    }
                    AndroidView(
                        modifier = Modifier.fillMaxWidth().heightIn(min = 200.dp, max = 270.dp),
                        factory = { context ->
                            WebView(context).apply {
                                settings.javaScriptEnabled = true
                                settings.domStorageEnabled = true
                                settings.allowFileAccess = false
                                settings.allowContentAccess = false
                                settings.mediaPlaybackRequiresUserGesture = true
                                webViewClient = object : WebViewClient() {
                                    override fun shouldOverrideUrlLoading(
                                        view: WebView,
                                        request: WebResourceRequest,
                                    ): Boolean = request.isForMainFrame &&
                                        (request.url.scheme != "https" || request.url.host != "www.youtube.com" ||
                                            request.url.path != "/embed/$videoId")
                                }
                                loadUrl(
                                    "https://www.youtube.com/embed/$videoId?start=${session.startSeconds}&fs=0",
                                    mapOf("Referer" to "https://${context.packageName}"),
                                )
                            }
                        },
                        onRelease = { view ->
                            view.stopLoading()
                            view.onPause()
                            view.destroy()
                        },
                    )
                }
            }
        }
    }
}

private data class VideoSession(
    val mediaId: String,
    val startSeconds: Long,
    val resumeAudio: Boolean,
)
