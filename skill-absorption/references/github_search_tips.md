# GitHub 高级搜索技巧

## 基础搜索

### 关键词搜索

```bash
# 基础关键词
gh search repos "claude skill"
gh search repos "anthropic skill"
gh search repos "claude-code skill"

# 多关键词（OR）
gh search repos "claude skill OR anthropic skill"

# 短语搜索
gh search repos '"claude code skill"'
```

## 排序和过滤

### 按星标排序

```bash
# 最多星标
gh search repos "claude skill" --sort stars --order desc

# 最少星标
gh search repos "claude skill" --sort stars --order asc
```

### 按更新时间排序

```bash
# 最近更新
gh search repos "claude skill" --sort updated --order desc
```

### 按 forks 排序

```bash
# 最多 forks
gh search repos "claude skill" --sort forks
```

## 高级过滤

### 语言过滤

```bash
# Python 项目
gh search repos "claude skill" --language python

# JavaScript 项目
gh search repos "claude skill" --language javascript

# TypeScript 项目
gh search repos "claude skill" --language typescript

# Rust 项目
gh search repos "claude skill" --language rust
```

### 文件搜索

```bash
# 搜索包含 SKILL.md 的仓库
gh search repos "filename:SKILL.md"

# 搜索包含特定文件的仓库
gh search repos "filename:SKILL.md claude"
```

### 内容搜索

```bash
# 在 README 中搜索
gh search repos "claude skill in:readme"

# 在描述中搜索
gh search repos "claude skill in:description"

# 在 topics 中搜索
gh search repos "claude skill in:topics"
```

### 日期过滤

```bash
# 最近创建的
gh search repos "claude skill" --created ">2024-01-01"

# 最近更新的
gh search repos "claude skill" --updated ">2024-01-01"
```

## Web 界面搜索

在 GitHub 搜索框中使用：

```
# 精确匹配
"claude skill"

# 排除关键词
claude skill -deprecated

# 特定用户/组织
claude skill user:anthropics
claude skill org:anthropics

# 仓库大小
claude skill size:<10000

# 许可证
claude skill license:mit

# 主题标签
claude skill topic:ai topic:automation
```

## 搜索代码

```bash
# 搜索代码中的特定内容
gh search code "def extract_skill" --language python

# 在特定仓库中搜索
gh search code "SKILL.md" --repo owner/repo-name
```

## 搜索 Topics

```bash
# 搜索带有特定 topic 的仓库
gh search repos "topic:claude-code"
gh search repos "topic:anthropic"
gh search repos "topic:ai-assistant"
```

## 实用组合

### 发现高质量 Skills

```bash
# 高星标 + 最近更新 + Python
gh search repos "claude skill" \
  --sort stars \
  --language python \
  --updated ">2024-01-01"
```

### 发现新 Skills

```bash
# 最近创建 + 有描述
gh search repos "claude skill" \
  --sort created \
  --order desc \
  --limit 20
```

### 发现相关项目

```bash
# 不仅限于 skill，还包括相关工具
gh search repos "claude-code" \
  --sort stars \
  --limit 50
```

## 保存搜索结果

```bash
# 保存到文件
gh search repos "claude skill" \
  --sort stars \
  --limit 20 \
  --json \
  > /tmp/skill-search-results.json

# 解析结果
jq -r '.[].full_name' /tmp/skill-search-results.json
```

## 克隆并分析

```bash
# 批量克隆前 5 个仓库
gh search repos "claude skill" \
  --sort stars \
  --limit 5 \
  --json \
  | jq -r '.[].html_url' \
  | while read url; do
      name=$(basename $url)
      git clone --depth 1 $url /tmp/skills/$name
    done

# 分析所有 SKILL.md
for f in /tmp/skills/*/SKILL.md; do
  echo "=== $f ==="
  head -30 "$f"
  echo ""
done
```

## 监控更新

```bash
# 查看某个仓库的最新提交
gh api repos/OWNER/REPO/commits --jq '.[0] | {sha, message, date: .commit.committer.date}'

# 查看仓库 releases
gh release list --repo OWNER/REPO --limit 5
```

## 推荐搜索查询

```bash
# 1. 寻找高质量的 Claude skills
gh search repos "claude skill" --sort stars --limit 10

# 2. 寻找最近更新的 skills
gh search repos "claude skill" --sort updated --limit 10

# 3. 寻找包含 SKILL.md 的项目
gh search repos "filename:SKILL.md claude" --limit 10

# 4. 寻找 Python 实现的 skills
gh search repos "claude skill" --language python --sort stars

# 5. 寻找完整示例
gh search repos "anthropic skill example" --sort stars
```
