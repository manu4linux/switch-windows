import time
import random
import pygetwindow as gw
import subprocess

def list_active_windows():
    """Returns a list of active application window titles (excluding system-level ones)."""
    titles = gw.getAllTitles()
    ignored_keywords = ["Window Server", "StatusIndicator", "Menubar", "Dock", "Control Center"]
    
    # Filter out invalid/system window titles
    valid_titles = [title.strip() for title in titles if title.strip() and not any(kw in title for kw in ignored_keywords)]
    
    return valid_titles

def activate_window(title):
    """Uses AppleScript to activate a window on macOS."""
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
            print(f"Skipping {title}: Application not running.")
        else:
            print(f"Switched to: {title}")
    except subprocess.CalledProcessError:
        print(f"Failed to switch to: {title}")

def switch_between_windows():
    """Continuously switches between valid application windows every 5s + random 0-120s."""
    while True:
        window_titles = list_active_windows()

        if not window_titles:
            print("No valid active windows found.")
            time.sleep(10)
            continue

        print("\nActive windows:")
        for title in window_titles:
            print(f"- {title}")

        for title in window_titles:
            activate_window(title)
            time.sleep(5)  # Switch every 5s

        delay = random.randint(0, 120)
        print(f"\nPausing for {delay} seconds before restarting...")
        time.sleep(delay)

if __name__ == "__main__":
    print("Starting window switcher...")
    switch_between_windows()
