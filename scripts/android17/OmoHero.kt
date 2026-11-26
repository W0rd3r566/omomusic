/*
 * Copyright (C) 2026 W0rd3r566
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
package com.dd3boh.outertune.ui.omo

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Palette
import androidx.compose.material.icons.rounded.Person
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.dd3boh.outertune.R
import com.dd3boh.outertune.constants.AccountChannelHandleKey
import com.dd3boh.outertune.constants.AccountNameKey
import com.dd3boh.outertune.constants.InnerTubeCookieKey
import com.dd3boh.outertune.utils.rememberPreference
import com.zionhuang.innertube.utils.parseCookieString

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun OmoHero(navController: NavController) {
    val cookie by rememberPreference(InnerTubeCookieKey, "")
    val accountName by rememberPreference(AccountNameKey, "")
    val channelHandle by rememberPreference(AccountChannelHandleKey, "")
    val signedIn = remember(cookie) { "SAPISID" in parseCookieString(cookie) }
    val accountLabel = if (signedIn) {
        channelHandle.ifBlank { accountName }.ifBlank { stringResource(R.string.account) }
    } else {
        stringResource(R.string.login)
    }
    val searchHeight = ButtonDefaults.MediumContainerHeight

    Surface(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
        shape = RoundedCornerShape(topStart = 40.dp, topEnd = 40.dp, bottomStart = 24.dp, bottomEnd = 24.dp),
        color = MaterialTheme.colorScheme.surfaceContainer,
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = "omo",
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.displayMedium.copy(
                        fontWeight = FontWeight.Black,
                        letterSpacing = (-2).sp,
                    ),
                )
                FilledTonalButton(
                    onClick = { navController.navigate("settings/appearance") },
                    shapes = ButtonDefaults.shapes(),
                    contentPadding = PaddingValues(12.dp),
                    modifier = Modifier.heightIn(min = 48.dp),
                ) {
                    Icon(Icons.Rounded.Palette, contentDescription = stringResource(R.string.omo_customize))
                }
                FilledTonalButton(
                    onClick = { navController.navigate(if (signedIn) "account" else "login") },
                    shapes = ButtonDefaults.shapes(),
                    modifier = Modifier.weight(1.6f).heightIn(min = 48.dp),
                    contentPadding = PaddingValues(horizontal = 12.dp),
                ) {
                    Icon(Icons.Rounded.Person, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text(accountLabel, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
            }
            Button(
                onClick = { navController.navigate("search") },
                shapes = ButtonDefaults.shapesFor(searchHeight),
                contentPadding = ButtonDefaults.contentPaddingFor(searchHeight),
                modifier = Modifier.fillMaxWidth().heightIn(min = searchHeight),
            ) {
                Icon(Icons.Rounded.Search, contentDescription = null)
                Spacer(Modifier.width(12.dp))
                Text(stringResource(R.string.search), style = MaterialTheme.typography.titleMedium)
            }
        }
    }
}
