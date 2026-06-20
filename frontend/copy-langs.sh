#!/bin/bash

echo "Cleaning old translations."
rm -rf ../allianceauth_pve/static/allianceauth_pve/react/i18n

echo "Copying new translations."
# copy the image assets to the correct place.
cp -r i18n ../allianceauth_pve/static/allianceauth_pve/react/i18n
echo "Translations copied successfully."
