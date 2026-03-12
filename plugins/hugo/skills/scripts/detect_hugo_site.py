#!/usr/bin/env python3
"""Detect if a directory is a Hugo site root and manage posts."""

import os
import re
import sys
from pathlib import Path


def is_hugo_site(directory: str) -> dict:
    """
    Check if directory is a Hugo site root.

    Returns dict with:
        - is_hugo_site: bool
        - config_file: str or None (config.toml/yaml/yml/json or hugo.toml/yaml/yml/json)
        - content_dir: str or None
        - existing_posts: list of .md files in content/posts/
    """
    dir_path = Path(directory).resolve()

    result = {
        "is_hugo_site": False,
        "config_file": None,
        "content_dir": None,
        "existing_posts": []
    }

    # Check for config files (Hugo supports multiple names/formats)
    config_names = ["config", "hugo"]
    config_extensions = [".toml", ".yaml", ".yml", ".json"]

    for name in config_names:
        for ext in config_extensions:
            config_path = dir_path / f"{name}{ext}"
            if config_path.exists():
                result["config_file"] = str(config_path)
                result["is_hugo_site"] = True
                break
        if result["config_file"]:
            break

    # Also check config/ directory
    config_dir = dir_path / "config"
    if config_dir.exists() and config_dir.is_dir():
        for ext in config_extensions:
            config_path = config_dir / f"_default{ext}"
            if config_path.exists():
                result["config_file"] = str(config_path)
                result["is_hugo_site"] = True
                break

    # Check for content directory
    content_path = dir_path / "content"
    if content_path.exists() and content_path.is_dir():
        result["content_dir"] = str(content_path)
        result["is_hugo_site"] = True

        # Find existing posts
        posts_dir = content_path / "posts"
        if posts_dir.exists():
            result["existing_posts"] = [
                str(f.relative_to(dir_path))
                for f in posts_dir.rglob("*.md")
            ]

    return result


def extract_title(file_path: str) -> str:
    """Extract title from markdown file's front matter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try TOML format (+++)
        toml_match = re.search(r'^\+\+\+\s*\n(.*?)^\+\+\+', content, re.MULTILINE | re.DOTALL)
        if toml_match:
            front_matter = toml_match.group(1)
            title_match = re.search(r'^title\s*=\s*["\'](.+?)["\']', front_matter, re.MULTILINE)
            if title_match:
                return title_match.group(1)

        # Try YAML format (---)
        yaml_match = re.search(r'^---\s*\n(.*?)^---', content, re.MULTILINE | re.DOTALL)
        if yaml_match:
            front_matter = yaml_match.group(1)
            title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', front_matter, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip('"\'').strip()

        return ""
    except Exception:
        return ""


def search_posts(directory: str, keywords: str) -> list:
    """
    Search for posts matching keywords in title or filename.

    Returns list of dicts with:
        - path: relative path to post
        - title: post title from front matter
        - match_score: relevance score
    """
    dir_path = Path(directory).resolve()
    posts_dir = dir_path / "content" / "posts"

    if not posts_dir.exists():
        return []

    keywords_lower = keywords.lower()
    results = []

    for md_file in posts_dir.rglob("*.md"):
        filename = md_file.stem.lower()
        title = extract_title(str(md_file)).lower()

        # Calculate match score
        score = 0

        # Check keyword in filename
        if keywords_lower in filename:
            score += 10

        # Check keyword in title
        if keywords_lower in title:
            score += 20

        # Check individual words
        for word in keywords_lower.split():
            if word in filename:
                score += 3
            if word in title:
                score += 5

        if score > 0:
            results.append({
                "path": str(md_file.relative_to(dir_path)),
                "title": extract_title(str(md_file)),
                "match_score": score
            })

    # Sort by score descending
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_hugo_site.py <directory> [search_keywords]")
        print("\nCommands:")
        print("  <directory>              Check if directory is a Hugo site")
        print("  <directory> <keywords>   Search for posts matching keywords")
        sys.exit(1)

    directory = sys.argv[1]

    # Search mode
    if len(sys.argv) >= 3:
        keywords = " ".join(sys.argv[2:])
        results = search_posts(directory, keywords)

        print(f"Searching for: '{keywords}'")
        print(f"Found {len(results)} matching post(s):")

        for post in results:
            print(f"  - [{post['path']}] \"{post['title']}\" (score: {post['match_score']})")

        if not results:
            print("  No matching posts found.")
        return

    # Detection mode
    result = is_hugo_site(directory)

    print(f"Directory: {directory}")
    print(f"Is Hugo site: {result['is_hugo_site']}")
    if result['config_file']:
        print(f"Config file: {result['config_file']}")
    if result['content_dir']:
        print(f"Content dir: {result['content_dir']}")
    if result['existing_posts']:
        print(f"Existing posts ({len(result['existing_posts'])}):")
        for post in result['existing_posts'][:10]:  # Show first 10
            title = extract_title(str(Path(directory) / post))
            print(f"  - {post} \"{title}\"")
        if len(result['existing_posts']) > 10:
            print(f"  ... and {len(result['existing_posts']) - 10} more")


if __name__ == "__main__":
    main()