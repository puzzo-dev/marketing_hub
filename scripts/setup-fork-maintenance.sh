#!/bin/bash
# Setup script for fork maintenance workflow
# Run this once to configure your repository

set -e  # Exit on error

echo "🔧 Marketing Hub Fork Maintenance Setup"
echo "========================================"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not a git repository"
    exit 1
fi

# Get current directory name
REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
echo "📦 Repository: $REPO_NAME"
echo ""

# Step 1: Check current remotes
echo "Step 1: Checking current remotes..."
echo "-----------------------------------"
git remote -v
echo ""

# Step 2: Add upstream remote
echo "Step 2: Adding upstream remote..."
echo "---------------------------------"
read -p "Enter upstream repository URL (e.g., https://github.com/upstream-owner/repo.git): " UPSTREAM_URL

if [ -z "$UPSTREAM_URL" ]; then
    echo "❌ No URL provided. Exiting."
    exit 1
fi

# Check if upstream already exists
if git remote | grep -q "^upstream$"; then
    echo "⚠️  Upstream remote already exists. Updating URL..."
    git remote set-url upstream "$UPSTREAM_URL"
else
    echo "➕ Adding upstream remote..."
    git remote add upstream "$UPSTREAM_URL"
fi

echo "✅ Upstream remote configured"
git remote -v | grep upstream
echo ""

# Step 3: Fetch upstream
echo "Step 3: Fetching upstream..."
echo "----------------------------"
git fetch upstream
echo "✅ Upstream fetched"
echo ""

# Step 4: Determine upstream branch
echo "Step 4: Detecting upstream branches..."
echo "--------------------------------------"
UPSTREAM_BRANCHES=$(git branch -r | grep upstream/ | sed 's/.*upstream\///' | grep -v HEAD)
echo "Available upstream branches:"
echo "$UPSTREAM_BRANCHES"
echo ""

read -p "Enter upstream branch name to track (usually 'main', 'master', or 'develop'): " UPSTREAM_BRANCH
if [ -z "$UPSTREAM_BRANCH" ]; then
    UPSTREAM_BRANCH="develop"
    echo "Using default: $UPSTREAM_BRANCH"
fi

# Verify branch exists
if ! git show-ref --verify --quiet "refs/remotes/upstream/$UPSTREAM_BRANCH"; then
    echo "❌ Branch upstream/$UPSTREAM_BRANCH does not exist"
    exit 1
fi

echo "✅ Will track: upstream/$UPSTREAM_BRANCH"
echo ""

# Step 5: Create local tracking branch for upstream
echo "Step 5: Creating local tracking branch..."
echo "-----------------------------------------"
if git show-ref --verify --quiet "refs/heads/${UPSTREAM_BRANCH}-upstream"; then
    echo "⚠️  Branch ${UPSTREAM_BRANCH}-upstream already exists. Resetting to upstream..."
    git branch -f "${UPSTREAM_BRANCH}-upstream" "upstream/$UPSTREAM_BRANCH"
else
    git branch "${UPSTREAM_BRANCH}-upstream" "upstream/$UPSTREAM_BRANCH"
fi
echo "✅ Created/updated: ${UPSTREAM_BRANCH}-upstream"
echo ""

# Step 6: Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Step 6: Current working branch: $CURRENT_BRANCH"
echo "------------------------------------------------"
echo ""

# Step 7: Show current state
echo "Step 7: Analyzing repository state..."
echo "-------------------------------------"
echo ""
echo "📊 Your patches (commits not in upstream):"
git log "upstream/$UPSTREAM_BRANCH..$CURRENT_BRANCH" --oneline --color=always || echo "  None (you're in sync with upstream)"
echo ""

# Step 8: Offer to rebase
echo "Step 8: Initial rebase (optional)..."
echo "------------------------------------"
COMMITS_BEHIND=$(git rev-list --count "$CURRENT_BRANCH..upstream/$UPSTREAM_BRANCH" 2>/dev/null || echo "0")
COMMITS_AHEAD=$(git rev-list --count "upstream/$UPSTREAM_BRANCH..$CURRENT_BRANCH" 2>/dev/null || echo "0")

echo "📈 Status:"
echo "  - You are $COMMITS_BEHIND commits behind upstream"
echo "  - You have $COMMITS_AHEAD local patches"
echo ""

if [ "$COMMITS_BEHIND" -gt 0 ] && [ "$COMMITS_AHEAD" -gt 0 ]; then
    read -p "⚠️  Rebase your $COMMITS_AHEAD patches on top of upstream now? (y/N): " DO_REBASE
    if [[ "$DO_REBASE" =~ ^[Yy]$ ]]; then
        echo "🔄 Rebasing..."
        if git rebase "upstream/$UPSTREAM_BRANCH"; then
            echo "✅ Rebase successful!"
            echo ""
            read -p "Push to origin with --force-with-lease? (y/N): " DO_PUSH
            if [[ "$DO_PUSH" =~ ^[Yy]$ ]]; then
                git push origin "$CURRENT_BRANCH" --force-with-lease
                echo "✅ Pushed to origin"
            else
                echo "⚠️  Remember to push later: git push origin $CURRENT_BRANCH --force-with-lease"
            fi
        else
            echo "❌ Rebase failed. Conflicts detected."
            echo "Run 'git rebase --abort' to cancel, or resolve conflicts manually."
            echo "See FORK-MAINTENANCE.md for conflict resolution guide."
            exit 1
        fi
    else
        echo "⏭️  Skipped rebase"
    fi
elif [ "$COMMITS_BEHIND" -eq 0 ]; then
    echo "✅ Already up to date with upstream"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📖 Next steps:"
echo "  1. Read FORK-MAINTENANCE.md for detailed workflow"
echo "  2. Set up GitHub Actions automation (optional)"
echo "  3. Run daily sync: git fetch upstream && git rebase upstream/$UPSTREAM_BRANCH"
echo ""
echo "🔗 Remotes configured:"
git remote -v
echo ""
echo "🌿 Branches:"
echo "  - upstream/$UPSTREAM_BRANCH (read-only reference)"
echo "  - ${UPSTREAM_BRANCH}-upstream (local mirror)"
echo "  - $CURRENT_BRANCH (your working branch)"
echo ""
echo "📝 Quick reference:"
echo "  git log ${UPSTREAM_BRANCH}-upstream..$CURRENT_BRANCH  # See your patches"
echo "  git fetch upstream && git rebase ${UPSTREAM_BRANCH}-upstream  # Sync upstream"
echo ""
