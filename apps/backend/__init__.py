"""Backend application package initialization."""

# Ensure internal packages are available on the import path.
from pathlib import Path
import sys

package_dir = Path(__file__).resolve().parents[2] / "packages"
if str(package_dir) not in sys.path:
    sys.path.append(str(package_dir))

