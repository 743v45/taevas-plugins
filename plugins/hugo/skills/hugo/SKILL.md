---
name: hugo
description: "Publish content to Hugo blog. Use when user invokes /hugo command to create or update blog posts. Supports multiple usage patterns: (1) /hugo alone - check Hugo installation, use configured site or ask for path, ask for content, (2) /hugo with content description - create/update post with described content, (3) /hugo with content and path - create/update post at specified path, (4) /hugo new <content> - force create new post, (5) /hugo update <content> - force update existing post. Site path is user-configured, no automatic scanning."
---

# Hugo Blog Publisher

Create and publish blog posts to Hugo static site.

## Command Syntax

```
/hugo [new|create|update] [content description] [site path] [-c|--check]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `new` / `create` | Force create a new post |
| `update` | Force update an existing post |
| `<content>` | Content description or title keywords |
| `<site path>` | Path to Hugo site (optional) |
| `-c` / `--check` | Verify with `hugo server` after create/update |

### Behavior

1. **With `new` or `create`**: Always create a new post, error if file exists
2. **With `update`**: Always update an existing post, error if not found
3. **Without mode flag**: Auto-detect - search for existing post by title/keywords
   - If matching posts found → show list with scores, ask user to select one or create new
   - If no match → create new post
4. **With `-c` or `--check`**: Run `hugo server -D` after create/update to preview

### Site Path Resolution

1. **User provides path in command** → Use that path
2. **No path in command, but current_site is configured** → Use configured site
3. **No path in command, no current_site configured** → Ask user for path and save it as current_site

## Configuration Cache

Hugo skill caches configuration in `~/.config/hugo-skill/config.json` to avoid repeated checks:

| Cache Item | Description | When Updated |
|------------|-------------|--------------|
| `hugo_version` | Hugo version string | First run or manual force |
| `current_site` | Current Hugo site path | When user sets/changes it |
| `sites` | List of known Hugo site paths | When user adds a site |

### Cache Behavior

- **Hugo Version**: Checked once, cached for subsequent runs. Use `python3 scripts/config_manager.py version --force` to re-verify.
- **Current Site**: Set by user, used as default when no path specified.
- **Sites List**: Manually added by user, no automatic scanning.

### Current Site Configuration

The "current" site is the default site used when no path is specified:

```bash
# Set the current site
python3 scripts/config_manager.py set-current /path/to/hugo/site

# Remove current site setting
python3 scripts/config_manager.py unset-current
```

## Workflow

1. **Check Hugo installation (cached)**

   First run: Execute `hugo version` and cache result.
   Subsequent runs: Use cached version, skip check.

   ```bash
   python3 scripts/config_manager.py version
   ```

   If Hugo not installed, prompt user: `brew install hugo` (macOS) or see https://gohugo.io/installation/

2. **Determine Hugo site path (user-provided only)**

   **不再自动扫描目录**。只使用用户提供的配置。

   **如果有配置的站点：**
   - 直接使用配置的站点，无需询问

   **如果没有配置站点：**
   - 直接询问用户提供站点路径
   - 用户输入后保存到配置，下次直接使用

   **配置管理命令：**
   ```bash
   # 查看当前配置
   python3 scripts/config_manager.py show

   # 设置当前使用的站点
   python3 scripts/config_manager.py set-current /path/to/hugo/site

   # 列出已配置的站点
   python3 scripts/config_manager.py list

   # 添加站点到配置
   python3 scripts/config_manager.py add /path/to/hugo/site

   # 从配置中移除站点
   python3 scripts/config_manager.py remove /path/to/hugo/site
   ```

   **用户在命令中指定路径时：**
   - 如果用户提供了路径参数 → 使用该路径
   - 如果用户未提供且无配置 → 询问用户路径并保存配置
   - 如果用户未提供但有配置 → 直接使用配置的站点

   **不再进行目录扫描，所有站点路径必须由用户明确提供。**

3. **Determine operation mode (new/update/auto)**

   - If user specified `new` or `create` → CREATE mode
   - If user specified `update` → UPDATE mode
   - Otherwise → AUTO mode

   **AUTO mode logic:**
   - Search existing posts for title/keyword match
   - If matches found → display list with titles and scores
   - Ask user: "找到以下相关文章，请选择要更新的文章（输入序号），或输入 'new' 创建新文章："
   - If no match or user enters 'new' → create new post

4. **Determine content**

   - If user described content → use that
   - If no content specified → ask user what they want to write about
   - Content may come from conversation context, user description, or files

   **Always confirm content with user before writing.**

5. **Determine front matter format**

   - If existing posts exist → read one to match format
   - If no posts → use default format from [references/front-matter.md](references/front-matter.md)

6. **Create or update the post**

   **Create new post:**
   ```bash
   cd /path/to/hugo/site
   hugo new content content/posts/<slug>.md
   ```
   Then write front matter and content to the file.

   **Update existing post:**
   - Read existing front matter
   - Update `lastmod` field (or add it if not present)
   - Update content while preserving other front matter fields
   - If updating `date` field, also keep original `date` and add `lastmod`

7. **Optional verification (with --check/-c)**
   ```bash
   hugo server -D
   ```
   Starts local server for preview. User can stop with Ctrl+C.

8. **Git commit workflow (after create/update)**

   After successfully creating or updating a post, ask the user:
   > "文章已完成。是否需要 git add 并 commit？"

   **If user wants to commit:**

   1. Check git status to see what files have changed:
      ```bash
      cd /path/to/hugo/site
      git status
      ```

   2. **Isolation check** - Ensure only the newly created/updated post file is staged:
      - If only the target post file has changes → proceed with commit
      - If other files have changes that are unrelated:
        - Use `git add <post-file-path>` to stage only the post file
        - Verify with `git diff --cached --name-only` that only the intended file is staged
      - If unable to isolate (e.g., other changes are interdependent or conflict) → ask user:
        > "检测到其他未提交的更改，无法单独提交文章。是否放弃提交？"
        - If user confirms → skip commit
        - If user wants to proceed anyway → warn and proceed

   3. **Create commit** with descriptive message:
      ```bash
      git commit -m "$(cat <<'EOF'
      <action>: <post-title>

      <brief description of changes>

      Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
      EOF
      )"
      ```
      Where `<action>` is:
      - `new` for new posts
      - `update` for updated posts

   4. **After commit succeeds**, ask user:
      > "提交完成。是否需要 git push？"

      - If yes → run `git push`
      - If no → inform user that commit is ready locally

   **If user declines commit:**
   > "好的，文章已保存但未提交。您可以稍后手动提交。"

## Scripts

### config_manager.py

Manage Hugo skill configuration cache:

```bash
# Check Hugo version (cached after first run)
python3 scripts/config_manager.py version

