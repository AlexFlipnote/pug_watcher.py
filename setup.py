import re

from setuptools import setup


version = ""
with open("pug_watcher/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name="pug-watcher",
    author="AlexFlipnote",
    url="https://github.com/AlexFlipnote/pug_watcher.py",
    version=version,
    packages=["pug_watcher"],
    description="Simple command-line Pug watcher/compiler made in Python",
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pug_watcher=pug_watcher.main:main"
        ]
    }
)
