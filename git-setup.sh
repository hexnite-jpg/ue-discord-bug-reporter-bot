#!/bin/bash
# Initialize git repository and make first commit

cd /home/botuser/discord_bot

# Initialize git if not already done
if [ ! -d .git ]; then
    git init
    git branch -M main
fi

# Add all files (gitignore will handle exclusions)
git add .

# Show what will be committed
echo "Files to be committed:"
git status --short

# Make first commit
git commit -m "Initial commit: Discord Bug Reporter Management Bot for Unreal Engine

- Webhook-based bug report processing
- Reaction-based status management
- Thread organization with auto-archiving
- Player ID blocking system
- Statistics and assignment tracking
- Complete installation tooling"

echo ""
echo "Next steps:"
echo "1. Create repo on GitHub (e.g., discord-ue-bug-tracker)"
echo "2. git remote add origin git@github.com:YOUR_USERNAME/discord-ue-bug-tracker.git"
echo "3. git push -u origin main"
