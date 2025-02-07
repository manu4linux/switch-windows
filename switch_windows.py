import time
import random
import pygetwindow as gw

def list_active_windows():
    """Returns a list of active window titles."""
    titles = gw.getAllTitles()
    return [title for title in titles if title.strip()]  # Remove empty titles

def switch_between_windows():
    """Continuously switches between active windows every 5s + random 0-120s."""
    while True:
        window_titles = list_active_windows()

        if not window_titles:
            print("No active windows found.")
            time.sleep(10)
            continue

        print("\nActive windows:")
        for title in window_titles:
            print(f"- {title}")

        for title in window_titles:
            window = gw.getWindowGeometry(title)
            if window:
                print(f"\nSwitching to: {title}")
                gw.activate(title)
                time.sleep(5)  # Switch every 5s

        delay = random.randint(0, 120)
        print(f"\nPausing for {delay} seconds before restarting...")
        time.sleep(delay)

if __name__ == "__main__":
    print("Starting window switcher...")
    switch_between_windows()
