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

    def render(self, path: str, filename: str, variables: dict = {}):
        pretty_location = path.replace(os.sep, "/")
        pug_file_location = pretty_location.replace(self.src, "./")
        self.print_debug(f"RENDER: {pretty_location} -> {filename}")

        try:
            return self.env.get_template(f"{pug_file_location}/{filename}").render(variables)
        except Exception as e:
            print(f"ERROR {pretty_location} -> {filename}: {e}")

    def read(self, location: str, encoding="utf8"):
        self.print_debug(f"READ: {location}")
        try:
            with open(location, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            with open(location, "rb") as f:
                return f.read()

    def write(self, location: str, data: str, encoding="utf8"):
        if not os.path.exists(os.path.dirname(location)):
            os.makedirs(os.path.dirname(location))

        self.print_debug(f"WRITE: {location}")
        try:
            with open(location, "w", encoding=encoding) as f:
                return f.write(data)
        except TypeError:
            with open(location, "wb") as f:
                return f.write(data)

    def old_files(self):
        for path, dirs, files in os.walk(self.dest):
            # Remove unused files
            for file in files:
                pwd = os.path.join(path, file)
                dist = pwd.replace(self.dest, self.src).replace(".html", ".pug")
                if not os.path.exists(dist):
                    os.remove(pwd)
                    self.print_debug(f"DELETE: {pwd}")

            # Remove empty folders
            for folder in dirs:
                folder_path = f"{path}/{folder}"
                if len(os.listdir(folder_path)) == 0:
                    os.rmdir(folder_path)
                    self.print_debug(f"DELETE: {folder_path}")

    def compile_pug(self, file: str, path: str = None, variables: dict = {}):
        if not path:
            path = os.path.dirname(file)
            file = os.path.basename(file)

        pwd = os.path.join(path, file)

        if re.compile(self.ignore).search(file):
            self.print_debug(f"SKIPPED: {pwd}")
            return

        dist = pwd.replace(self.src, self.dest)
        if re.compile(self.compile).search(file):
            data = self.render(path, file, variables)
            dist = dist.replace(".pug", ".html")
        else:
            data = self.read(pwd)

        if data:
            self.write(dist, data)
        else:
            print(f"ERROR {pwd}: Data content was empty, skipping")

    def compiler(self, everything: bool = True, watch_file: str = None, variables: dict = {}):
        if everything:
            for path, dirs, files in os.walk(self.src):
                for file in files:
                    self.compile_pug(file, path, variables)
        else:
            self.compile_pug(watch_file, variables=variables)

        self.old_files()
