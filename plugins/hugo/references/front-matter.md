# Default Front Matter Format

Use this format when no existing posts are found in the Hugo site.

## TOML format (+++)

```toml
+++
title = "Your Post Title"
date = 2024-01-15T10:00:00+08:00
draft = false
description = "A brief description of the post"
tags = ["tag1", "tag2"]
categories = ["category1"]
+++

Your content here...
```

## YAML format (---)

```yaml
---
title: "Your Post Title"
date: 2024-01-15T10:00:00+08:00
draft: false
description: "A brief description of the post"
tags:
  - tag1
  - tag2
categories:
  - category1
---

Your content here...
```

## Common front matter fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Post title |
| date | datetime | Recommended | Publication date (ISO 8601 format) |
| draft | boolean | Recommended | Set to `false` to publish |
| description | string | Optional | Brief summary for SEO/listing |
| tags | array | Optional | Post tags |
| categories | array | Optional | Post categories |
| author | string | Optional | Author name |
| slug | string | Optional | URL slug (defaults to filename) |
| image | string | Optional | Featured image path |

## Detecting existing format

When existing posts exist, read one to determine the format used:
- Starts with `+++` → TOML
- Starts with `---` → YAML