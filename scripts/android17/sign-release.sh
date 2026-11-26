#!/usr/bin/env bash
set -euo pipefail
umask 077

unsigned_apk=${1:?Provide the unsigned APK}
signed_apk=${2:?Provide the signed APK path}
build_tools="${ANDROID_HOME:?Set ANDROID_HOME}/build-tools/36.0.0"
: "${OMO_RELEASE_KEYSTORE:?Missing release keystore}"
: "${OMO_RELEASE_PASSWORD:?Missing release keystore password}"

temporary_dir=$(mktemp -d)
trap 'rm -rf -- "$temporary_dir"' EXIT
printf '%s' "$OMO_RELEASE_KEYSTORE" | base64 --decode > "$temporary_dir/omo-release.p12"

"$build_tools/zipalign" -P 16 4 "$unsigned_apk" "$temporary_dir/aligned.apk"
"$build_tools/apksigner" sign \
    --ks "$temporary_dir/omo-release.p12" --ks-type PKCS12 --ks-key-alias omo-release \
    --ks-pass env:OMO_RELEASE_PASSWORD --v4-signing-enabled false \
    --out "$temporary_dir/signed.apk" "$temporary_dir/aligned.apk"
"$build_tools/apksigner" verify --verbose --print-certs "$temporary_dir/signed.apk"

badging=$("$build_tools/aapt" dump badging "$temporary_dir/signed.apk")
grep -Fq "package: name='dev.w0rd3r.omomusic'" <<< "$badging"
grep -Fxq "application-label:'Omo music'" <<< "$badging"
grep -E "^native-code:.*'arm64-v8a'" <<< "$badging"
mv "$temporary_dir/signed.apk" "$signed_apk"
