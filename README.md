# Window Switcher

**Window Switcher** is a Python-based automation tool for macOS that cycles through active application windows based on user inactivity. It intelligently checks both mouse movement and keyboard activity to ensure that window switching occurs only when the user is idle—making it a helpful utility for multitaskers or automation enthusiasts.

Additionally, the tool retrieves and displays the CPU usage percentage for each active window's associated process (using psutil), providing real-time insights into resource consumption.

## Key Features

- **Dynamic Window Switching:**  
  Automatically cycles through active windows, bringing each window to the foreground using AppleScript.

- **User Inactivity Detection:**  
  Uses Quartz to monitor mouse position and keyboard events. The script switches windows only if no mouse movement or typing has been detected for 2 seconds.

- **Dynamic Configuration:**  
  Reads settings from a `config.json` file on every cycle. This means you can update options (such as ignored window keywords, logging preferences, and background mode) on the fly without restarting the script.

- **Customizable Behavior:**  
  - **Ignored Keywords:** Exclude windows (like "Dock" or "Menubar") by specifying keywords.
  - **Logging Options:** Enable or disable file logging.
  - **Background Mode:** Suppress terminal output by setting `background_mode` to `true` in `config.json`.

- **Rich Terminal Output:**  
  Uses the [rich](https://pypi.org/project/rich/) library to display active windows and statuses in a visually appealing table (unless running in background mode).

- **Fallback Mechanism:**  
  If AppleScript fails to activate a window, the script uses the macOS `open` command as a fallback.

- **Command-Line Options:**  
  Customize delay intervals between switches, limit the switcher to specific applications, and disable logging via command-line arguments.

## Requirements

- macOS
- Python 3.x
- [pygetwindow](https://pypi.org/project/PyGetWindow/)
- [psutil](https://pypi.org/project/psutil/)
- [pyobjc-framework-Quartz](https://pypi.org/project/pyobjc-framework-Quartz/)
- [rich](https://pypi.org/project/rich/)

## Installation

1. **Clone the repository** (or download the source code).

2. **Set up a virtual environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate      # On macOS/Linux
   venv\Scripts\activate         # On Windows
   ```

3. **Install the required packages:**

```bash
pip install -r requirements.txt
```
Tip: You can generate a requirements.txt using pip freeze > requirements.txt if it’s not provided.

##  Configuration
Customize your settings by editing the config.json file. For example:

```json
{
  "ignored_keywords": ["Window Server", "StatusIndicator", "Menubar", "Dock", "Control Center"],
  "enable_logging": true,
  "background_mode": false
}
```

## Usage
Run the script with optional command-line arguments:

```bash
python switch_windows.py --min-delay 5 --max-delay 10 --apps Safari Terminal --skip-log
```
If you set "background_mode": true in your config.json, the script will run without printing to the terminal while still logging events to the log file (if logging is enabled).

## Benefits
- Increased Productivity: Automatically cycle through your work windows when you’re not actively using the mouse or keyboard.
- Dynamic Adjustments: Change configuration settings on the fly without restarting the script.
- Enhanced Focus: The inactivity checks help prevent accidental window switches when you’re actively working.

## License
This project is licensed under the MIT License.

## Contributing
Contributions are welcome! Please feel free to open issues or submit pull requests to improve the functionality or add new features.