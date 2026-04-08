#! /usr/bin/env python-script-runner
# /// script
# dependencies = [
#   "requests",
#   "rich<10",
# ]
# ///

import requests
from rich import print

ip = requests.get("https://icanhazip.com").text.strip()
print(f"Your public IP address is [bold]{ip}[/bold]")
