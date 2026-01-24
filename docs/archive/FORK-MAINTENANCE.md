# Fork Maintenance Workflow

This document describes the rebase-only workflow for maintaining this fork with minimal local patches on top of upstream.

## Repository Structure

```
origin (your fork) → github.com/puzzo-dev/marketing_hub.git
upstream (original) → [upstream-repo-url]
```

## Initial Setup

### 1. Add Upstream Remote

```bash
git remote add upstream https://github.com/[upstream-owner]/[upstream-repo].git
git fetch upstream
```

### 2. Verify Remotes

```bash
git remote -v
# origin    https://github.com/puzzo-dev/marketing_hub.git (fetch)
# origin    https://github.com/puzzo-dev/marketing_hub.git (push)
# upstream  https://github.com/[upstream-owner]/[upstream-repo].git (fetch)
# upstream  https://github.com/[upstream-owner]/[upstream-repo].git (push)
```

### 3. Create Tracking Branches

```bash
# Track upstream's main branch (adjust branch name as needed)
git fetch upstream
git branch -u upstream/develop develop-upstream

# Your working branch (tracks your fork)
git checkout -b develop
git branch -u origin/develop
```

## Branch Strategy

```
upstream/develop     ← Original upstream (never modified)
    ↓
develop-upstream     ← Local tracking of upstream (fast-forward only)
    ↓
develop              ← Your branch with patches (rebase on top)
    ↓
origin/develop       ← Your fork (force-push safe after rebase)
```

### Branch Purposes

- **`upstream/develop`**: Read-only reference to original repo
- **`develop-upstream`**: Local mirror of upstream (fast-forward only)
- **`develop`**: Your working branch with patches on top
- **`origin/develop`**: Your fork on GitHub

## Daily Workflow

### Syncing Upstream Changes

**Do this regularly (daily for fast-moving repos):**

```bash
# 1. Fetch latest upstream changes
git fetch upstream

# 2. Update your local upstream mirror (fast-forward only)
git checkout develop-upstream
git merge --ff-only upstream/develop
# If this fails, your develop-upstream is corrupted. Reset it:
# git reset --hard upstream/develop

# 3. Rebase your patches on top of upstream
git checkout develop
git rebase develop-upstream

# 4. If rebase succeeds without conflicts:
git push origin develop --force-with-lease

# If conflicts occur, see "Handling Conflicts" section below
```

### Making New Changes

**Always work on top of your develop branch:**

```bash
git checkout develop
git pull origin develop  # Get your latest changes

# Make your changes
git add .
git commit -m "fix: your local patch"

# Push to your fork
git push origin develop
```

## Handling Conflicts

When `git rebase develop-upstream` produces conflicts:

### Step 1: Identify the Conflict

```bash
git status
# Shows which files have conflicts
```

### Step 2: Resolve Conflicts

```bash
# Edit conflicting files manually
# Remove conflict markers (<<<<<<<, =======, >>>>>>>)
# Keep your fix, incorporate upstream changes

# After fixing each file:
git add <conflicting-file>

# Continue rebase
git rebase --continue

# If you mess up and want to start over:
git rebase --abort
```

### Step 3: Verify Your Fix Still Works

```bash
# After rebase completes, test your application
npm run build
npm run dev
# Run your test suite if available
```

### Step 4: Force Push (Safe After Rebase)

```bash
# Use --force-with-lease for safety
# This prevents overwriting others' changes
git push origin develop --force-with-lease

# If --force-with-lease fails, someone else pushed:
git pull --rebase origin develop
git push origin develop --force-with-lease
```

## Recovery Scenarios

### Scenario 1: Upstream Fixed Your Issue

**What happened:** Upstream merged a fix for the same issue you patched.

**Recovery:**

```bash
# 1. Fetch upstream
git fetch upstream
git checkout develop-upstream
git merge --ff-only upstream/develop

# 2. Rebase and drop duplicate commit
git checkout develop
git rebase -i develop-upstream

# In the interactive editor:
# - Mark your now-redundant commit as "drop"
# - Save and exit

# 3. Verify and push
git log --oneline -10  # Verify your patch is gone
git push origin develop --force-with-lease
```

### Scenario 2: Rebase Went Wrong

**What happened:** You have a messy rebase state and want to start over.

**Recovery:**

```bash
# 1. Abort current rebase
git rebase --abort

# 2. Reset to your last known good state
git reflog  # Find the commit hash before rebase
git reset --hard <hash-before-rebase>

# 3. Try again more carefully
git fetch upstream
git checkout develop-upstream
git merge --ff-only upstream/develop
git checkout develop
git rebase develop-upstream
```

### Scenario 3: Lost Commits After Force Push

**What happened:** Force push removed commits you needed.

**Recovery:**

```bash
# 1. Find lost commits
git reflog
# Look for your commit before force push

# 2. Recover lost work
git checkout develop
git cherry-pick <lost-commit-hash>

# 3. Push again
git push origin develop --force-with-lease
```

## Force Push Safety Rules

### ✅ Safe to Force Push:

