import os
import re
import sass

from jinja2 import Environment, FileSystemLoader


class Pug:
    def __init__(self, src: str, dest: str, debug: bool = False):
        self.src = src
        self.dest = dest
        self.debug = debug

        self.ignore = r"_.*\.(pug|scss)"
        self.re_compile_pug = r".*\.pug"
        self.re_compile_scss = r".*\.scss"

        self.env = Environment(
            loader=FileSystemLoader(self.src),
            extensions=["pypugjs.ext.jinja.PyPugJSExtension"]
        )

    def print_debug(self, text):
        if self.debug:
            print(text)

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
                dist = pwd.replace(self.dest, self.src).replace(".html", ".pug").replace(".css", ".scss")
                if not os.path.exists(dist):
                    os.remove(pwd)
                    self.print_debug(f"DELETE: {pwd}")

            # Remove empty folders
            for folder in dirs:
                folder_path = f"{path}/{folder}"
                if len(os.listdir(folder_path)) == 0:
                    os.rmdir(folder_path)
                    self.print_debug(f"DELETE: {folder_path}")

    def render_pug(self, path: str, filename: str, variables: dict = {}):
        pretty_location = path.replace(os.sep, "/")
        pug_file_location = pretty_location.replace(self.src, "./")
        self.print_debug(f"RENDER: {pretty_location} -> {filename}")

        try:
            return self.env.get_template(f"{pug_file_location}/{filename}").render(variables)
        except Exception as e:
            print(f"ERROR {pretty_location} -> {filename}: {e}")

    def compile_dynamic(self, file: str, path: str = None, engine: str = "pug", variables: dict = {}, scss_compressed: bool = False):
        if not path:
            path = os.path.dirname(file)
            file = os.path.basename(file)

        pwd = os.path.join(path, file)
        dist = pwd.replace(self.src, self.dest)

        if re.compile(self.ignore).search(file):
            self.print_debug(f"SKIPPED: {pwd}")
            return

        self.print_debug(f"RENDER: {path} -> {file}")
        if engine == "pug":
            dist, data = self.compile_pug(dist, file, path, variables=variables)
        elif engine == "scss":
            dist, data = self.compile_scss(dist, file, path, scss_compressed=scss_compressed)
        else:
            data = self.read(pwd)

        if data:
            self.write(dist, data)
        else:
            print(f"ERROR {pwd}: Data content was empty, skipping")

    def compile_pug(self, dist: str, file: str, path: str = None, variables: dict = {}):
        if re.compile(self.re_compile_pug).search(file):

            pretty_location = path.replace(os.sep, "/")
            pug_file_location = pretty_location.replace(self.src, "./")

            try:
                data = self.env.get_template(f"{pug_file_location}/{file}").render(variables)
            except Exception as e:
                print(f"ERROR {pretty_location} -> {file}: {e}")
                return None, None

            dist = dist.replace(".pug", ".html")
            return dist, data
        return None, None

    def compile_scss(self, dist: str, file: str, path: str = None, scss_compressed: bool = False):
        if re.compile(self.re_compile_scss).search(file):
            with open(f"{path}/{file}", "r", encoding="utf8") as f:
                try:
                    data = sass.compile(
                        string=f.read(),
                        output_style="compressed" if scss_compressed else "nested",
                        include_paths=[path]
                    )
                except Exception as e:
                    print(f"ERROR {path} -> {file}: {e}")
                    return None, None

            dist = dist.replace(".scss", ".css")
            return dist, data
        return None, None

    def compiler(self, everything: bool = True, watch_file: str = None, variables: dict = {}, scss_compressed: bool = False):
        if everything:
            for path, dirs, files in os.walk(self.src):
                for file in files:
                    ext = file.split(".")[-1]
                    self.compile_dynamic(
                        file, path, engine=ext,
                        variables=variables, scss_compressed=scss_compressed
                    )
        else:
            ext = watch_file.split(".")[-1]
            self.compile_dynamic(
                watch_file, engine=ext,
                variables=variables, scss_compressed=scss_compressed
            )

        self.old_files()
