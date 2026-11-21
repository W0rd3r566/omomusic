/*
 * omo Branding — Copyright (C) 2026 W0rd3r566 and contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * Independent resource patch for a user-provided YouTube Music installation.
 * No authentication, paid features, DRM, or media fetching code.
 */
package dev.w0rd3r.omo.patches

import app.revanced.patcher.patch.PatchException
import app.revanced.patcher.patch.resourcePatch
import org.w3c.dom.Element

private const val ANDROID = "http://schemas.android.com/apk/res/android"
private const val MUSIC_PACKAGE = "com.google.android.apps.youtube.music"

private val brandedResources = listOf(
    "drawable/omo_foreground.xml",
    "drawable/omo_monochrome.xml",
    "mipmap-anydpi/omo_launcher.xml",
    "mipmap-anydpi-v26/omo_launcher.xml",
    "values/omo_colors.xml",
)

@Suppress("unused")
val omoBrandingPatch = resourcePatch(
    name = "omo Branding",
    description = "Use the omo name, rounded monochrome/adaptive icon and blue play mark.",
) {
    compatibleWith(MUSIC_PACKAGE())

    execute {
        // Copy original omo vector resources, without Google assets or app code.
        for (relative in brandedResources) {
            val resource = "omo/" + relative
            val bytes = OmoBrandingResources::class.java.classLoader
                ?.getResourceAsStream(resource)?.use { it.readBytes() }
                ?: throw PatchException("Missing resource: " + resource)
            val output = get("res/" + relative)
            output.parentFile?.mkdirs()
            output.writeBytes(bytes)
        }
        document("AndroidManifest.xml").use { manifest ->
            val app = manifest.getElementsByTagName("application").item(0) as? Element
                ?: throw PatchException("Missing application element")
            app.setOmoIdentity()
            for (type in arrayOf("activity", "activity-alias")) {
                val nodes = app.getElementsByTagName(type)
                for (i in 0 until nodes.length) {
                    val element = nodes.item(i) as? Element ?: continue
                    val filters = element.getElementsByTagName("intent-filter")
                    for (j in 0 until filters.length) {
                        val filter = filters.item(j) as? Element ?: continue
                        if (filter.hasIntentValue("action", "android.intent.action.MAIN") &&
                            filter.hasIntentValue("category", "android.intent.category.LAUNCHER")) {
                            element.setOmoIdentity()
                            break
                        }
                    }
                }
            }
        }
    }
}

private object OmoBrandingResources

private fun Element.setOmoIdentity() {
    setAttributeNS(ANDROID, "android:label", "omo")
    setAttributeNS(ANDROID, "android:icon", "@mipmap/omo_launcher")
    setAttributeNS(ANDROID, "android:roundIcon", "@mipmap/omo_launcher")
}

private fun Element.hasIntentValue(tag: String, name: String): Boolean {
    val elements = getElementsByTagName(tag)
    for (i in 0 until elements.length) {
        val node = elements.item(i) as? Element ?: continue
        if (node.getAttributeNS(ANDROID, "name") == name) return true
    }
    return false
}
