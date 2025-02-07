#!/usr/bin/env python3
import pygetwindow as gw

def list_active_windows():
    # Retrieve a list of window titles.
    titles = gw.getAllTitles()
    
    if not titles:
        print("No active windows detected.")
        return
    
    print("Current active windows:")
    for title in titles:
        print(f"- {title}")

if __name__ == "__main__":
    list_active_windows()
