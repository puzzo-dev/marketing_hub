# Contributing to Marketing Hub

## Branching Strategy

```
main ← version-15 ← develop ← feature/*
 │         │            │
 │         │            └── Active development
 │         └── Frappe v15 stable releases
 └── Production-ready releases (all Frappe versions)
```

### Branches

| Branch | Purpose | Protected | Deploys to |
|--------|---------|-----------|------------|
| `main` | Production-ready releases | Yes | Production |
| `version-15` | Stable for Frappe v15 (`bench` tracks this) | Yes | Staging |
| `develop` | Active development, feature integration | No | Dev |
| `feature/*` | Individual features/fixes | No | — |
| `hotfix/*` | Urgent production fixes | No | — |

### Workflow

1. **New feature**: Branch from `develop` → `feature/my-feature`
2. **Merge feature**: PR into `develop`
3. **Release**: Merge `develop` → `version-15` → `main`, tag on `main`
4. **Hotfix**: Branch from `main` → `hotfix/fix-name`, merge back to `main` AND `develop`

## Versioning

Follows [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`):

- **MAJOR** — Breaking changes (API, doctype schema changes that require data migration)
- **MINOR** — New features (new pages, doctypes, API endpoints)
- **PATCH** — Bug fixes, UI tweaks, performance improvements

Pre-release suffixes: `-alpha.N`, `-beta.N`, `-rc.N`

### Version Files

Version must be updated in **three places**:

```
marketing_hub/__init__.py    →  __version__ = "X.Y.Z"
marketing_hub/hooks.py       →  app_version = "X.Y.Z"
frontend/package.json        →  "version": "X.Y.Z"
```

### Tags

Tags follow `vX.Y.Z` format (e.g., `v1.0.0`, `v1.1.0-beta.1`). Always annotated:

```bash
git tag -a v1.1.0 -m "v1.1.0: Brief description"
git push origin --tags
```

## Release Process

```bash
# 1. On develop: bump version in all 3 files
# 2. Commit
git commit -m "chore(release): Bump version to X.Y.Z"

# 3. Merge to version-15
git checkout version-15
git merge develop

# 4. Merge to main
git checkout main
git merge version-15

# 5. Tag
git tag -a vX.Y.Z -m "vX.Y.Z: Release notes"

# 6. Push everything
git push origin main version-15 develop --tags

# 7. Switch back to develop
git checkout develop
```

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new tracking links page
fix: correct channel field name mismatch
refactor: migrate AxisChart to new config API
chore(release): bump version to 1.0.0
docs: update installation guide
```

Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `style`, `test`, `perf`
