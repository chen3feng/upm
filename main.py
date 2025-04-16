# upm.py - Unreal Plugin Manager using Git Subtree

import os
import json
import subprocess
import argparse

CONFIG_FILE = "Plugins/upm-plugins.json"

def find_project_root():
    path = os.getcwd()
    while path != os.path.dirname(path):
        for file in os.listdir(path):
            if file.endswith(".uproject"):
                return path
        path = os.path.dirname(path)
    return None

def load_config(project_root):
    config_path = os.path.join(project_root, CONFIG_FILE)
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {"plugins": {}}

def save_config(project_root, config):
    config_path = os.path.join(project_root, CONFIG_FILE)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def add_plugin(name, url, ref, project_root):
    path = f"Plugins/{name}"
    print(f"➕ Adding plugin {name} from {url} ({ref}) to {path}...")
    subprocess.run(["git", "subtree", "add", "--prefix", path, url, ref, "--squash"])

    config = load_config(project_root)
    config["plugins"][name] = {"url": url, "ref": ref, "path": path}
    save_config(project_root, config)

def pull_plugin(name, plugin, project_root):
    print(f"🔄 Pulling plugin {name}...")
    subprocess.run(["git", "subtree", "pull", "--prefix", plugin["path"], plugin["url"], plugin["ref"], "--squash"])

def push_plugin(name, plugin):
    print(f"⬆️  Pushing plugin {name}...")
    subprocess.run(["git", "subtree", "push", "--prefix", plugin["path"], plugin["url"], plugin["ref"]])

def pull_all(project_root):
    config = load_config(project_root)
    for name, plugin in config["plugins"].items():
        pull_plugin(name, plugin, project_root)

def show_help():
    print("""
Unreal Plugin Manager (upm) - using git subtree

Usage:
  upm add <url> [name] [--ref ref]     Add a new plugin
  upm pull <name>                      Pull updates for a plugin
  upm push <name>                      Push local changes to plugin repo
  upm pull-all                         Pull updates for all plugins
  upm help                             Show this help
    """)

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('command', nargs='?', default='help')
    parser.add_argument('args', nargs='*')
    parser.add_argument('--ref', default='main')
    args = parser.parse_args()

    project_root = find_project_root()
    if not project_root:
        print("❌ You are not in a unreal project")
        return

    config = load_config(project_root)

    if not args.command:
        parser.print_help()
        return

    if args.command == 'add':
        if len(args.args) < 1:
            print("❌ Missing plugin URL")
            return
        url = args.args[0]
        name = args.args[1] if len(args.args) > 1 else os.path.basename(url).replace('.git', '')
        add_plugin(name, url, args.ref, project_root)

    elif args.command == 'pull':
        name = args.args[0] if args.args else None
        if not name or name not in config["plugins"]:
            print("❌ Missing or unknown plugin name")
            return
        pull_plugin(name, config["plugins"][name], project_root)

    elif args.command == 'push':
        name = args.args[0] if args.args else None
        if not name or name not in config["plugins"]:
            print("❌ Missing or unknown plugin name")
            return
        push_plugin(name, config["plugins"][name])

    elif args.command == 'pull-all':
        pull_all(project_root)

    else:
        show_help()

if __name__ == "__main__":
    main()
