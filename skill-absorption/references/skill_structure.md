# Claude Skill 标准结构

## 目录结构

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter (必需)
│   │   ├── name: skill 名称
│   │   └── description: skill 描述和使用场景
│   └── Markdown 内容 (必需)
├── scripts/ (可选)
│   └── *.py, *.sh 等可执行脚本
├── references/ (可选)
│   └── *.md 参考文档
└── assets/ (可选)
    └── 模板、图片、字体等资源文件
```

## SKILL.md 结构

### Frontmatter

```yaml
---
name: skill-name
description: 详细的 skill 描述，说明功能和使用场景。当用户需要 [功能 X] 或处理 [任务 Y] 时触发此 skill。
---
```

**name 要求：**
- 使用小写字母和连字符（kebab-case）
- 例如：`pdf-processor`, `big-query-helper`
- 最大 40 个字符

**description 要求：**
- 说明 skill 的功能
- 说明何时使用此 skill（触发条件）
- 示例场景
- 这是触发 skill 的关键

### Body 结构

常见结构模式：

**1. 基于工作流**（顺序流程）
```markdown
# Skill Name

## Overview
概述

## Workflow Decision Tree
决策树

## Step 1
步骤 1

## Step 2
步骤 2
```

**2. 基于任务**（工具集合）
```markdown
# Skill Name

## Quick Start
快速开始

## Task Category 1
任务类别 1

## Task Category 2
任务类别 2
```

**3. 参考/指南**（标准规范）
```markdown
# Skill Name

## Guidelines
指南

## Specifications
规范

## Usage
用法
```

## Scripts 最佳实践

- 使用 Python 或 Bash
- 添加 shebang (`#!/usr/bin/env python3`)
- 包含文档字符串说明用途
- 可独立执行
- 返回适当的退出码

## References 最佳实践

- 详细的 API 文档
- 工作流程指南
- 数据库 schema
- 仅在需要时加载
- 使用链接从 SKILL.md 引用

## Assets 最佳实践

- 模板文件 (.docx, .pptx, .html)
- 图片资源
- 字体文件
- 示例项目
- 不加载到上下文，只用于输出

## 渐进披露设计

1. **Metadata** - 始终在上下文中（~100 词）
2. **SKILL.md body** - skill 触发时加载（<5k 词）
3. **Bundled resources** - 需要时加载

保持 SKILL.md 精简，详细信息放入 references/。

## 示例 Skills

### PDF Skill
- 处理 PDF 文件：读取、合并、拆分、提取文本
- 触发条件：用户提到 PDF 文件操作

### DOCX Skill
- 处理 Word 文档：创建、编辑、跟踪更改
- 触发条件：用户提到 .docx 或 Word 文档

### BigQuery Skill
- 查询 BigQuery 数据库
- 触发条件：用户询问数据查询

## 命名约定

### Skill 名称
- 小写字母和连字符
- 描述性但简洁
- 例如：`data-analyzer`, `api-client`

### 文件命名
- scripts: `snake_case.py` 或 `kebab-case.sh`
- references: `kebab-case.md`
- assets: 根据类型使用适当扩展名

### 代码风格
- Python: PEP 8
- Bash: Google Shell Style Guide
- Markdown: 标准 Markdown
