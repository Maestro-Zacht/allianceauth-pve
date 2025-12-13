#!/bin/bash

echo "Cleaning old assets."
rm -rf ../allianceauth_pve/static/allianceauth_pve/react/

echo "Copying new assets."
mkdir -p ../allianceauth_pve/static/allianceauth_pve/react
cp -r dist/static/allianceauth_pve/react ../allianceauth_pve/static/allianceauth_pve
cp -r dist/assets ../allianceauth_pve/static/allianceauth_pve/react/assets

cp dist/.vite/manifest.json ../allianceauth_pve/static/allianceauth_pve/react/manifest.json

echo "Assets copied successfully."
