/*
 * omo Black — Copyright (C) 2026 W0rd3r566 and contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
package dev.w0rd3r.omo.patches

import app.revanced.patcher.patch.resourcePatch
import org.w3c.dom.Element

/**
 * Optional near-black palette. Only touches existing named colors; a Music
 * version without these resources is left unchanged.
 */
@Suppress("unused")
val omoBlackThemePatch = resourcePatch(
    name = "omo Black",
    description = "Use the clean black and graphite color palette of omo.",
) {
    compatibleWith("com.google.android.apps.youtube.music"())

    execute {
        val colors = get("res/values/colors.xml")
        if (!colors.exists()) return@execute
        val replacements = mapOf(
            "yt_black0" to "#FF282828",
            "yt_black1" to "#FF202020",
            "yt_black2" to "#FF181818",
            "yt_black3" to "#FF0F0F0F",
            "yt_black4" to "#FF030303",
            "yt_black_pure" to "#FF000000",
        )
        document("res/values/colors.xml").use { doc ->
            val nodes = doc.getElementsByTagName("color")
            for (i in 0 until nodes.length) {
                val element = nodes.item(i) as? Element ?: continue
                replacements[element.getAttribute("name")]?.let { color ->
                    element.textContent = color
                }
            }
        }
    }
}
