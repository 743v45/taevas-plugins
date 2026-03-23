---
name: skill-absorption
description: 从 GitHub 或其他来源发现、提取并学习其他人的 Claude skills，将其整合到自己的 skill 中。用于技能发现、内容提取、模式学习、知识整合。当用户想要"学习别人的 skill"、"复制 skill"、"吸收技能"、"整合其他人的 skill"时触发此 skill。
---

# Skill Absorption（技能吸收）

## 概述

本 skill 帮助你从 GitHub 或其他来源发现、提取并学习其他人的 Claude skills，然后将这些知识整合到你自己的 skill 中。

## 工作流程

### 1. 发现技能 (Discovery)

搜索 GitHub 上的 Claude skills：

```bash
# 搜索 GitHub 上的 claude skills
gh search repos "claude skill" --sort stars
gh search repos "claude-code skill" --sort stars
```

或使用 Tavily 搜索：

```
搜索关键词：
- "claude skill github"
- "anthropic skill example"
- "claude-code skill marketplace"
```

### 2. 分析技能 (Analysis)

找到 skill 后，分析其结构：

```bash
# 克隆 repository
git clone <repository-url> /tmp/skill-analysis

# 查看 SKILL.md 结构
head -100 /tmp/skill-analysis/SKILL.md

# 查看 scripts/
ls -la /tmp/skill-analysis/scripts/

# 查看 references/
ls -la /tmp/skill-analysis/references/
```

### 3. 提取内容 (Extraction)

提取有价值的部分：

```python
# scripts/extract_skill.py
import os
import yaml
import shutil

def extract_skill(source_path, target_path):
    """从源 skill 提取内容到目标 skill"""

    # 读取源 SKILL.md
    with open(os.path.join(source_path, 'SKILL.md'), 'r') as f:
        content = f.read()

    # 解析 frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2]

    # 复制有用的资源
    for dir_name in ['scripts', 'references', 'assets']:
        source_dir = os.path.join(source_path, dir_name)
        if os.path.exists(source_dir):
            target_dir = os.path.join(target_path, dir_name)
            # 合并而不是覆盖
            merge_directories(source_dir, target_dir)

def merge_directories(source, target):
    """合并两个目录，不覆盖已有文件"""
    if not os.path.exists(target):
        shutil.copytree(source, target)
    else:
        for item in os.listdir(source):
            source_path = os.path.join(source, item)
            target_path = os.path.join(target, item)
            if not os.path.exists(target_path):
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, target_path)
                else:
                    shutil.copy2(source_path, target_path)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python extract_skill.py <source_skill_path> <target_skill_path>")
        sys.exit(1)
    extract_skill(sys.argv[1], sys.argv[2])
```

### 4. 整合知识 (Integration)

将提取的内容整合到自己的 skill 中：

**SKILL.md 整合策略：**

```markdown
---
name: my-skill
description: [整合后的描述，包含吸收的技能功能]
---

# My Skill

## 概述

[整合后的概述]

## 核心功能

### 原生功能
[你原来的功能]

### 从 [source-skill-name] 吸收的功能
[吸收的功能，注明来源]

## 工作流程

[整合后的工作流程]

## 资源

### Scripts
- `original_script.py` - [描述]
- `absorbed_script.py` - 从 [source] 吸收，用于 [功能]

### References
- `original_guide.md` - [描述]
- `absorbed_reference.md` - 从 [source] 吸收，包含 [内容]
```

### 5. 验证和测试 (Validation)

使用 skill-creator 的验证工具：

```bash
# 验证 skill 结构
python3 /Users/taevas/.claude/skills/skill-creator/scripts/quick_validate.py /path/to/your/skill

# 打包 skill
python3 /Users/taevas/.claude/skills/skill-creator/scripts/package_skill.py /path/to/your/skill
```

## 最佳实践

### 1. 选择性吸收
- 不要复制整个 skill，只吸收你需要的部分
- 理解代码/文档后再整合，不要盲目录入
- 保留原始来源的引用和归属

### 2. 保持一致性
- 确保吸收的内容与自己的 skill 风格一致
- 统一命名约定、文档格式、代码风格
- 整合重复的 functionality

### 3. 尊重版权和许可
- 检查原始 skill 的 LICENSE
- 遵守开源协议的归属要求
- 不要吸收专有或敏感内容

### 4. 持续学习
- 定期搜索新的 skill 来学习
- 关注 Anthropic 官方的 skill 更新
- 参与社区分享你自己的 skill

## 常用 GitHub 搜索查询

```bash
# 高星标的 claude skills
gh search repos "claude skill" --sort stars --limit 10

# 最近更新的 skills
gh search repos "claude-code skill" --sort updated --limit 10

# 特定语言的 skill 脚本
gh search repos "claude skill language:python" --limit 10

# 在 README 中提到 skill 的仓库
gh search repos "claude skill in:readme" --limit 10
```

## 资源

### Scripts
- `extract_skill.py` - 从源 skill 提取内容并整合到目标 skill
- `analyze_skill.py` - 分析 skill 结构和内容（可选）

### References
- `skill_structure.md` - Claude skill 标准结构和规范
- `github_search_tips.md` - GitHub 高级搜索技巧
