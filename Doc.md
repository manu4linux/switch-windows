
---

# Detailed Documentation for Window Switcher

This document provides an in-depth explanation of how the Window Switcher works. It covers the project’s architecture, the functions used, and the flow of execution.

---

## Overview

The **Window Switcher** is designed to automate the process of switching between active application windows on macOS. It leverages several key libraries and system APIs:

- **AppleScript:** For activating and bringing windows to the foreground.
- **Quartz (via PyObjC):** For accessing low-level system events, such as mouse position and keyboard events.
- **pygetwindow:** For retrieving a list of active window titles.
- **psutil:** For monitoring CPU usage of processes.
- **rich:** For formatted terminal output (when not in background mode).

---

## Major Components

### 1. Configuration Management

- **Dynamic Configuration Reloading:**  
  The script reads from `config.json` on every cycle. This means that any changes made to the configuration file (such as updating ignored keywords, toggling logging, or enabling background mode) will take effect immediately without needing to restart the script.
  
- **Config Options:**
  - `ignored_keywords`: A list of strings that, if found in a window title, will exclude that window from the switcher.
  - `enable_logging`: A Boolean to enable or disable logging of window switches to a log file.
  - `background_mode`: When set to `true`, the script suppresses terminal output.

### 2. User Activity Monitoring

- **Mouse Movement Detection:**  
  The function `get_cursor_position()` uses Quartz’s `CGEventCreate` and `CGEventGetLocation` to capture the current mouse position. The helper function `is_cursor_moving()` samples the mouse position every 0.1 seconds over a 2-second period. If any movement is detected, the window switch is skipped.

- **Keyboard Activity Detection:**  
  A Quartz event tap is set up via the `monitor_keyboard()` function to monitor keyboard events. The callback function `keyboard_callback()` updates a global timestamp (`last_keypress_time`) whenever a key is pressed or modifier keys change. The helper function `is_typing()` checks if any key event has occurred in the last 2 seconds.

### 3. Window Listing and Activation

- **Listing Active Windows:**  
  Using `pygetwindow`, the function `list_active_windows()` collects all current window titles and filters out those containing any keywords specified in `ignored_keywords`.

- **Activating Windows:**  
  The function `activate_window()` constructs and executes an AppleScript to bring a target window to the foreground. Before doing so, it checks both mouse movement and keyboard activity to ensure that the user is idle. If AppleScript fails (for example, if the application isn’t running), the script falls back to using the macOS `open -a` command.

### 4. Logging

- **Terminal Logging:**  
  The helper function `log_print()` is used throughout the code for all terminal output. It checks the `BACKGROUND_MODE` flag (which is derived from `config.json`) to decide whether to print messages to the terminal.

- **File Logging:**  
  When enabled, every successful window switch is logged to `switch_log.txt` with a timestamp via the `log_switch()` function.

### 5. Main Loop and Execution Flow

- **Main Loop (`switch_between_windows`):**  
  This function contains the continuous loop that:
  - Reloads the configuration.
  - Retrieves the list of active windows.
  - Filters windows (if specific apps are specified via command-line arguments).
  - Cycles through the list, activating each window if the inactivity criteria are met.
  - Waits for a random delay between window switches (customizable via command-line parameters).

- **Keyboard Monitoring Thread:**  
  A separate daemon thread is launched at startup to continuously monitor keyboard events, ensuring that the latest keypress data is always available for inactivity checks.

- **Command-Line Arguments:**  
  The script accepts several arguments to customize its behavior:
  - `--min-delay` and `--max-delay`: Set the minimum and maximum delays (in seconds) between window switches.
  - `--apps`: Limit the window switcher to a specific list of applications.
  - `--skip-log`: Disable file logging for the current session.

---

## Detailed Code Walkthrough

1. **Configuration and Logging Functions:**
   - `load_config()`: Reads and returns configuration settings from `config.json`, falling back on defaults if necessary.
   - `log_print()`: Conditionally prints messages to the terminal based on the `BACKGROUND_MODE` setting.
   - `log_switch()`: Appends details of each window switch to `switch_log.txt` if logging is enabled.

2. **User Activity Functions:**
   - `get_cursor_position()`: Uses Quartz to retrieve the current mouse cursor position.
   - `is_cursor_moving()`: Checks if the mouse has moved over a 2-second period by sampling its position every 0.1 seconds.
   - `keyboard_callback()`: Updates `last_keypress_time` when a key event is detected.
   - `monitor_keyboard()`: Sets up and runs the Quartz event tap for keyboard monitoring.
   - `is_typing()`: Determines if there has been any keyboard activity in the last 2 seconds.

3. **Window Management Functions:**
   - `list_active_windows()`: Collects and filters active window titles using `pygetwindow`.
   - `activate_window()`: Activates a target window using an AppleScript command, but only if the inactivity checks (mouse and keyboard) pass.
   - `switch_between_windows()`: The main loop that cycles through windows. It reloads the configuration at the start of each cycle and then performs window switching based on the current settings and activity status.

4. **Program Execution:**
   - The script starts by launching the keyboard monitoring thread.
   - Command-line arguments are parsed to customize the behavior.
   - The main loop (`switch_between_windows`) runs continuously, dynamically reloading configuration settings and processing active windows.

---

## Conclusion

The **Window Switcher** provides an automated, configurable way to manage window focus on macOS based on user inactivity. Its dynamic configuration reloading and robust activity checks make it a versatile tool for enhancing productivity and automating window management tasks.

For any questions or contributions, please refer to the project’s repository or contact the maintainer.
