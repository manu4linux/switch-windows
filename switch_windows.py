import time
from traceback import print_last
import Quartz
import pygetwindow as gw
from pygetwindow import MacOSWindow

def get_all_windows():
    """
    Uses Quartz to get information on all on-screen windows and returns
    a list of MacOSWindow objects.
    """
    # Options to list only on-screen windows and exclude desktop elements
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
    windows = []
    for win_dict in window_list:
        try:
            # Construct a MacOSWindow from the dictionary returned by Quartz.
            win = MacOSWindow(win_dict)
            windows.append(win)
        except Exception as e:
            # Skip windows that cannot be parsed into a MacOSWindow object.
            # You might want to log e for debugging.
            pass
    return windows

def getWindowsWithTitle(partial_title):
    """
    Returns a list of window objects whose title contains the given partial_title (case-insensitive).
    """
    all_windows = get_all_windows()
    print(f"Found {len(all_windows)} windows.")
    print("Window titles:")
    for win in all_windows:
        print(f"  {win.title}")
        
        
    return [win for win in all_windows if partial_title.lower() in win.title.lower()]

def switch_between_windows(title1, title2, delay=5):
    """
    Alternates focus between two windows identified by partial titles.
    """
    # Retrieve the windows using our custom helper
    windows1 = getWindowsWithTitle(title1)
    windows2 = getWindowsWithTitle(title2)
    
    if not windows1:
        print(f"No window found with title containing: '{title1}'")
        return
    if not windows2:
        print(f"No window found with title containing: '{title2}'")
        return

    # Use the first matching window for each title
    win1 = windows1[0]
    win2 = windows2[0]
    
    print(f"Found windows:\n  Window 1: {win1.title}\n  Window 2: {win2.title}")
    
    # Optionally, bring both windows to the front once at start
    win1.activate()
    time.sleep(1)
    win2.activate()
    time.sleep(1)
    
    # Toggle focus indefinitely
    while True:
        if win1.isActive:
            print(f"Switching focus from '{win1.title}' to '{win2.title}'")
            win2.activate()
        else:
            print(f"Switching focus from '{win2.title}' to '{win1.title}'")
            win1.activate()
        time.sleep(delay)

if __name__ == '__main__':
    # Replace "Safari" and "Terminal" with part of the window titles you want to switch between.
    # On macOS, these are common examples. Adjust as needed.
    # switch_between_windows("Safari", "Terminal", delay=5)
    switch_between_windows("Slack", "Ghostty", delay=5)
