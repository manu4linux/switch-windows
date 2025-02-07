import pygetwindow as gw

print("pygetwindow version:", getattr(gw, '__version__', 'unknown'))
print("Available attributes in pygetwindow:")
print(dir(gw))

# Attempt to call the function
try:
    windows = gw.getWindowsWithTitle("Notepad")
    print("Found windows:", windows)
except AttributeError:
    print("The function getWindowsWithTitle is not available.")
