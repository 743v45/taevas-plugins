#!/usr/bin/env python3
"""Detect if a directory is a Hugo site root."""

import os
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_hugo_site.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
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
            print(f"  - {post}")
        if len(result['existing_posts']) > 10:
            print(f"  ... and {len(result['existing_posts']) - 10} more")


if __name__ == "__main__":
    main()