#!/usr/bin/env bash
set -euo pipefail
umask 077

repo=W0rd3r566/omomusic
signing_dir="${XDG_DATA_HOME:-$HOME/.local/share}/omo-music-signing"
keystore="$signing_dir/omo-release.p12"
password="$signing_dir/password"

gh auth status --hostname github.com
configured_secrets=$(gh secret list --repo "$repo" --app actions --json name --jq '.[].name')

if [[ ! -f "$keystore" && ! -f "$password" ]]; then
    if grep -Eq '^OMO_RELEASE_(KEYSTORE|PASSWORD)$' <<< "$configured_secrets"; then
        echo "Restore the original signing files before configuring this repository." >&2
        exit 1
    fi
    signing_parent=$(dirname "$signing_dir")
    mkdir -p "$signing_parent"
    temporary_dir=$(mktemp -d "$signing_parent/.omo-music-signing.XXXXXX")
    trap 'rm -rf -- "$temporary_dir"' EXIT
    openssl rand -hex 32 > "$temporary_dir/password"
    keytool -genkeypair -storetype PKCS12 -keystore "$temporary_dir/omo-release.p12" \
        -storepass:file "$temporary_dir/password" -alias omo-release \
        -keyalg RSA -keysize 3072 -validity 10000 -dname "CN=Omo music"
    mv -T "$temporary_dir" "$signing_dir"
fi

keytool -list -storetype PKCS12 -keystore "$keystore" -storepass:file "$password" \
    -alias omo-release >/dev/null
base64 -w0 "$keystore" | gh secret set OMO_RELEASE_KEYSTORE --repo "$repo"
tr -d '\n' < "$password" | gh secret set OMO_RELEASE_PASSWORD --repo "$repo"
printf 'Signing configured. Keep a private backup of %s\n' "$signing_dir"