# Force re-check Hugo version
python3 scripts/config_manager.py version --force

# Show full config
python3 scripts/config_manager.py show

# Set current site (used by default)
python3 scripts/config_manager.py set-current /path/to/hugo/site

# Remove current site setting
python3 scripts/config_manager.py unset-current

# List configured sites
python3 scripts/config_manager.py list

# Add a site to configuration
python3 scripts/config_manager.py add /path/to/hugo/site

# Remove a site from configuration
python3 scripts/config_manager.py remove /path/to/hugo/site
```

### detect_hugo_site.py

Check if a directory is a Hugo site root:

```bash
python3 scripts/detect_hugo_site.py /path/to/check
```

Returns:
- `is_hugo_site`: boolean
- `config_file`: path to config (config.toml/yaml/json or hugo.toml/yaml/json)
- `content_dir`: path to content directory
- `existing_posts`: list of existing .md files in content/posts/

## Example Usage

**User:** `/hugo`
**Response:**
1. Check cached Hugo version (skip if already cached)
2. Check if site is configured:
   - If configured: "使用已配置站点: `/path/to/site`"
   - If not configured: Ask user: "请提供您的 Hugo 站点路径："
3. Ask: "请问您想写什么内容？"

**User:** `/hugo 写一篇关于 Go 并发的文章`
**Response:**
1. Use cached Hugo version (skip check if already cached)
2. Use configured site (or ask if not configured)
3. Search existing posts for "Go 并发" or similar keywords
4. If matches found:
   ```
   找到以下相关文章：
     1. [content/posts/go-concurrency.md] "Go 并发编程指南" (score: 25)
     2. [content/posts/goroutine-basics.md] "Goroutine 基础入门" (score: 12)
   请选择要更新的文章（输入序号），或输入 'new' 创建新文章：
   ```
5. User selects → update that post; User enters 'new' → create new post
6. Confirm content and write file

**User:** `/hugo new Go 泛型教程`
**Response:**
1. Force create mode - skip existing post search
2. Use configured site (or ask if not configured)
3. Generate content
4. Create new file: `content/posts/go-generics-tutorial.md`

**User:** `/hugo update Go 并发`
**Response:**
1. Force update mode - search for matching post
2. Find existing post by title/keywords
3. Read current content
4. Ask: "找到文章 go-concurrency.md，请描述要更新的内容"
5. Update content and set `lastmod` field

**User:** `/hugo 写一篇关于 Rust 的文章 /path/to/another/hugo/site`
**Response:**
1. Use specified path instead of cached site
2. Follow same workflow as above

**User:** `/hugo new Go 泛型教程 -c`
**Response:**
1. Create new post
2. Run `hugo server -D` for preview
3. User can view at http://localhost:1313

## Updating Posts

When updating an existing post:

1. **Read existing front matter** - preserve all existing fields
2. **Update timestamps**:
   - TOML: Add/update `lastmod = 2024-01-20T15:30:00+08:00`
   - YAML: Add/update `lastmod: 2024-01-20T15:30:00+08:00`
3. **Keep original `date`** - do not modify the original publication date
4. **Update content** - replace or append based on user request

### Example updated front matter (TOML)

```toml
+++
title = "Go 并发编程指南"
date = 2024-01-15T10:00:00+08:00
lastmod = 2024-01-20T15:30:00+08:00
draft = false
description = "深入理解 Go 语言并发模型"
tags = ["go", "concurrency", "goroutine"]
categories = ["编程"]
+++
```

### Example updated front matter (YAML)

```yaml
---
title: "Go 并发编程指南"
date: 2024-01-15T10:00:00+08:00
lastmod: 2024-01-20T15:30:00+08:00
draft: false
description: "深入理解 Go 语言并发模型"
tags:
  - go
  - concurrency
  - goroutine
categories:
  - 编程
---
```

## File Structure

```
hugo-site/
├── config.toml (or hugo.toml, config.yaml, etc.)
├── content/
│   └── posts/
│       └── my-first-post.md  ← New posts go here
└── ...

~/.config/hugo-skill/
└── config.json  ← Cache file for version and sites
```

## Reference

- Front matter format: [references/front-matter.md](references/front-matter.md)
- Hugo docs: https://gohugo.io/getting-started/quick-start/#add-content