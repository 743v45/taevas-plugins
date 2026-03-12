---
name: hugo
description: "Publish content to Hugo blog. Use when user invokes /hugo command to create new blog posts. Supports multiple usage patterns: (1) /hugo alone - check Hugo installation, find site, ask for content, (2) /hugo with content description - create post with described content, (3) /hugo with content and path - create post at specified path, (4) /hugo with path - use specified Hugo site path. Always confirms site path and content with user before writing."
---

# Hugo Blog Publisher

Create and publish blog posts to Hugo static site.

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

3. **Determine content**

   - If user described content → use that
   - If no content specified → ask user what they want to write about
   - Content may come from conversation context, user description, or files

   **Always confirm content with user before writing.**

4. **Determine front matter format**

   - If existing posts exist → read one to match format
   - If no posts → use default format from [references/front-matter.md](references/front-matter.md)

5. **Create the post**

   ```bash
   cd /path/to/hugo/site
   hugo new content content/posts/<slug>.md
   ```

   Then write front matter and content to the file.

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
3. Generate content outline
4. Confirm: "确认写入以下内容到 content/posts/go-concurrency.md？"
5. Write file after confirmation

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