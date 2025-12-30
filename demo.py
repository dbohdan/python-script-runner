#! /usr/bin/env python-script-runner
# /// script
# dependencies = [
#   "httpx",
#   "rich<10",
# ]
# ///

import httpx
from rich import print

ip = httpx.get("https://icanhazip.com").text.strip()
print(f"Your public IP address is [bold]{ip}[/bold]")
