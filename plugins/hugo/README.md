# Hugo 博客发布

为 Claude Code 提供 Hugo 静态博客发布功能。使用 `/hugo` 命令快速创建和更新博客文章。

## 功能特性

- **自动检测**：自动检测 Hugo 站点和配置
- **智能模式**：支持创建、更新、自动判断三种模式
- **文章搜索**：根据关键词搜索现有文章
- **格式适配**：自动匹配现有文章的 front matter 格式 (TOML/YAML)
- **更新时间**：更新文章时自动设置 `lastmod` 字段
- **交互确认**：操作前确认站点路径和内容

## 安装

```bash
# 从 marketplace 安装
claude plugin marketplace add 743v45/taevas-plugins
claude plugin install hugo@taevas-plugins

# 更新命令
claude plugin marketplace update taevas-plugins && claude plugin update hugo@taevas-plugins
```

## 使用方法

### 命令语法

```
/hugo [new|create|update] [内容描述] [站点路径] [-c|--check]
```

| 参数 | 说明 |
|------|------|
| `new` / `create` | 强制创建新文章 |
| `update` | 强制更新现有文章 |
| `内容描述` | 文章内容或标题关键词 |
| `站点路径` | Hugo 站点路径（可选） |
| `-c` / `--check` | 创建/更新后启动 `hugo server` 预览 |

### 模式说明

#### 自动模式（推荐）

```bash
/hugo 写一篇关于 Go 并发的文章
```

- 搜索现有文章是否匹配
- 找到则询问是否更新
- 未找到则创建新文章

#### 创建模式

```bash
/hugo new Go 泛型教程
```

强制创建新文章，不搜索现有文章。

#### 更新模式

```bash
/hugo update Go 并发
```

搜索并更新现有文章，未找到时报错。

#### 交互模式

```bash
/hugo
```

逐步询问站点、内容等信息。

#### 指定路径

```bash
/hugo 写一篇关于 Rust 的文章 ~/my-blog
```

在指定路径的 Hugo 站点操作。

## 文章搜索

当使用自动模式或更新模式时，会根据关键词搜索现有文章：

- 搜索文章标题（front matter 中的 title）
- 搜索文件名
- 计算匹配度并排序

示例输出：
```
Searching for: 'Go 并发'
Found 2 matching post(s):
  - [content/posts/go-concurrency.md] "Go 并发编程指南" (score: 25)
  - [content/posts/go-advanced.md] "Go 高级并发模式" (score: 15)
```

## 更新文章

更新现有文章时：

1. 读取现有 front matter，保留所有字段
2. 添加或更新 `lastmod` 字段
3. 保留原始 `date`（发布时间）
4. 更新文章内容

### 更新后的 Front Matter 示例

```toml
+++
title = "Go 并发编程指南"
date = 2024-01-15T10:00:00+08:00      # 原始发布时间
lastmod = 2024-01-20T15:30:00+08:00   # 更新时间
draft = false
description = "深入理解 Go 语言并发模型"
tags = ["go", "concurrency", "goroutine"]
categories = ["编程"]
+++
```

## Front Matter 格式

插件会自动检测现有文章的格式：

- `+++` 开头 → TOML 格式
- `---` 开头 → YAML 格式

新站点默认使用 TOML 格式。

## 文件结构

```
hugo-site/
├── config.toml (或 hugo.toml, config.yaml)
├── content/
│   └── posts/
│       └── my-post.md  ← 文章位置
└── ...
```

## 依赖

- [Hugo](https://gohugo.io/installation/) - 静态站点生成器

安装 (macOS):
```bash
brew install hugo
```

## 相关链接

- [Hugo 官方文档](https://gohugo.io/)
- [Front Matter 参考](references/front-matter.md)