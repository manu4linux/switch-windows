import time
import pygetwindow as gw

def get_window_by_title(partial_title):
    """
    Returns the first window whose title contains the given partial title.
    """
    windows = gw.getWindowsWithTitle(partial_title)
    if not windows:
        raise Exception(f"No window found with title containing: '{partial_title}'")
    return windows[0]

def switch_between_windows(title1, title2, delay=5):
    """
    Alternates focus between two windows identified by their partial titles.
    
    :param title1: Partial title of the first window.
    :param title2: Partial title of the second window.
    :param delay: Delay in seconds between switching.
    """
    try:
        win1 = get_window_by_title(title1)
        win2 = get_window_by_title(title2)
    except Exception as e:
        print(e)
        return

    print(f"Found windows:\n  Window 1: {win1.title}\n  Window 2: {win2.title}")
    
    # Bring both windows to the front once at start (optional)
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
    # Replace 'Notepad' and 'Calculator' with part of the window titles you want to switch between.
    # For example, on Windows you might use "Notepad" and "Calculator".
    switch_between_windows("Notepad", "Calculator", delay=5)
