import argparse
import sys
import shlex
import pug_watcher
import json
import time
import re

from watchgod import watch
from . import Pug


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


def getargs():
    args = sys.argv
    args[0] = ""
    return " ".join(args)


def kill(value: int = 0, msg: str = None):
    if msg:
        print(msg)
    sys.exit(value)


def shell():
    """ The shell/command manager """
    arguments = getargs()
    parser = Arguments(description="Simple command-line Pug watcher")
    parser.add_argument("-v", "--version", action="store_true", default=False, help="Shows the version and exits")
    parser.add_argument("-p", "--path", nargs="?", help="Choose the path where the script will read and then write to (from/path:to/path)")
    parser.add_argument("-w", "--watch", action="store_true", default=False, help="Make the script run endlessly and watch changes")
    parser.add_argument("-c", "--config", action="store_true", default=False, help="Get settings from a '.pug_watcher.json' file")
    parser.add_argument("-d", "--debug", action="store_true", default=False, help="Enable debug mode")

    try:
        arguments = arguments.replace("\\", "/")
        args = parser.parse_args(shlex.split(arguments))
    except Exception as e:
        kill(0, e)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        kill(1)

    if args.version:
        kill(0, f"pug_watcher v{pug_watcher.__version__}")

    config = {}
    if args.config:
        try:
            with open(".pug_watcher.json", "r", encoding="utf8") as f:
                config = json.load(f)
        except FileNotFoundError:
            kill(0, "I was unable to find a config file named '.pug_watcher.json'")

    settings = {
        "watch": config.get("watch", args.watch),
        "path": config.get("path", args.path),
        "debug": config.get("debug", args.debug),
        "variables": config.get("variables", {})
    }

    if settings["path"]:
        find_paths = re.compile(r"(.*):(.*)").search(settings["path"])
        if not find_paths:
            kill(0, "Path must be valid, it must be 'Source/Folder:Dest/Folder'")
        src = find_paths.group(1)
        dest = find_paths.group(2)
    else:
        src, dest = "./src", "./dist"

    pug = Pug(src, dest, debug=settings["debug"])

    if settings["watch"]:
        print("Compiling everything first...")
        pug.compiler(variables=settings["variables"])

        print(f"Started watcher from source folder '{src}' to destination folder '{dest}'")
        for changes in watch(src):
            if len(changes) == 1:
                change, file = next(iter(changes), (None, ""))
                if change == 2 and file:
                    pug.compiler(
                        everything=False,
                        watch_file=file,
                        variables=settings["variables"]
                    )
                elif change == 3:
                    pug.old_files()
    else:
        print(f"Compiling from source folder '{src}' to destination folder '{dest}'")
        before = time.monotonic()
        pug.compiler(variables=settings["variables"])
        print(f"Done compiling | {int((time.monotonic() - before) * 1000)}ms")


def main():
    """ This is used by the cmd handler """
    try:
        shell()
    except KeyboardInterrupt:
        print("Stopping process...")
