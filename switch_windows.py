#!/usr/bin/env python3
from AppKit import NSWorkspace
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGWindowListExcludeDesktopElements

def list_active_windows():
    window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements, 0)
    titles = [win['kCGWindowName'] for win in window_list if 'kCGWindowName' in win and win['kCGWindowName']]
    
    if not titles:
        print("No active windows detected.")
        return
    
    print("Current active windows:")
    for title in titles:
        print(f"- {title}")

def activate_window(app_name):
    workspace = NSWorkspace.sharedWorkspace()
    apps = workspace.runningApplications()
    
    for app in apps:
        if app.localizedName() == app_name:
            app.activateWithOptions_(NSWorkspace.ActivationPolicyRegular)
            print(f"Switched to: {app_name}")
            return
    
    print(f"No application found with name: {app_name}")

if __name__ == "__main__":
    print("Active windows before switching:")
    list_active_windows()
    
    target_app = "Slack"  # Change this to the desired window title
    activate_window(target_app)
