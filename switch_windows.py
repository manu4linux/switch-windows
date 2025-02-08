import time
import random
import pygetwindow as gw
import subprocess
import argparse
import json
import psutil  # CPU usage
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from Quartz import CoreGraphics, EventType, Quartz

console = Console()

CONFIG_FILE = Path("config.json")
LOG_FILE = Path("switch_log.txt")

DEFAULT_CONFIG = {
    "ignored_keywords": ["Window Server", "StatusIndicator", "Menubar", "Dock", "Control Center"],
    "enable_logging": True
}

def load_config():
    """Load configuration from config.json."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red]Failed to load config.json: {e}[/red]")
    return DEFAULT_CONFIG  

CONFIG = load_config()

def get_cpu_usage(process_name):
    """Returns the CPU usage percentage of a given process."""
    for proc in psutil.process_iter(attrs=['name', 'cpu_percent']):
        try:
            if proc.info['name'] == process_name:
                return proc.info['cpu_percent']
        except psutil.NoSuchProcess:
            pass
    return 0.0

def list_active_windows():
    """Returns a dictionary of active application window titles with CPU usage."""
    titles = gw.getAllTitles()
    ignored_keywords = CONFIG.get("ignored_keywords", DEFAULT_CONFIG["ignored_keywords"])
    
    seen = set()
    valid_windows = {}

    for title in titles:
        title = title.strip()
        if title and title not in seen and not any(kw in title for kw in ignored_keywords):
            cpu_usage = get_cpu_usage(title)
            valid_windows[title] = cpu_usage
            seen.add(title)
    
    return valid_windows

def log_switch(title, skip_log):
    """Logs window switch attempts to a file, if logging is enabled."""
    if not skip_log and CONFIG.get("enable_logging", True):
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Switched to: {title}\n")

def get_cursor_position():
    """Returns the current cursor position as (x, y) tuple."""
    loc = CoreGraphics.CGEventGetLocation(CoreGraphics.CGEventCreate(None))
    return int(loc.x), int(loc.y)

def is_cursor_moving():
    """Detects if the cursor has moved in the last 2 seconds."""
    old_pos = get_cursor_position()
    time.sleep(0.1)
    
    for _ in range(20):  # Check for 2 seconds
        new_pos = get_cursor_position()
        if new_pos != old_pos:
            console.print("[yellow]Cursor is moving, skipping script execution.[/yellow]")
            return True
        time.sleep(0.1)
    
    console.print("[green]Cursor is idle, proceeding...[/green]")
    return False

last_keypress_time = time.time()

def keyboard_callback(proxy, event_type, event, refcon):
    """Callback function to detect keyboard activity."""
    global last_keypress_time
    if event_type in [CoreGraphics.kCGEventKeyDown, CoreGraphics.kCGEventFlagsChanged]:
        last_keypress_time = time.time()  # Update last keypress time
    return event

def monitor_keyboard():
    """Starts a keyboard event listener."""
    tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,
        Quartz.kCGHeadInsertEventTap,
        Quartz.kCGEventTapOptionListenOnly,
        (1 << CoreGraphics.kCGEventKeyDown) | (1 << CoreGraphics.kCGEventFlagsChanged),
        keyboard_callback,
        None
    )
    
    if not tap:
        console.print("[red]Failed to create keyboard event listener.[/red]")
        return
    
    run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
    Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), run_loop_source, Quartz.kCFRunLoopCommonModes)
    Quartz.CGEventTapEnable(tap, True)
    
    console.print("[blue]Keyboard monitoring started.[/blue]")
    Quartz.CFRunLoopRun()

def is_typing():
    """Checks if typing has occurred in the last 2 seconds."""
    return (time.time() - last_keypress_time) < 2

def activate_window(title, skip_log):
    """Attempts to activate a window using AppleScript with additional checks."""
    if is_cursor_moving():
        return
    
    if is_typing():
        console.print("[yellow]Typing detected, skipping script execution.[/yellow]")
        return

    script = f'''
    tell application "{title}"
        activate
    end tell
    tell application "System Events"
        tell process "{title}"
            set frontmost to true
            try
                perform action "AXRaise" of (windows whose value of attribute "AXMinimized" is true)
            end try
        end tell
        
        delay 0.01
        key code 48 using {{command down}}
    end tell
    '''

    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if "App Not Found" in result.stdout:
            console.print(f"[yellow]Skipping {title}: Application not running.[/yellow]")
            return False
        console.print(f"[green]Switched to: {title}[/green]")
        log_switch(title, skip_log)
        return True
    except subprocess.CalledProcessError:
        console.print(f"[red]Failed to switch to: {title}, trying fallback...[/red]")
        subprocess.run(["open", "-a", title])  
        return False

def switch_between_windows(delay_min, delay_max, cycle_apps, skip_log):
    """Continuously switches between valid application windows at a random interval."""
    last_window = None
    while True:
        window_data = list_active_windows()

        if cycle_apps:
            window_data = {title: cpu for title, cpu in window_data.items() if title in cycle_apps}

        if not window_data:
            console.print("[bold red]No valid active windows found.[/bold red]")
            time.sleep(10)
            continue

        table = Table(title="Active Windows", show_header=True, header_style="bold cyan")
        table.add_column("Index", justify="right")
        table.add_column("Window Title", style="bold magenta")
        table.add_column("CPU Usage (%)", style="bold yellow")

        for idx, (title, cpu_usage) in enumerate(window_data.items(), start=1):
            table.add_row(str(idx), title, f"{cpu_usage:.2f}%")

        console.print(table)

        for title in window_data.keys():
            if title == last_window:
                console.print(f"[yellow]Skipping {title} (already switched to last time).[/yellow]")
                continue
            
            activate_window(title, skip_log)
            last_window = title  

            delay = random.randint(delay_min, delay_max)
            console.print(f"[blue]Pausing for {delay} seconds before switch...[/blue]")
            time.sleep(delay)

        delay = random.randint(10, 60)
        console.print(f"[green]\nPausing for {delay} seconds before restarting...[/green]")
        time.sleep(delay)

if __name__ == "__main__":
    import threading
    threading.Thread(target=monitor_keyboard, daemon=True).start()

    parser = argparse.ArgumentParser(description="Cycle through active windows.")
    parser.add_argument("--min-delay", type=int, default=5, help="Minimum delay between switches (seconds)")
    parser.add_argument("--max-delay", type=int, default=10, help="Maximum delay between switches (seconds)")
    parser.add_argument("--apps", nargs="*", help="List of specific apps to cycle through (optional)")
    parser.add_argument("--skip-log", action="store_true", help="Disable logging for this session")

    args = parser.parse_args()

    console.print("[bold green]Starting window switcher...[/bold green]")
    switch_between_windows(args.min_delay, args.max_delay, args.apps, args.skip_log)
