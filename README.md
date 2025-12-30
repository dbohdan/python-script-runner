# python-script-runner

**python-script-runner** is a POSIX shell script that provides a unified [shebang line](https://en.wikipedia.org/wiki/Shebang_(Unix)) for Python scripts with [inline script metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/) (PEP 723).
The shell script automatically invokes the first Python script runner it finds in [`PATH`](https://en.wikipedia.org/wiki/PATH_(variable)).

## Example

```python
#! /usr/bin/env python-script-runner
# /// script
# dependencies = [
#   "httpx",
#   "rich",
# ]
# ///

import httpx
from rich import print

ip = httpx.get("https://icanhazip.com").text.strip()
print(f"Your public IP address is [bold]{ip}[/bold]")
```

## Motivation

Scripts with inline script metadata can be run using a variety of tools, like uv, pipx, hatch, or pip-run.
However, each tool requires a different shebang line:

```python
#! /usr/bin/env -S uv run --script --
```

or

```python
#! /usr/bin/env -S pipx run --path --
```

This creates a portability problem.
A script written for uv won't run on a system with only pipx and vice versa.
Asking the user to edit the script is not user-friendly.

The idea behind python-script-runner is to provide a single executable name to use.
It tries a hardcoded list of popular PEP 723-compatible runners (ordered by GitHub stars as a proxy for popularity) and executes your script with the first runner it finds.

The order is:

1. [uv](https://github.com/astral-sh/uv)
2. [pipx](https://github.com/pypa/pipx)
3. [Hatch](https://github.com/pypa/hatch)
4. [pip-run](https://github.com/jaraco/pip-run)

If no known runner is found, python-script-runner exits with status 127.

## Requirements

- POSIX shell
- At least one supported runner
- Python &ge; 3.10 for testing

## Installation

Copy the script to a directory in your `PATH`, like `~/.local/bin/` or `/usr/local/bin/`.

```sh
curl -o ~/.local/bin/python-script-runner https://raw.githubusercontent.com/dbohdan/python-script-runner/master/python-script-runner
chmod +x ~/.local/bin/python-script-runner
```

## Limitations

python-script-runner deliberately avoids configuration.
It only tries known runners in a fixed order.
Edit the script if you want to add runners or change the order.

## License

[MIT License](LICENSE).
