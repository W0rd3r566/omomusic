package com.zionhuang.innertube

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.jsonObject

data class OmoChannel(
    val name: String,
    val byline: String?,
    val channelHandle: String?,
    val thumbnailUrl: String?,
    val isSelected: Boolean,
    val signinUrl: String?,
    val pageId: String?,
    val dataSyncId: String?,
)

internal fun JsonObject.parseAccountsListFallback(): List<OmoChannel> {
    val accounts = mutableListOf<OmoChannel>()
    collectAccountItems(this, accounts)
    return accounts
}

private fun collectAccountItems(
    element: JsonElement,
    accounts: MutableList<OmoChannel>,
) {
    when (element) {
        is JsonObject -> {
            val renderer = element["accountItem"] as? JsonObject ?: element["accountItemRenderer"] as? JsonObject
            renderer?.toAccount()?.let(accounts::add)
            element.values.forEach { collectAccountItems(it, accounts) }
        }

        is JsonArray -> {
            element.forEach { collectAccountItems(it, accounts) }
        }

        else -> {}
    }
}

private fun JsonObject.toAccount(): OmoChannel? {
    val name = textFromRuns("accountName") ?: textFromRuns("channelHandle") ?: textFromRuns("accountByline") ?: return null
    val endpoint = findSelectActiveIdentityEndpoint(this)
    return OmoChannel(
        name = name,
        byline = textFromRuns("accountByline"),
        channelHandle = textFromRuns("channelHandle"),
        thumbnailUrl = thumbnailUrl(),
        isSelected = (this["isSelected"] as? JsonPrimitive)?.contentOrNull?.toBoolean() ?: false,
        signinUrl = endpoint?.tokenValue("accountSigninToken", "signinUrl"),
        pageId = endpoint?.tokenValue("pageIdToken", "pageId"),
        dataSyncId = endpoint?.tokenValue("datasyncIdToken", "datasyncIdToken"),
    )
}

private fun JsonObject.textFromRuns(key: String): String? {
    val text = this[key] as? JsonObject ?: return null
    return (text["runs"] as? JsonArray)
        ?.mapNotNull { ((it as? JsonObject)?.get("text") as? JsonPrimitive)?.contentOrNull }
        ?.joinToString("")
        ?.takeIf(String::isNotBlank)
        ?: (text["simpleText"] as? JsonPrimitive)?.contentOrNull?.takeIf(String::isNotBlank)
}

private fun JsonObject.thumbnailUrl(): String? =
    ((this["accountPhoto"] as? JsonObject)?.get("thumbnails") as? JsonArray)
        ?.lastOrNull()
        ?.let { ((it as? JsonObject)?.get("url") as? JsonPrimitive)?.contentOrNull }

private fun JsonObject.tokenValue(
    tokenKey: String,
    valueKey: String,
): String? =
    (this["supportedTokens"] as? JsonArray)
        ?.firstNotNullOfOrNull { token ->
            (((token as? JsonObject)?.get(tokenKey) as? JsonObject)?.get(valueKey) as? JsonPrimitive)?.contentOrNull
        }

private fun findSelectActiveIdentityEndpoint(element: JsonElement): JsonObject? =
    when (element) {
        is JsonObject -> {
            element["selectActiveIdentityEndpoint"] as? JsonObject
                ?: element.values.firstNotNullOfOrNull(::findSelectActiveIdentityEndpoint)
        }

        is JsonArray -> {
            element.firstNotNullOfOrNull(::findSelectActiveIdentityEndpoint)
        }

        else -> {
            null
        }
    }
