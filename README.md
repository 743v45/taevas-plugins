# Taevas Plugins Marketplace

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-purple.svg)](https://claude.ai/code)

A collection of plugins for Claude Code with sound notifications and workflow enhancements.

## Available Plugins

| Plugin | Description | Category |
|--------|-------------|----------|
| **sound-hooks** | Sound notification hooks for task events | Notifications |
| **workflow-helper** | Workflow helper with common utilities | Productivity |

## Quick Start

```bash
# Add marketplace
claude plugin marketplace add 743v45/taevas-plugins

# Install plugins
claude plugin install sound-hooks@taevas-plugins
claude plugin install workflow-helper@taevas-plugins
```

## Sound Hooks

Audio feedback for task and command events.

### Configuration

Edit `.claude/plugins/sound-hooks/config.json`:

```json
{
  "enabled": true,
  "notifications": {
    "enabled": true,
    "sound": "Glass",
    "sounds": {
      "task_start": "Ping",
      "task_complete": "Hero",
      "task_error": "Basso",
      "command_start": "Tink"
    },
    "log": true
  }
}
```

### Available Sounds (macOS)

| Sound | Description |
|-------|-------------|
| Glass | Glass ping |
| Ping | Bell ping |
| Hero | Hero effect |
| Tink | Tinkling bell |
| Basso | Deep bass |
| Pop | Pop sound |

## License

MIT License - see [LICENSE](LICENSE)
