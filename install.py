"""Install this plugin's optional voice dependencies into its private lib folder.

Run from this plugin folder with the same Python version as the host app's engine (Bifrost Scribe: 3.12),
because lib/ holds compiled modules for that version. Bifrost Scribe ships the plugin with lib/ built this way,
so Scribe users need neither Python nor pip.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).parent
subprocess.check_call(
    [sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(ROOT / "lib"), "-r", str(ROOT / "requirements.txt")]
)
