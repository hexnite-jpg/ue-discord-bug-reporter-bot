#!/bin/bash

# Create a distribution package of the Discord Bug Tracker Bot

set -e

VERSION="1.0.0"
PACKAGE_NAME="discord-bug-tracker-v${VERSION}"
DIST_DIR="dist"

echo "Creating distribution package: $PACKAGE_NAME"
echo ""

# Create dist directory
mkdir -p "$DIST_DIR/$PACKAGE_NAME"

# Copy essential files
echo "Copying files..."
cp bot.py "$DIST_DIR/$PACKAGE_NAME/"
cp requirements.txt "$DIST_DIR/$PACKAGE_NAME/"
cp install.sh "$DIST_DIR/$PACKAGE_NAME/"
cp .env.example "$DIST_DIR/$PACKAGE_NAME/"
cp INSTALL.md "$DIST_DIR/$PACKAGE_NAME/"
cp README.md "$DIST_DIR/$PACKAGE_NAME/"
cp QUICKREF.md "$DIST_DIR/$PACKAGE_NAME/"
cp SERVER_ADMIN_GUIDE.md "$DIST_DIR/$PACKAGE_NAME/"
cp PLUGIN_INTEGRATION.md "$DIST_DIR/$PACKAGE_NAME/"
cp INVITE.md "$DIST_DIR/$PACKAGE_NAME/"

# Create example config files
touch "$DIST_DIR/$PACKAGE_NAME/guild_config.json"
echo '{}' > "$DIST_DIR/$PACKAGE_NAME/guild_config.json"

touch "$DIST_DIR/$PACKAGE_NAME/blocked_ids.json"
echo '{}' > "$DIST_DIR/$PACKAGE_NAME/blocked_ids.json"

# Create archive
echo "Creating archive..."
cd "$DIST_DIR"
tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"
zip -r "${PACKAGE_NAME}.zip" "$PACKAGE_NAME" > /dev/null

echo ""
echo "✓ Package created successfully!"
echo ""
echo "Distribution files:"
echo "  - ${DIST_DIR}/${PACKAGE_NAME}.tar.gz"
echo "  - ${DIST_DIR}/${PACKAGE_NAME}.zip"
echo ""
echo "Users can extract and run: ./install.sh"
