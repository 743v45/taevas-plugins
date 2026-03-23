#!/usr/bin/env python3
"""
Skill Analyzer - 分析 skill 结构和内容

Usage:
    python analyze_skill.py <skill_path>

Example:
    python analyze_skill.py /path/to/skill
"""

import os
import sys
import yaml
from pathlib import Path


def count_lines(file_path):
    """计算文件行数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except:
        return 0


def analyze_skill(skill_path):
    """分析 skill 结构"""
    skill_path = os.path.abspath(skill_path)

    if not os.path.exists(skill_path):
        print(f"❌ 错误: 路径不存在: {skill_path}")
        sys.exit(1)

    print(f"\n🔍 分析 Skill: {skill_path}\n")

    # 检查 SKILL.md
    skill_md_path = os.path.join(skill_path, 'SKILL.md')
    if os.path.exists(skill_md_path):
        print("✅ 找到 SKILL.md")

        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析 frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    print(f"\n📋 Frontmatter:")
                    print(f"   名称: {frontmatter.get('name', 'N/A')}")
                    print(f"   描述: {frontmatter.get('description', 'N/A')[:80]}...")
                except yaml.YAMLError as e:
                    print(f"⚠️  解析 frontmatter 失败: {e}")

        # 统计 body
        body_lines = len(content.split('\n'))
        print(f"\n📝 内容统计:")
        print(f"   总行数: {body_lines}")

        # 提取标题
        import re
        headers = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        if headers:
            print(f"\n📑 主要章节:")
            for header in headers[:10]:  # 最多显示 10 个
                print(f"   - {header}")
    else:
        print("❌ 未找到 SKILL.md")

    # 分析子目录
    print(f"\n📂 资源目录:")
    for dir_name in ['scripts', 'references', 'assets']:
        dir_path = os.path.join(skill_path, dir_name)
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            total_size = sum(
                os.path.getsize(os.path.join(dir_path, f))
                for f in files
                if os.path.isfile(os.path.join(dir_path, f))
            )
            print(f"   ✅ {dir_name}/: {len(files)} 个文件, {total_size/1024:.1f} KB")

            # 显示前 5 个文件
            for f in sorted(files)[:5]:
                file_path = os.path.join(dir_path, f)
                if os.path.isfile(file_path):
                    lines = count_lines(file_path)
                    print(f"      - {f} ({lines} 行)")
        else:
            print(f"   ❌ {dir_name}/: 不存在")

    print("\n✅ 分析完成！\n")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    skill_path = sys.argv[1]
    analyze_skill(skill_path)


if __name__ == '__main__':
    main()
