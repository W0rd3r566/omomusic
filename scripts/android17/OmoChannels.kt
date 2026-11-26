package com.dd3boh.outertune.ui.omo

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Person
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.datastore.preferences.core.edit
import coil3.compose.AsyncImage
import com.dd3boh.outertune.LocalSyncUtils
import com.dd3boh.outertune.R
import com.dd3boh.outertune.constants.*
import com.dd3boh.outertune.ui.component.PreferenceEntry
import com.dd3boh.outertune.utils.dataStore
import com.zionhuang.innertube.OmoChannel
import com.zionhuang.innertube.YouTube
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.launch

@Composable
internal fun OmoChannels(cookie: String, handle: String) {
    var open by remember(cookie) { mutableStateOf(false) }
    PreferenceEntry(
        title = { Text(stringResource(R.string.omo_channels)) },
        description = handle.takeIf { it.isNotBlank() },
        icon = { Icon(Icons.Rounded.Person, null) },
        onClick = { open = true },
    )
    if (!open) return
    val context = LocalContext.current
    val sync = LocalSyncUtils.current
    val scope = rememberCoroutineScope()
    var channels by remember { mutableStateOf<List<OmoChannel>>(emptyList()) }
    var busy by remember { mutableStateOf(true) }
    var failed by remember { mutableStateOf(false) }
    var attempt by remember { mutableIntStateOf(0) }
    LaunchedEffect(cookie, attempt) {
        busy = true
        failed = false
        try {
            channels = YouTube.omoChannels()
            failed = channels.isEmpty()
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Exception) {
            failed = true
        } finally {
            busy = false
        }
    }
    AlertDialog(
        onDismissRequest = { open = false },
        title = { Text(stringResource(R.string.omo_channels)) },
        text = {
            Column(Modifier.verticalScroll(rememberScrollState())) {
                if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())
                if (failed) Text(stringResource(R.string.omo_channel_error))
                channels.forEach { channel ->
                    val current = handle.isNotBlank() && handle.equals(channel.channelHandle, true)
                    Row(
                        modifier = Modifier.fillMaxWidth().clickable(enabled = !busy && !current) {
                            busy = true
                            failed = false
                            scope.launch {
                                try {
                                    val identity = YouTube.omoIdentity(channel)
                                    context.dataStore.edit {
                                        check(it[InnerTubeCookieKey] == cookie)
                                        it[DataSyncIdKey] = identity.first
                                        it[AccountNameKey] = identity.second.name
                                        it[AccountChannelHandleKey] = identity.second.channelHandle.orEmpty()
                                        identity.second.email?.let { email -> it[AccountEmailKey] = email }
                                    }
                                    YouTube.dataSyncId = identity.first
                                    sync.startManualSync()
                                    open = false
                                } catch (cancelled: CancellationException) {
                                    throw cancelled
                                } catch (_: Exception) {
                                    failed = true
                                } finally {
                                    busy = false
                                }
                            }
                        }.padding(vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                    ) {
                        AsyncImage(channel.thumbnailUrl, null, Modifier.size(40.dp).clip(CircleShape))
                        Column(Modifier.weight(1f)) {
                            Text(channel.name, style = MaterialTheme.typography.titleMedium)
                            (channel.channelHandle ?: channel.byline)?.let { Text(it, style = MaterialTheme.typography.bodySmall) }
                        }
                        if (current) RadioButton(selected = true, onClick = null)
                    }
                }
            }
        },
        confirmButton = { TextButton(onClick = { open = false }) { Text(stringResource(android.R.string.cancel)) } },
        dismissButton = { if (failed) TextButton(onClick = { attempt++ }) { Text(stringResource(R.string.retry)) } },
    )
}
