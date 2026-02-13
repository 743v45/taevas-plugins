# Workflow Helper

Development workflow utilities for Claude Code.

## Features

- **Git Info**: Display current branch, commit count, and working tree status
- **Commit Message Check**: Remind to include co-authored-by in commits
- **Project Info**: Show project summary on session start

## Scripts

### git-info.sh

Shows git repository information in a compact format:

```bash
./scripts/git-info.sh
# Output: [main|142|clean] or [feature-branch|58|3 changed]
```

Format: `[branch|commits|status]`

## Hooks

The plugin includes these hooks:

| Hook | Trigger | Action |
|------|--------|--------|
| git-branch-info | Before bash commands | Show current git branch |
| commit-msg-check | Git commit | Check commit message format |
| project-info | Session start | Show project summary |

## Manual Usage

```bash
# Check git info
~/.claude/plugins/workflow-helper/scripts/git-info.sh
```
