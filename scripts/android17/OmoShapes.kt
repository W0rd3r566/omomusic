package com.dd3boh.outertune.ui.omo

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.datastore.preferences.core.intPreferencesKey
import com.dd3boh.outertune.R
import com.dd3boh.outertune.utils.rememberPreference
import kotlin.math.roundToInt

internal enum class OmoShape(keyName: String, val initial: Int, val label: Int) {
    Dock("omo_dock_roundness", 50, R.string.omo_dock_shape),
    Buttons("omo_controls_roundness", 50, R.string.omo_controls_shape);
    val key = intPreferencesKey(keyName)
}

@Composable
internal fun omoShape(part: OmoShape): RoundedCornerShape {
    val percent by rememberPreference(part.key, part.initial)
    return RoundedCornerShape(percent.coerceIn(0, 50))
}

@Composable
internal fun OmoShapeSettings() {
    Column(Modifier.fillMaxWidth().padding(horizontal = 16.dp)) {
        for (part in OmoShape.entries) {
            var saved by rememberPreference(part.key, part.initial)
            var drag by remember(part) { mutableStateOf<Float?>(null) }
            Text(stringResource(part.label, (drag?.roundToInt() ?: saved) * 2))
            Slider(value = drag ?: saved.toFloat(), valueRange = 0f..50f,
                onValueChange = { drag = it },
                onValueChangeFinished = {
                    drag?.let { saved = it.roundToInt() }
                    drag = null
                })
        }
    }
}
