"""Install this plugin's optional voice dependencies into its private lib folder.

Run with Python 3.11+ from this plugin folder before copying it into AutoScript's
plugins folder. Release ZIPs will bundle lib/ so ordinary AutoScript.exe users do
not need Python or pip.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).parent
subprocess.check_call(
    [sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(ROOT / "lib"), "-r", str(ROOT / "requirements.txt")]
)
