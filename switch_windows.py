#!/usr/bin/env python3

from ssl import ALERT_DESCRIPTION_UNSUPPORTED_EXTENSION
import time
import random
from AppKit import NSWorkspace
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGWindowListExcludeDesktopElements

def list_active_windows():
    """Returns a list of active window titles."""
    window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements, 0)
    titles = [win['kCGWindowName'] for win in window_list if 'kCGWindowName' in win and win['kCGWindowName']]
    
    return titles

def activate_window(app_name):
    """Activates a window based on its application name."""
    workspace = NSWorkspace.sharedWorkspace()
    apps = workspace.runningApplications()
    
    for app in apps:
        if app.localizedName() == app_name:
            app.activateWithOptions_(NSWorkspace.ActivationPolicyRegular)
            print(f"Switched to: {app_name}")
            return True

    print(f"Application not found: {app_name}")
    return False

def switch_between_windows():
    """Continuously switches between all active windows every 5 seconds with a random delay of up to 120 seconds."""
    while True:
        window_titles = list_active_windows()
        # Add custom windows to the list
        # window_titles.append("Notes")  #append
        # window_titles.append("Ghostty")  #append
        
        # # Remove duplicates
        # window_titles = list(set(window_titles))

         # Filter out empty titles
        
        if not window_titles:
            print("No active windows detected.")
            time.sleep(10)
            continue

        print("\nActive windows:")
        for title in window_titles:
            print(f"- {title}")

        for window in window_titles:
            print(f"\nSwitching to: {window}")
            activate_window(window)
            time.sleep(5)  # Switch every 5 seconds

        # Introduce a random delay between 0 and 120 seconds
        delay = random.randint(0, 120)
        print(f"\nPausing for {delay} seconds before restarting...")
        time.sleep(delay)

if __name__ == "__main__":
    print("Starting window switcher...")
    switch_between_windows()
