/*
 * omo Music design presets — Copyright (C) 2026 W0rd3r566.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
package com.dd3boh.outertune.ui.theme

import androidx.compose.ui.graphics.Color

/** User-selected colors are stored by enum name in DataStore. */
enum class OmoAccent(
    val title: String,
    val argb: Long,
) {
    SKY("Sky", 0xFFA7D7FF),
    MINT("Mint", 0xFF98E8D0),
    LAVENDER("Lavender", 0xFFD1C4FF),
    CORAL("Coral", 0xFFFFB4A4),
    AMBER("Amber", 0xFFFFDA93);

    val color: Color get() = Color(argb)
}

enum class OmoCorners(
    val title: String,
    val smallDp: Int,
    val mediumDp: Int,
    val largeDp: Int,
    val extraLargeDp: Int,
) {
    SOFT("Soft", 8, 12, 20, 26),
    EXPRESSIVE("Expressive", 12, 20, 28, 36),
    ROUND("Round", 20, 28, 36, 48);
}
