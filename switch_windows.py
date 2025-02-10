import time
import random
import pygetwindow as gw
import subprocess
import argparse
import json
import psutil  # For CPU usage
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Import Quartz modules from PyObjC
import Quartz
from Quartz import CoreGraphics

# Initialize Rich console
console = Console()

# Global flag to control terminal logging; will be set from config.json
BACKGROUND_MODE = False

# Configuration and log file paths
CONFIG_FILE = Path("config.json")
DEFAULT_LOG_FILE = "~/switch_log.txt"

# Default configuration (includes the background_mode option)
DEFAULT_CONFIG = {
    "ignored_keywords": ["Window Server", "StatusIndicator", "Menubar", "Dock", "Control Center"],
    "enable_logging": True,
    "background_mode": False
}

def log_print(*args, **kwargs):
    """
    Print to terminal only if not in background mode.
    """
    if not BACKGROUND_MODE:
        console.print(*args, **kwargs)

def load_config():
    """Load configuration from config.json or return default configuration."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            log_print(f"[red]Failed to load config.json: {e}[/red]")
    return DEFAULT_CONFIG

# Initially load config once.
CONFIG = load_config()
BACKGROUND_MODE = CONFIG.get("background_mode", DEFAULT_CONFIG["background_mode"])
LOG_FILE = Path(CONFIG.get("logfilepath", str(DEFAULT_LOG_FILE))).expanduser()

def get_cpu_usage(process_name):
    """Return the CPU usage percentage for a given process."""
    for proc in psutil.process_iter(attrs=['name', 'cpu_percent']):
        try:
            if proc.info['name'] == process_name:
                return proc.info['cpu_percent']
        except psutil.NoSuchProcess:
            pass
    return 0.0

def list_active_windows():
    """Return a dictionary of active window titles with their CPU usage."""
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
    """Log the window switch attempt to a file, if logging is enabled."""
    if not skip_log and CONFIG.get("enable_logging", True):
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Switched to: {title}\n")

def get_cursor_position():
    """Return the current mouse cursor position as an (x, y) tuple."""
    loc = CoreGraphics.CGEventGetLocation(CoreGraphics.CGEventCreate(None))
    return int(loc.x), int(loc.y)

def is_cursor_moving():
    """
    Check if the cursor has moved during a 10-second period.
    Samples the cursor position every 0.1 seconds.
    """
    initial_pos = get_cursor_position()
    for _ in range(random.randint(10, 30)*10):  # 20 iterations * 0.1 sec = 2 seconds
        time.sleep(0.1)
        new_pos = get_cursor_position()
        if new_pos != initial_pos:
            log_print("[blue]Cursor is moving, skipping app.[/blue]")
            return True
    log_print("[green]Cursor is idle, proceeding...[/green]")
    return False

# Global variable to track the last keypress time
last_keypress_time = time.time()

def keyboard_callback(proxy, event_type, event, refcon):
    """Callback function invoked on key events to update last keypress time."""
    global last_keypress_time
    if event_type in [CoreGraphics.kCGEventKeyDown, CoreGraphics.kCGEventFlagsChanged]:
        last_keypress_time = time.time()
    return event

def monitor_keyboard():
    """
    Set up a keyboard event listener to track typing.
    This function runs in its own run loop.
    """
    event_mask = (1 << CoreGraphics.kCGEventKeyDown) | (1 << CoreGraphics.kCGEventFlagsChanged)
    tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,
        Quartz.kCGHeadInsertEventTap,
        Quartz.kCGEventTapOptionListenOnly,
        event_mask,
        keyboard_callback,
        None
    )
    
    if not tap:
        log_print("[red]Failed to create keyboard event listener.[/red]")
        return

    run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
    Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), run_loop_source, Quartz.kCFRunLoopCommonModes)
    Quartz.CGEventTapEnable(tap, True)
    log_print("[blue]Keyboard monitoring started.[/blue]")
    Quartz.CFRunLoopRun()

def is_typing():
    """Return True if a key event occurred in the last 10 seconds."""
    return (time.time() - last_keypress_time) < random.randint(10, 30)

def activate_window(title, skip_log):
    """
    Activate a window using AppleScript.
    Only performs the activation if both the mouse cursor is idle
    and no typing has occurred in the last 2 seconds.
    """
    if is_cursor_moving():
        return
    if is_typing():
        log_print("[blue]Typing detected, skipping script execution.[/blue]")
        return
    
    
    # AppleScript to activate a window and raise it if minimized
    # and then simulate Command-Tab to switch applications backgroud.
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
            log_print(f"[blue]Skipping {title}: Application not running.[/blue]")
            return False
        log_print(f"[green]Switched to: {title}[/green]")
        log_switch(title, skip_log)
        return True
    except subprocess.CalledProcessError:
        log_print(f"[red]Failed to switch to: {title}, trying fallback...[/red]")
        subprocess.run(["open", "-a", title])
        return False

def switch_between_windows(delay_min, delay_max, cycle_apps, skip_log):
    """
    Continuously switch between active windows at random intervals.
    If specific apps are provided (cycle_apps), only those are considered.
    Before each cycle, the config file is re-read.
    """
    last_window = None
    while True:
        # Reload configuration each cycle
        global CONFIG, BACKGROUND_MODE
        CONFIG = load_config()
        BACKGROUND_MODE = CONFIG.get("background_mode", DEFAULT_CONFIG["background_mode"])

        window_data = list_active_windows()

        if cycle_apps:
            # Filter to only the specified apps.
            window_data = {title: cpu for title, cpu in window_data.items() if title in cycle_apps}

        if not window_data:
            log_print("[bold red]No valid active windows found.[/bold red]")
            time.sleep(10)
            continue

        # Display active windows in a table (only if not in background mode)
        table = Table(title="Active Windows", show_header=True, header_style="bold cyan")
        table.add_column("Index", justify="right")
        table.add_column("Window Title", style="bold magenta")
        table.add_column("CPU Usage (%)", style="bold yellow")
        for idx, (title, cpu_usage) in enumerate(window_data.items(), start=1):
            table.add_row(str(idx), title, f"{cpu_usage:.2f}%")
        log_print(table)

        for title in window_data.keys():
            if title == last_window:
                log_print(f"[yellow]Skipping {title} (already switched to last time).[/yellow]")
                continue
            
            activate_window(title, skip_log)
            last_window = title

            delay = random.randint(delay_min, delay_max)
            log_print(f"[yellow]Pausing before next switch...[/yellow]")
            time.sleep(delay)

        delay = random.randint(10, 60)
        log_print(f"[green]\nPausing for {delay} seconds before restarting cycle...[/green]")
        time.sleep(delay)

if __name__ == "__main__":
    # Start keyboard monitoring in a separate daemon thread
    import threading
    threading.Thread(target=monitor_keyboard, daemon=True).start()

    parser = argparse.ArgumentParser(description="Cycle through active windows.")
    parser.add_argument("--min-delay", type=int, default=0, help="Minimum delay between switches (seconds)")
    parser.add_argument("--max-delay", type=int, default=3, help="Maximum delay between switches (seconds)")
    parser.add_argument("--apps", nargs="*", help="List of specific apps to cycle through (optional)")
    parser.add_argument("--skip-log", action="store_true", help="Disable logging for this session")
    args = parser.parse_args()

    log_print(f"[green]Log file path:[/green] {LOG_FILE}")
    switch_between_windows(args.min_delay, args.max_delay, args.apps, args.skip_log)
