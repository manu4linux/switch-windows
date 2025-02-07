import time
import random
import pygetwindow as gw
import subprocess
import argparse
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

CONFIG_FILE = Path("config.json")
LOG_FILE = Path("switch_log.txt")

# Default ignored window names (modifiable via config)
DEFAULT_IGNORED_KEYWORDS = ["Window Server", "StatusIndicator", "Menubar", "Dock", "Control Center"]

def load_config():
    """Loads ignored keywords from config.json or uses defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            return config.get("ignored_keywords", DEFAULT_IGNORED_KEYWORDS)
        except Exception as e:
            console.print(f"[red]Failed to load config.json: {e}[/red]")
    return DEFAULT_IGNORED_KEYWORDS

def list_active_windows():
    """Returns a list of unique active application window titles (excluding system-level ones)."""
    titles = gw.getAllTitles()
    ignored_keywords = load_config()
    
    # Remove duplicates and filter invalid/system window titles
    unique_titles = list(set(title.strip() for title in titles if title.strip() and not any(kw in title for kw in ignored_keywords)))
    
    return unique_titles

def log_switch(title):
    """Logs window switch attempts to a file."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Switched to: {title}\n")

def activate_window(title):
    """Attempts to activate a window using AppleScript with fallback."""
    script = f'''
    tell application "System Events"
        set appList to name of every process
        if "{title}" is in appList then
            tell application "{title}" to activate
        else
            return "App Not Found"
        end if
    end tell
    '''
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if "App Not Found" in result.stdout:
            console.print(f"[yellow]Skipping {title}: Application not running.[/yellow]")
            return False
        console.print(f"[green]Switched to: {title}[/green]")
        log_switch(title)
        return True
    except subprocess.CalledProcessError:
        console.print(f"[red]Failed to switch to: {title}, trying fallback...[/red]")
        subprocess.run(["open", "-a", title])  # Fallback method
        return False

def switch_between_windows(delay_min, delay_max, cycle_apps):
    """Continuously switches between unique valid application windows at a random interval."""
    while True:
        window_titles = list_active_windows()

        if cycle_apps:
            # If specific apps are provided, filter only those
            window_titles = [title for title in window_titles if title in cycle_apps]

        if not window_titles:
            console.print("[bold red]No valid active windows found.[/bold red]")
            time.sleep(10)
            continue

        # Display active windows in a table
        table = Table(title="Active Windows (Unique)", show_header=True, header_style="bold cyan")
        table.add_column("Index", justify="right")
        table.add_column("Window Title", style="bold magenta")
        for idx, title in enumerate(window_titles, start=1):
            table.add_row(str(idx), title)
        console.print(table)

        for title in window_titles:
            activate_window(title)
            delay = random.randint(delay_min, delay_max)
            console.print(f"[blue]Pausing for {delay} seconds before switch...[/blue]")
            time.sleep(delay)

        delay = random.randint(30, 120)
        console.print(f"[green]\nPausing for {delay} seconds before restarting...[/green]")
        time.sleep(delay)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cycle through active windows.")
    parser.add_argument("--min-delay", type=int, default=5, help="Minimum delay between switches (seconds)")
    parser.add_argument("--max-delay", type=int, default=20, help="Maximum delay between switches (seconds)")
    parser.add_argument("--apps", nargs="*", help="List of specific apps to cycle through (optional)")

    args = parser.parse_args()

    console.print("[bold green]Starting window switcher...[/bold green]")
    switch_between_windows(args.min_delay, args.max_delay, args.apps)
