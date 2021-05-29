import os
import re

from jinja2 import Environment, FileSystemLoader


class Pug:
    def __init__(self, src: str, dest: str, debug: bool = False):
        self.src = src
        self.dest = dest
        self.debug = debug

        self.ignore = r"_.*\.pug"
        self.compile = r".*\.pug"

        self.env = Environment(
            loader=FileSystemLoader(self.src),
            extensions=["pypugjs.ext.jinja.PyPugJSExtension"]
        )

    def print_debug(self, text):
        if self.debug:
            print(text)

    def render(self, path: str, filename: str):
        pretty_location = path.replace(os.sep, "/")
        self.print_debug(f"RENDER: {pretty_location} -> {filename}")

        try:
            return self.env.get_template(filename).render()
        except Exception as e:
            print(f"ERROR {pretty_location} -> {filename}: {e}")

    def read(self, location: str, encoding="utf8"):
        with open(location, "r", encoding=encoding) as f:
            self.print_debug(f"READ: {location}")
            return f.read()

    def write(self, location: str, data: str, encoding="utf8"):
        with open(location, "w", encoding=encoding) as f:
            self.print_debug(f"WRITE: {location}")
            return f.write(data)

    def old_files(self):
        for path, dirs, files in os.walk(self.dest):
            for file in files:
                pwd = os.path.join(path, file)
                dist = pwd.replace(self.dest, self.src).replace(".html", ".pug")
                if not os.path.exists(dist):
                    os.remove(pwd)
                    self.print_debug(f"DELETE: {pwd}")

    def compile_pug(self, file: str, path: str = None):
        if not path:
            path = os.path.dirname(file)
            file = os.path.basename(file)

        pwd = os.path.join(path, file)

        if re.compile(self.ignore).search(file):
            self.print_debug(f"SKIPPED: {pwd}")
            return

        dist = pwd.replace(self.src, self.dest)
        if re.compile(self.compile).search(file):
            data = self.render(path, file)
            dist = dist.replace(".pug", ".html")
        else:
            data = self.read(pwd)

        if data:
            self.write(dist, data)
        else:
            print(f"ERROR {pwd}: Data content was empty, skipping")

    def compiler(self, everything: bool = True, watch_file: str = None):
        if everything:
            for path, dirs, files in os.walk(self.src):
                for file in files:
                    self.compile_pug(file, path)
        else:
            self.compile_pug(watch_file)

        self.old_files()
