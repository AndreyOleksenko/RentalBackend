#!/usr/bin/env python
import sys
import os

print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Python path:", sys.path)
print("Current directory:", os.getcwd())
print("Directory contents:", os.listdir("."))

try:
    import RentalService
    print("RentalService module found at:", RentalService.__file__)
except ImportError as e:
    print("Error importing RentalService:", e)

try:
    from RentalService import settings
    print("RentalService.settings module found at:", settings.__file__)
except ImportError as e:
    print("Error importing RentalService.settings:", e)

print("\nChecking directory structure:")
for root, dirs, files in os.walk(".", topdown=True, maxdepth=2):
    print(f"Directory: {root}")
    for d in dirs:
        print(f"  Subdirectory: {d}")
    for f in files:
        if f.endswith(".py"):
            print(f"  Python file: {f}") 