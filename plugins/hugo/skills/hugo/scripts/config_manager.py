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
            "sites": [],
            "blacklist": [],
            "last_updated": None
        }

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Ensure blacklist exists for backward compatibility
            if "blacklist" not in config:
                config["blacklist"] = []
            return config
    except (json.JSONDecodeError, IOError):
        return {
            "hugo_version": None,
            "hugo_version_checked": None,
            "sites": [],
            "blacklist": [],
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


def find_hugo_sites(search_paths: list = None, force: bool = False, include_blacklisted: bool = False) -> list:
    """
    Find all Hugo sites in search paths and cache results.

    Args:
        search_paths: List of directories to search (default: home and common locations)
        force: Force re-scan even if cached results exist
        include_blacklisted: If True, return all sites including blacklisted ones

    Returns:
        List of site info dicts with path, config_file, content_dir
    """
    config = load_config()

    # Return cached sites if available and not forced
    if not force and config.get("sites"):
        sites = config["sites"]
    else:
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
            except:
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
                        if "content" in str(config_file):
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

        sites = unique_sites

    # Filter out blacklisted sites if not explicitly including them
    if not include_blacklisted:
        blacklist = config.get("blacklist", [])
        blacklisted_paths = {Path(p).resolve() for p in blacklist}
        sites = [
            s for s in sites
            if Path(s["path"]).resolve() not in blacklisted_paths
        ]

    return sites


def get_blacklisted_sites() -> list:
    """
    Get all blacklisted sites with their info.

    Returns:
        List of site info dicts that are in the blacklist
    """
    config = load_config()
    blacklist = config.get("blacklist", [])

    if not blacklist:
        return []

    # Get full site info for blacklisted paths
    blacklisted_sites = []
    all_sites = config.get("sites", [])

    for path in blacklist:
        # Find site info from cached sites
        site_info = None
        for site in all_sites:
            if Path(site["path"]).resolve() == Path(path).resolve():
                site_info = site.copy()
                break

        if not site_info:
            # Site not in cache, create minimal info
            site_info = {
                "path": path,
                "config_file": None,
                "content_dir": None
            }

        blacklisted_sites.append(site_info)

    return blacklisted_sites


def blacklist_site(site_path: str) -> dict:
    """
    Add a site to the blacklist.

    Args:
        site_path: Path to the Hugo site

    Returns:
        Result dict with success status
    """
    config = load_config()
    site_dir = Path(site_path).resolve()

    # Initialize blacklist if not exists
    if "blacklist" not in config:
        config["blacklist"] = []

    # Check if already blacklisted
    blacklisted_paths = [Path(p).resolve() for p in config["blacklist"]]
    if site_dir in blacklisted_paths:
        return {
            "success": True,
            "already_blacklisted": True,
            "path": str(site_dir)
        }

    # Add to blacklist
    config["blacklist"].append(str(site_dir))
    save_config(config)

    return {
        "success": True,
        "already_blacklisted": False,
        "path": str(site_dir)
    }


def unblacklist_site(site_path: str) -> dict:
    """
    Remove a site from the blacklist.

    Args:
        site_path: Path to the Hugo site

    Returns:
        Result dict with success status
    """
    config = load_config()
    site_dir = Path(site_path).resolve()

    blacklist = config.get("blacklist", [])
    original_count = len(blacklist)

    config["blacklist"] = [
        p for p in blacklist
        if Path(p).resolve() != site_dir
    ]

    if len(config["blacklist"]) == original_count:
        return {
            "success": False,
            "error": f"Site '{site_path}' is not in blacklist"
        }

    save_config(config)

    return {
        "success": True,
        "path": str(site_dir)
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

    # Get blacklisted sites for display
    blacklisted = get_blacklisted_sites()

    print("\n=== Hugo 站点选择 ===")
    print("请选择操作方式：")
    print("  0. 输入自定义路径")
    print("  1. 扫描默认路径 (~)")

    if sites:
        print(f"\n已找到 {len(sites)} 个可用 Hugo 站点：")
        for i, site in enumerate(sites, 2):
            print(f"  {i}. {site['path']}")

    # Show blacklisted sites separately
    if blacklisted:
        print(f"\n[黑名单] {len(blacklisted)} 个站点已禁用：")
        for i, site in enumerate(blacklisted, 1):
            print(f"  - {site['path']}")

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
                    # Check if blacklisted
                    custom_path_resolved = Path(custom_path).resolve()
                    blacklisted_paths = [Path(p).resolve() for p in [s["path"] for s in blacklisted]]
                    if custom_path_resolved in blacklisted_paths:
                        print(f"警告: '{custom_path}' 在黑名单中")
                        confirm = input("是否要从黑名单移除并使用？[y/N]: ").strip().lower()
                        if confirm in ('y', 'yes'):
                            unblacklist_site(custom_path)
                            print(f"已从黑名单移除: {custom_path}")
                        else:
                            print("已取消")
                            continue

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
        print("  config_manager.py rescan               Re-scan for Hugo sites")
        print("  config_manager.py select [--force]     Interactive site selection")
        print("  config_manager.py blacklist <path>     Add a site to blacklist")
        print("  config_manager.py unblacklist <path>   Remove a site from blacklist")
        print("  config_manager.py blacklist-list       List blacklisted sites")
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
        blacklisted = get_blacklisted_sites()

        if sites:
            print(f"Cached Hugo sites ({len(sites)}):")
            for i, site in enumerate(sites, 1):
                print(f"  {i}. {site['path']}")
        else:
            print("No cached sites. Run 'config_manager.py sites' to scan, or add manually.")

        if blacklisted:
            print(f"\nBlacklisted sites ({len(blacklisted)}):")
            for site in blacklisted:
                print(f"  - {site['path']}")

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

    elif command == "blacklist":
        if len(sys.argv) < 3:
            print("Usage: config_manager.py blacklist <path>")
            sys.exit(1)

        result = blacklist_site(sys.argv[2])
        if result["success"]:
            if result.get("already_blacklisted"):
                print(f"Site already blacklisted: {result['path']}")
            else:
                print(f"Added to blacklist: {result['path']}")
                print("Note: This site will be excluded from selection and scanning.")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")

    elif command == "unblacklist":
        if len(sys.argv) < 3:
            print("Usage: config_manager.py unblacklist <path>")
            sys.exit(1)

        result = unblacklist_site(sys.argv[2])
        if result["success"]:
            print(f"Removed from blacklist: {result['path']}")
        else:
            print(f"Error: {result['error']}")

    elif command == "blacklist-list":
        blacklisted = get_blacklisted_sites()
        if blacklisted:
            print(f"Blacklisted sites ({len(blacklisted)}):")
            for i, site in enumerate(blacklisted, 1):
                print(f"  {i}. {site['path']}")
        else:
            print("No blacklisted sites.")

    elif command == "rescan":
        print("Re-scanning for Hugo sites...")
        sites = find_hugo_sites(force=True)
        blacklisted = get_blacklisted_sites()

        print(f"Found {len(sites)} available Hugo site(s):")
        for i, site in enumerate(sites, 1):
            print(f"  {i}. {site['path']}")

        if blacklisted:
            print(f"\n[Blacklisted] {len(blacklisted)} site(s) excluded:")
            for site in blacklisted:
                print(f"  - {site['path']}")

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