# pug_watcher.py
A simple command-line watcher/compiler that transforms Pug to HTML files (and syncs folders!) This package also supports compling SCSS for easier building of websites 🎉

# Requirements
- Python 3.6 or above

# Install
You can install it by simply doing `pip install pug-watcher`

## Arguments
By simply writing `pug_watcher` in the console, you will be shown all available commands that it has to offer.

## --config argument
There is a config file you can use to avoid having to use every single argument available in command arguments. Simply create a file called `.pug_watcher.json`. The file accepts the following arguments:
```py
watch:           bool  # If it should watch the paths in question for changes (Default: false)
path:            str   # The paths to watch/compile like 'source/dir:dest/dir' (Default: src:dist)
debug:           bool  # If the compiler should show what it does (Default: false)
variables:       dict  # A list of variables to be used in Pug (Default: {})
scss_compressed: bool  # If the SCSS compiled should be compressed or not (Default: false)
```
#### Variables example
```json
{
  "variables": {
    "name": "AlexFlipnote",
    "stuff": "coding, yes yes"
  }
}
```
