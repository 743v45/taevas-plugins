# Hugo 博客发布

为 Claude Code 提供 Hugo 静态博客发布功能。使用 `/hugo` 命令快速创建和发布博客文章。

## 功能特性

- **自动检测**：自动检测 Hugo 站点和配置
- **多种模式**：支持 4 种使用模式
- **格式适配**：自动匹配现有文章的 front matter 格式 (TOML/YAML)
- **交互确认**：创建前确认站点路径和内容

## 安装

```bash
# 从 marketplace 安装
claude plugin marketplace add 743v45/taevas-plugins
claude plugin install hugo@taevas-plugins

# 更新命令
claude plugin marketplace update taevas-plugins && claude plugin update hugo@taevas-plugins
```

## 使用方法

### 模式 1: 交互式

```bash
/hugo
```

1. 检查 Hugo 安装
2. 检测当前目录的 Hugo 站点
3. 询问要写的内容
4. 确认后创建文章

### 模式 2: 指定内容

```bash
/hugo 写一篇关于 Go 并发的文章
```

1. 检查 Hugo 安装
2. 检测/确认站点路径
3. 生成内容大纲
4. 确认后创建文章

### 模式 3: 指定内容和路径

```bash
/hugo 写一篇关于 Rust 的文章 ~/my-blog
```

在指定路径的 Hugo 站点创建文章。

### 模式 4: 仅指定路径

```bash
/hugo ~/my-blog
```

使用指定的 Hugo 站点路径，然后询问内容。

## Front Matter 格式

插件会自动检测现有文章的格式：

- `+++` 开头 → TOML 格式
- `---` 开头 → YAML 格式

新站点默认使用 TOML 格式：

```toml
+++
title = "文章标题"
date = 2024-01-15T10:00:00+08:00
draft = false
description = "文章简介"
tags = ["tag1", "tag2"]
categories = ["category1"]
+++
```

## 文件结构

```
hugo-site/
├── config.toml (或 hugo.toml, config.yaml)
├── content/
│   └── posts/
│       └── my-post.md  ← 新文章位置
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