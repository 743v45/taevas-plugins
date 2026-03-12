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
            "last_updated": None
        }

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {
            "hugo_version": None,
            "hugo_version_checked": None,
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

    return unique_sites


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
        if sites:
            print(f"Cached Hugo sites ({len(sites)}):")
            for i, site in enumerate(sites, 1):
                print(f"  {i}. {site['path']}")
        else:
            print("No cached sites. Run 'config_manager.py sites' to scan, or add manually.")

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

    elif command == "rescan":
        print("Re-scanning for Hugo sites...")
        sites = find_hugo_sites(force=True)
        print(f"Found {len(sites)} Hugo site(s):")
        for i, site in enumerate(sites, 1):
            print(f"  {i}. {site['path']}")

    elif command == "show":
        config = load_config()
        print(json.dumps(config, indent=2, ensure_ascii=False))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()