- **After rebasing on upstream** (as described in this workflow)
- **Using `--force-with-lease`** instead of `--force`
- **On branches you own** (your fork's develop)
- **After verifying** your changes work

### ❌ Never Force Push:

- **On shared branches** (if others contribute to your fork)
- **Without `--force-with-lease`** (you might overwrite others' work)
- **Without testing** after rebase
- **On `main`/`master` branches** that others depend on

### Why `--force-with-lease` is Better:

```bash
# ❌ Dangerous (overwrites everything):
git push origin develop --force

# ✅ Safe (fails if remote has unexpected changes):
git push origin develop --force-with-lease
```

## Automated Sync (GitHub Actions)

Create `.github/workflows/sync-upstream.yml`:

```yaml
name: Sync Upstream

on:
  schedule:
    # Run every day at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          ref: develop
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Configure Git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
      
      - name: Add Upstream Remote
        run: |
          git remote add upstream https://github.com/[upstream-owner]/[upstream-repo].git
          git fetch upstream
      
      - name: Check for Upstream Changes
        id: check
        run: |
          git fetch upstream
          UPSTREAM_COMMIT=$(git rev-parse upstream/develop)
          LOCAL_BASE=$(git merge-base develop upstream/develop)
          
          if [ "$UPSTREAM_COMMIT" != "$LOCAL_BASE" ]; then
            echo "changes=true" >> $GITHUB_OUTPUT
            echo "Upstream has new changes"
          else
            echo "changes=false" >> $GITHUB_OUTPUT
            echo "Already up to date"
          fi
      
      - name: Rebase on Upstream
        if: steps.check.outputs.changes == 'true'
        run: |
          # Create local tracking branch
          git branch -f develop-upstream upstream/develop
          
          # Attempt rebase
          if git rebase develop-upstream; then
            echo "✅ Rebase successful"
            git push origin develop --force-with-lease
          else
            echo "❌ Rebase failed - conflicts detected"
            git rebase --abort
            exit 1
          fi
      
      - name: Create Issue on Conflict
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Upstream Sync Failed - Manual Rebase Required',
              body: `The automated upstream sync failed due to conflicts.
              
              **Action Required:**
              1. Run the manual sync workflow locally
              2. Resolve conflicts in the affected files
              3. Test your changes
              4. Push with \`--force-with-lease\`
              
              See [FORK-MAINTENANCE.md](./FORK-MAINTENANCE.md) for detailed instructions.
              
              **Failed Workflow:** ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}`,
              labels: ['upstream-sync', 'needs-attention']
            })
```

### Setting Up Automation

1. **Create the workflow file** (see above)
2. **Update upstream URL** in the workflow
3. **Enable Actions** in your fork's settings
4. **Test manually** first:
   ```bash
   # In GitHub UI: Actions → Sync Upstream → Run workflow
   ```
5. **Monitor for failures** via email notifications or issues

### Automation Benefits

- ✅ Stays in sync automatically
- ✅ Creates issues when manual intervention needed
- ✅ Runs daily (or on-demand)
- ✅ Uses `--force-with-lease` for safety
- ✅ Fails gracefully on conflicts

### Automation Limitations

- ❌ Cannot resolve conflicts automatically
- ❌ Cannot test if your patch still works
- ⚠️ You must monitor for failed runs

## Keeping Your Patch Minimal

### Principles

1. **One commit per logical fix** (use `git commit --amend` to update)
2. **Clear commit messages** describing why the patch exists
3. **Regular rebasing** to stay close to upstream
4. **Submit PRs upstream** when possible to remove your patch

### Tracking Your Patches

List commits that are yours (not in upstream):

```bash
git log develop-upstream..develop --oneline
# These are your local patches
```

### Cleaning Up Merged Patches

When upstream merges your fix:

```bash
# Interactive rebase to drop merged commits
git rebase -i develop-upstream

# Mark redundant commits as "drop"
# Save and exit
```

## Quick Reference

### Daily Sync

```bash
git fetch upstream
git checkout develop-upstream && git merge --ff-only upstream/develop
git checkout develop && git rebase develop-upstream
git push origin develop --force-with-lease
```

### Check Status

```bash
# See your patches
git log develop-upstream..develop --oneline

# Check if upstream has changes
git fetch upstream
git log develop..upstream/develop --oneline
```

### Emergency Abort

```bash
git rebase --abort
git reset --hard origin/develop  # Last known good state
```

## When to Use This Workflow

✅ **Use this workflow when:**
- You cannot contribute fixes back to upstream
- Upstream moves fast and you need to stay current
- Your changes are minimal and well-isolated
- You want a clean, linear history
- Stability matters more than convenience

❌ **Don't use this workflow when:**
- You have extensive custom modifications
- You work with a team that doesn't understand rebasing
- Upstream rarely changes
- You prefer merge-based workflows

## Additional Resources

- [Git Rebase Documentation](https://git-scm.com/docs/git-rebase)
- [Force Push Safety](https://git-scm.com/docs/git-push#Documentation/git-push.txt---force-with-lease)
- [Git Reflog Recovery](https://git-scm.com/docs/git-reflog)

## Support

If you encounter issues with this workflow:
1. Check `git reflog` for recovery options
2. Review the "Recovery Scenarios" section above
3. Consider asking in Git communities for complex cases
