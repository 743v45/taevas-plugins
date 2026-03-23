#!/usr/bin/env python3
"""
Skill Extractor - 从源 skill 提取内容并整合到目标 skill

Usage:
    python extract_skill.py <source_skill_path> <target_skill_path>

Example:
    python extract_skill.py /tmp/skill-analysis /Users/taevas/.claude/skills/my-skill
"""

import os
import sys
import shutil
import re
from pathlib import Path


def parse_skill_md(skill_path):
    """解析 SKILL.md 文件，提取 frontmatter 和 body"""
    skill_md_path = os.path.join(skill_path, 'SKILL.md')

    if not os.path.exists(skill_md_path):
        print(f"❌ 错误: 未找到 SKILL.md: {skill_md_path}")
        return None, None, None

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析 frontmatter
    frontmatter = {}
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            import yaml
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
            except yaml.YAMLError as e:
                print(f"⚠️  解析 frontmatter 失败: {e}")

    return frontmatter, body, content


def merge_directories(source, target, overwrite=False):
    """合并两个目录

    Args:
        source: 源目录
        target: 目标目录
        overwrite: 是否覆盖已有文件
    """
    if not os.path.exists(source):
        return

    if not os.path.exists(target):
        shutil.copytree(source, target)
        print(f"  ✅ 复制目录: {os.path.basename(source)}")
        return

    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        target_path = os.path.join(target, item)

        if os.path.isdir(source_path):
            merge_directories(source_path, target_path, overwrite)
        else:
            if not os.path.exists(target_path):
                shutil.copy2(source_path, target_path)
                print(f"  ✅ 复制文件: {item}")
            elif overwrite:
                shutil.copy2(source_path, target_path)
                print(f"  🔄 覆盖文件: {item}")
            else:
                print(f"  ⏭️  跳过已存在: {item}")


def extract_skill(source_path, target_path):
    """从源 skill 提取内容到目标 skill"""

    source_path = os.path.abspath(source_path)
    target_path = os.path.abspath(target_path)

    print(f"\n🔍 分析源 skill: {source_path}")
    print(f"🎯 目标 skill: {target_path}\n")

    # 验证源 skill
    if not os.path.exists(os.path.join(source_path, 'SKILL.md')):
        print(f"❌ 错误: 源目录不是有效的 skill (缺少 SKILL.md)")
        sys.exit(1)

    # 解析源 skill
    source_frontmatter, source_body, source_content = parse_skill_md(source_path)

    if source_frontmatter:
        print(f"📋 源 skill 名称: {source_frontmatter.get('name', 'Unknown')}")
        print(f"📝 源 skill 描述: {source_frontmatter.get('description', 'No description')[:100]}...")

    # 确保目标目录存在
    os.makedirs(target_path, exist_ok=True)

    # 复制资源目录
    print("\n📂 复制资源:")
    for dir_name in ['scripts', 'references', 'assets']:
        source_dir = os.path.join(source_path, dir_name)
        target_dir = os.path.join(target_path, dir_name)
        if os.path.exists(source_dir):
            merge_directories(source_dir, target_dir)

    # 生成吸收报告
    report_path = os.path.join(target_path, 'references', 'absorption_report.md')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Skill Absorption Report\n\n")
        f.write(f"**吸收时间**: {os.popen('date').read().strip()}\n")
        f.write(f"**源 Skill**: {source_path}\n")
        f.write(f"**源 Skill 名称**: {source_frontmatter.get('name', 'Unknown') if source_frontmatter else 'Unknown'}\n\n")
        f.write(f"## 源 Skill 描述\n\n")
        f.write(f"{source_frontmatter.get('description', 'No description') if source_frontmatter else 'N/A'}\n\n")
        f.write(f"## 吸收的资源\n\n")

        for dir_name in ['scripts', 'references', 'assets']:
            source_dir = os.path.join(source_path, dir_name)
            if os.path.exists(source_dir):
                f.write(f"### {dir_name}/\n")
                for item in os.listdir(source_dir):
                    f.write(f"- {item}\n")
                f.write("\n")

        f.write(f"## 整合建议\n\n")
        f.write(f"1. 查看并理解复制的资源\n")
        f.write(f"2. 将有用部分整合到 SKILL.md\n")
        f.write(f"3. 确保风格和命名一致\n")
        f.write(f"4. 注明来源和归属\n")

    print(f"\n📄 吸收报告已保存: {report_path}")
    print(f"✅ Skill 吸收完成！")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    source = sys.argv[1]
    target = sys.argv[2]

    extract_skill(source, target)


if __name__ == '__main__':
    main()
