#!/usr/bin/env python3
"""Configuration manager for Hugo skill - caches Hugo version and site paths."""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


# Config file location: ~/.config/hugo-skill/config.json
CONFIG_DIR = Path.home() / ".config" / "hugo-skill"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir():
    """Ensure config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return {
            "hugo_version": None,
            "hugo_version_checked": None,
            "current_site": None,
            "sites": [],
            "last_updated": None
        }

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Ensure current_site exists for backward compatibility
            if "current_site" not in config:
                config["current_site"] = None
            return config
    except (json.JSONDecodeError, IOError):
        return {
            "hugo_version": None,
            "hugo_version_checked": None,
            "current_site": None,
            "sites": [],
            "last_updated": None
        }


def save_config(config: dict):
    """Save configuration to file."""
    ensure_config_dir()
    config["last_updated"] = datetime.now().isoformat()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def check_hugo_version(force: bool = False) -> dict:
    """
    Check Hugo version and cache result.

    Returns:
        - version: Hugo version string
        - cached: whether result was from cache
        - valid: whether Hugo is installed and working
    """
    config = load_config()

    # Return cached version if available and not forced
    if not force and config.get("hugo_version"):
        return {
            "version": config["hugo_version"],
            "cached": True,
            "valid": True
        }

    # Check Hugo version
    try:
        result = subprocess.run(
            ["hugo", "version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            version = result.stdout.strip()
            config["hugo_version"] = version
            config["hugo_version_checked"] = datetime.now().isoformat()
            save_config(config)

            return {
                "version": version,
                "cached": False,
                "valid": True
            }
        else:
            return {
                "version": None,
                "cached": False,
                "valid": False,
                "error": result.stderr.strip() or "Unknown error"
            }
    except FileNotFoundError:
        return {
            "version": None,
            "cached": False,
            "valid": False,
            "error": "Hugo not found. Please install Hugo first."
        }
    except subprocess.TimeoutExpired:
        return {
            "version": None,
            "cached": False,
            "valid": False,
            "error": "Hugo version check timed out"
        }


def find_hugo_sites(search_paths: list = None, force: bool = False) -> list:
    """
    Find all Hugo sites in search paths and cache results.

    Args:
        search_paths: List of directories to search (default: home and common locations)
        force: Force re-scan even if cached results exist

    Returns:
        List of site info dicts with path, config_file, content_dir
    """
    config = load_config()

    # Return cached sites if available and not forced
    if not force and config.get("sites"):
        return config["sites"]

    # Default search paths
    if search_paths is None:
        search_paths = [
            Path.home(),
            Path.home() / "code",
            Path.home() / "projects",
            Path.home() / "workspace",
            Path.home() / "work",
            Path.home() / "blog",
            Path.home() / "sites",
        ]

        # Add current directory if available
        try:
            search_paths.insert(0, Path.cwd())
        except Exception:
            pass

    sites = []
    config_names = ["config", "hugo"]
    config_extensions = [".toml", ".yaml", ".yml", ".json"]

    for base_path in search_paths:
        if not base_path.exists() or not base_path.is_dir():
            continue

        # Search for Hugo config files
        for config_name in config_names:
            for ext in config_extensions:
                pattern = f"**/{config_name}{ext}"
                for config_file in base_path.glob(pattern):
                    site_dir = config_file.parent

                    # Skip if it's inside another Hugo site's content directory
                    # Check if any parent directory is named "content"
                    parts = config_file.parts
                    if "content" in parts[:-1]:  # Exclude the filename itself
                        continue

                    # Verify it has a content directory
                    content_dir = site_dir / "content"
                    if content_dir.exists() and content_dir.is_dir():
                        sites.append({
                            "path": str(site_dir),
                            "config_file": str(config_file),
                            "content_dir": str(content_dir)
                        })

    # Remove duplicates based on path
    seen = set()
    unique_sites = []
    for site in sites:
        if site["path"] not in seen:
            seen.add(site["path"])
            unique_sites.append(site)

    # Update config
    config["sites"] = unique_sites
    save_config(config)

    return unique_sites


def get_current_site() -> dict:
    """
    Get the currently configured site.

    Returns:
        Site info dict or None if not configured
    """
    config = load_config()
    current_path = config.get("current_site")

    if not current_path:
        return None

    # Find site info from cached sites
    for site in config.get("sites", []):
        if Path(site["path"]).resolve() == Path(current_path).resolve():
            return site

    # Site path exists but not in cache, validate and return minimal info
    site_dir = Path(current_path)
    if site_dir.exists():
        return {
            "path": str(site_dir.resolve()),
            "config_file": None,
            "content_dir": str(site_dir / "content") if (site_dir / "content").exists() else None
        }

    return None


def set_current_site(site_path: str) -> dict:
    """
    Set the current Hugo site.

    Args:
        site_path: Path to the Hugo site

    Returns:
        Result dict with success status
    """
    site_dir = Path(site_path).resolve()

    if not site_dir.exists():
        return {
            "success": False,
            "error": f"Directory '{site_path}' does not exist"
        }

    # Validate it's a Hugo site
    config_names = ["config", "hugo"]
    config_extensions = [".toml", ".yaml", ".yml", ".json"]

    site_config = None
    for name in config_names:
        for ext in config_extensions:
            candidate = site_dir / f"{name}{ext}"
            if candidate.exists():
                site_config = str(candidate)
                break
        if site_config:
            break

    content_dir = site_dir / "content"
    if not site_config and not content_dir.exists():
        return {
            "success": False,
            "error": f"'{site_path}' is not a valid Hugo site (missing config or content directory)"
        }

    # Add to sites list if not already there
    config = load_config()
    existing_sites = config.get("sites", [])

    site_info = {
        "path": str(site_dir),
        "config_file": site_config,
        "content_dir": str(content_dir) if content_dir.exists() else None
    }

    # Update or add site in list
    found = False
    for i, s in enumerate(existing_sites):
        if Path(s["path"]).resolve() == site_dir:
            existing_sites[i] = site_info
            found = True
            break

    if not found:
        existing_sites.append(site_info)

    config["sites"] = existing_sites
    config["current_site"] = str(site_dir)
    save_config(config)

    return {
        "success": True,
        "site": site_info,
        "path": str(site_dir)
    }


def unset_current_site() -> dict:
    """
    Remove the current site setting.

    Returns:
        Result dict with success status
    """
    config = load_config()

    if not config.get("current_site"):
        return {
            "success": True,
            "was_set": False,
            "message": "No current site was configured"
        }

    config["current_site"] = None
    save_config(config)

    return {
        "success": True,
        "was_set": True,
        "message": "Current site setting removed"
    }


def add_site(site_path: str) -> dict:
    """
    Add a Hugo site to the cached list.

    Returns:
        Site info dict or error
    """
    config = load_config()
    site_dir = Path(site_path).resolve()

    # Check if already in list
    for site in config.get("sites", []):
        if Path(site["path"]).resolve() == site_dir:
            return {"success": True, "site": site, "already_exists": True}

    # Validate it's a Hugo site
    config_names = ["config", "hugo"]
    config_extensions = [".toml", ".yaml", ".yml", ".json"]

    site_config = None
    for name in config_names:
        for ext in config_extensions:
            candidate = site_dir / f"{name}{ext}"
            if candidate.exists():
                site_config = str(candidate)
                break
        if site_config:
            break

    content_dir = site_dir / "content"

    if not site_config or not content_dir.exists():
        return {
            "success": False,
            "error": f"'{site_path}' is not a valid Hugo site (missing config or content directory)"
        }

    new_site = {
        "path": str(site_dir),
        "config_file": site_config,
        "content_dir": str(content_dir)
    }

    config.setdefault("sites", []).append(new_site)
    save_config(config)

    return {"success": True, "site": new_site, "already_exists": False}


def remove_site(site_path: str) -> dict:
    """
    Remove a Hugo site from the cached list.
    """
    config = load_config()
    site_dir = Path(site_path).resolve()

    original_count = len(config.get("sites", []))
    config["sites"] = [
        s for s in config.get("sites", [])
        if Path(s["path"]).resolve() != site_dir
    ]

    if len(config["sites"]) == original_count:
        return {"success": False, "error": f"Site '{site_path}' not found in cached list"}

    save_config(config)
    return {"success": True, "removed": str(site_dir)}


def list_sites() -> list:
    """List all cached Hugo sites."""
    config = load_config()
    return config.get("sites", [])


def select_site_interactive(force_scan: bool = False) -> dict:
    """
    Interactive site selection with three options:
    1. Select from scanned sites (confirm with user)
    2. User provides custom path
    3. Scan default path (~)

    Returns:
        - selected: bool (whether a site was selected)
        - site: site info dict or None
        - action: "selected" | "custom" | "default" | "cancelled"
    """
    # First, try to get cached or scan for sites
    sites = find_hugo_sites(force=force_scan)

    # Check for current site
    current = get_current_site()
    if current:
        print(f"\n当前配置的站点: {current['path']}")
        use_current = input("使用当前站点？[Y/n]: ").strip().lower()
        if use_current in ('', 'y', 'yes'):
            return {
                "selected": True,
                "site": current,
                "action": "selected"
            }

    print("\n=== Hugo 站点选择 ===")
    print("请选择操作方式：")
    print("  0. 输入自定义路径")
    print("  1. 扫描默认路径 (~)")

    if sites:
        print(f"\n已找到 {len(sites)} 个可用 Hugo 站点：")
        for i, site in enumerate(sites, 2):
            print(f"  {i}. {site['path']}")

    print()

    while True:
        try:
            choice = input("请输入选项编号: ").strip()

            if not choice:
                if sites and len(sites) == 1:
                    # Auto-select if only one site
                    print(f"\n自动选择唯一站点: {sites[0]['path']}")
                    return {
                        "selected": True,
                        "site": sites[0],
                        "action": "selected"
                    }
                continue

            choice_num = int(choice)

            if choice_num == 0:
                # Custom path
                custom_path = input("请输入 Hugo 站点路径: ").strip()
                if custom_path:
                    # Validate and add the site
                    result = add_site(custom_path)
                    if result["success"]:
                        print(f"已添加站点: {result['site']['path']}")
                        return {
                            "selected": True,
                            "site": result["site"],
                            "action": "custom"
                        }
                    else:
                        print(f"错误: {result['error']}")
                        continue
                else:
                    print("路径不能为空")
                    continue

            elif choice_num == 1:
                # Scan default path (~)
                home_path = Path.home()
                print(f"\n正在扫描 {home_path}...")
                sites = find_hugo_sites(search_paths=[home_path], force=True)

                if sites:
                    print(f"找到 {len(sites)} 个可用站点：")
                    for i, site in enumerate(sites, 1):
                        print(f"  {i}. {site['path']}")

                    if len(sites) == 1:
                        print(f"\n自动选择: {sites[0]['path']}")
                        return {
                            "selected": True,
                            "site": sites[0],
                            "action": "default"
                        }

                    # Let user select from scanned sites
                    sub_choice = input("请选择站点编号: ").strip()
                    try:
                        sub_num = int(sub_choice)
                        if 1 <= sub_num <= len(sites):
                            return {
                                "selected": True,
                                "site": sites[sub_num - 1],
                                "action": "default"
                            }
                        else:
                            print(f"请输入 1-{len(sites)} 之间的数字")
                    except ValueError:
                        print("请输入有效数字")
                else:
                    print(f"在 {home_path} 下未找到 Hugo 站点")
                continue

            elif sites and 2 <= choice_num <= len(sites) + 1:
                # Select from existing sites
                site_idx = choice_num - 2
                selected_site = sites[site_idx]

                # Confirm with user
                confirm = input(f"确认使用站点 '{selected_site['path']}'? [Y/n]: ").strip().lower()
                if confirm in ('', 'y', 'yes'):
                    return {
                        "selected": True,
                        "site": selected_site,
                        "action": "selected"
                    }
                else:
                    print("已取消，请重新选择")
                    continue

            else:
                max_option = len(sites) + 1 if sites else 1
                print(f"请输入 0-{max_option} 之间的数字")

        except ValueError:
            print("请输入有效数字")
        except KeyboardInterrupt:
            print("\n已取消")
            return {
                "selected": False,
                "site": None,
                "action": "cancelled"
            }


def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Hugo Skill Configuration Manager")
        print("\nUsage:")
        print("  config_manager.py version [--force]    Check Hugo version")
        print("  config_manager.py sites [--force]      Find Hugo sites")
        print("  config_manager.py list                 List cached sites")
        print("  config_manager.py add <path>           Add a site to cache")
        print("  config_manager.py remove <path>        Remove a site from cache")
        print("  config_manager.py set-current <path>   Set the current site")
        print("  config_manager.py unset-current        Remove current site setting")
        print("  config_manager.py select [--force]     Interactive site selection")
        print("  config_manager.py show                 Show full config")
        sys.exit(1)

    command = sys.argv[1]

    if command == "version":
        force = "--force" in sys.argv or "-f" in sys.argv
        result = check_hugo_version(force)

        if result["valid"]:
            if result["cached"]:
                print(f"Hugo version (cached): {result['version']}")
            else:
                print(f"Hugo version: {result['version']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")

    elif command == "sites":
        force = "--force" in sys.argv or "-f" in sys.argv
        sites = find_hugo_sites(force=force)

        if sites:
            print(f"Found {len(sites)} Hugo site(s):")
            for i, site in enumerate(sites, 1):
                print(f"  {i}. {site['path']}")
                print(f"     Config: {site['config_file']}")
        else:
            print("No Hugo sites found. You can add one manually with:")
            print("  config_manager.py add <path>")

    elif command == "list":
        sites = list_sites()
        current = get_current_site()

        if current:
            print(f"当前站点: {current['path']}")
            print()

        if sites:
            print(f"缓存的 Hugo 站点 ({len(sites)}):")
            for i, site in enumerate(sites, 1):
                marker = " *" if current and site["path"] == current.get("path") else ""
                print(f"  {i}. {site['path']}{marker}")
        else:
            print("没有缓存的站点。请使用 'config_manager.py add <path>' 添加站点。")

    elif command == "add":
        if len(sys.argv) < 3:
            print("Usage: config_manager.py add <path>")
            sys.exit(1)

        result = add_site(sys.argv[2])
        if result["success"]:
            if result.get("already_exists"):
                print(f"Site already cached: {result['site']['path']}")
            else:
                print(f"Added site: {result['site']['path']}")
        else:
            print(f"Error: {result['error']}")

    elif command == "remove":
        if len(sys.argv) < 3:
            print("Usage: config_manager.py remove <path>")
            sys.exit(1)

        result = remove_site(sys.argv[2])
        if result["success"]:
            print(f"Removed site: {result['removed']}")
        else:
            print(f"Error: {result['error']}")

    elif command == "set-current":
        if len(sys.argv) < 3:
            print("Usage: config_manager.py set-current <path>")
            sys.exit(1)

        result = set_current_site(sys.argv[2])
        if result["success"]:
            print(f"已设置当前站点: {result['path']}")
        else:
            print(f"错误: {result['error']}")

    elif command == "unset-current":
        result = unset_current_site()
        if result["success"]:
            if result["was_set"]:
                print("已移除当前站点设置")
            else:
                print(result["message"])

    elif command == "show":
        config = load_config()
        print(json.dumps(config, indent=2, ensure_ascii=False))

    elif command == "select":
        force = "--force" in sys.argv or "-f" in sys.argv
        result = select_site_interactive(force_scan=force)

        if result["selected"]:
            print(f"\n已选择站点: {result['site']['path']}")
            print(f"操作方式: {result['action']}")
            # Output JSON for easy parsing by caller
            print("\n--- JSON OUTPUT ---")
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("未选择站点")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()