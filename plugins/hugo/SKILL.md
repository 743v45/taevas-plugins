---
name: hugo
description: "Publish content to Hugo blog. Use when user invokes /hugo command to create or update blog posts. Supports multiple usage patterns: (1) /hugo alone - check Hugo installation, find site, ask for content, (2) /hugo with content description - create/update post with described content, (3) /hugo with content and path - create/update post at specified path, (4) /hugo new <content> - force create new post, (5) /hugo update <content> - force update existing post. Always confirms site path and content with user before writing."
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

## Workflow

1. **Check Hugo installation**
   ```bash
   hugo version
   ```
   If not installed, prompt user to install: `brew install hugo` (macOS) or see https://gohugo.io/installation/

2. **Determine Hugo site path**

   - If user specified a path → use it
   - Otherwise → detect current directory using `scripts/detect_hugo_site.py`

   **Always confirm with user** unless explicitly told to skip confirmation.

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

## Scripts

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
1. Check `hugo version`
2. Run `detect_hugo_site.py` on current directory
3. If Hugo site found: "检测到 Hugo 站点在 `/path/to/site`，确认在此目录操作？"
4. Ask: "请问您想写什么内容？"

**User:** `/hugo 写一篇关于 Go 并发的文章`
**Response:**
1. Check Hugo installation
2. Detect/confirm site path
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
2. Detect/confirm site path
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
1. Use specified path instead of auto-detect
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
```

## Reference

- Front matter format: [references/front-matter.md](references/front-matter.md)
- Hugo docs: https://gohugo.io/getting-started/quick-start/#add-content