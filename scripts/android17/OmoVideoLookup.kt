package com.zionhuang.innertube

import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.contentOrNull

private const val AUDIO_TRACK = "MUSIC_VIDEO_TYPE_ATV"
private val idPattern = Regex("[A-Za-z0-9_-]{11}")

internal data class VideoMatch(val id: String? = null, val audioTrack: Boolean = false)

internal fun findVideoMatch(response: JsonObject, requestedId: String): VideoMatch {
    var isAudioTrack = false
    for (row in response.objectsNamed("playlistPanelVideoWrapperRenderer")) {
        val primary = row.obj("primaryRenderer")?.obj("playlistPanelVideoRenderer")
        if (primary?.videoId() != requestedId) continue
        val type = primary.videoType()
        if (type.isVideo()) return VideoMatch(requestedId)
        isAudioTrack = isAudioTrack || type == AUDIO_TRACK
        val counterpart = row["counterpart"] ?: continue
        for (entry in counterpart.objectsNamed("playlistPanelVideoRenderer")) {
            val id = entry.videoId() ?: continue
            if (id != requestedId && entry.videoType() != AUDIO_TRACK && entry["unplayableText"] == null) {
                return VideoMatch(id)
            }
        }
    }
    for (entry in response.objectsNamed("playlistPanelVideoRenderer")) {
        if (entry.videoId() != requestedId) continue
        val type = entry.videoType()
        if (type.isVideo()) return VideoMatch(requestedId)
        isAudioTrack = isAudioTrack || type == AUDIO_TRACK
    }
    return VideoMatch(audioTrack = isAudioTrack)
}

private fun JsonObject.obj(key: String) = this[key] as? JsonObject
private fun JsonObject.text(key: String) = (this[key] as? JsonPrimitive)?.contentOrNull

private fun JsonObject.videoId() =
    (text("videoId") ?: obj("navigationEndpoint")?.obj("watchEndpoint")?.text("videoId"))
        ?.takeIf(idPattern::matches)

private fun JsonObject.videoType() =
    obj("navigationEndpoint")?.obj("watchEndpoint")
        ?.obj("watchEndpointMusicSupportedConfigs")?.obj("watchEndpointMusicConfig")?.text("musicVideoType")
        ?: text("musicVideoType")

private fun String?.isVideo() = this == "MUSIC_VIDEO_TYPE_OMV" || this == "MUSIC_VIDEO_TYPE_UGC"

private fun JsonElement.objectsNamed(key: String): Sequence<JsonObject> = sequence {
    when (val value = this@objectsNamed) {
        is JsonObject -> {
            value.obj(key)?.let { yield(it) }
            for (child in value.values) yieldAll(child.objectsNamed(key))
        }
        is JsonArray -> for (child in value) yieldAll(child.objectsNamed(key))
        else -> Unit
    }
}
