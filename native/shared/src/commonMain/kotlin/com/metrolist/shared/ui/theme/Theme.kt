package com.metrolist.shared.ui.theme

import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.MaterialExpressiveTheme
import androidx.compose.material3.MotionScheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.Color
import com.metrolist.shared.ui.haptics.MetrolistHapticsProvider

private val LightColors =
    lightColorScheme(
        primary = Color(0xFF216580),
        onPrimary = Color.White,
        secondary = Color(0xFF4D7182),
        onSecondary = Color.White,
        background = Color(0xFFFAF9F7),
        onBackground = Color(0xFF1D2024),
        surface = Color.White,
        onSurface = Color(0xFF1D2024),
        error = Color(0xFFB00020),
        onError = Color.White,
    )

private val DarkColors =
    darkColorScheme(
        primary = Color(0xFFA7D7FF),
        onPrimary = Color.Black,
        secondary = Color(0xFFB5CBD9),
        onSecondary = Color.Black,
        background = Color(0xFF0A0B0C),
        onBackground = Color(0xFFE8EBEF),
        surface = Color(0xFF13161A),
        onSurface = Color(0xFFE8EBEF),
        error = Color(0xFFCF6679),
        onError = Color.Black,
    )

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun MetrolistTheme(
    useDarkTheme: Boolean = false,
    content: @Composable () -> Unit,
) {
    val colors = if (useDarkTheme) DarkColors else LightColors

    val motionScheme = remember { MotionScheme.expressive() }
    MaterialExpressiveTheme(
        colorScheme = animateColorScheme(colors, motionScheme),
        motionScheme = motionScheme,
        typography = Typography(),
        content = { MetrolistHapticsProvider(content) },
    )
}
