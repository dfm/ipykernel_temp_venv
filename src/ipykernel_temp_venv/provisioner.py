import os
import re
import venv
from tempfile import TemporaryDirectory
from typing import Any, Optional

from jupyter_client import LocalProvisioner
from traitlets.log import get_logger

REPL_PATTERN = re.compile(r"{(\s*)executable(\s*)}")
HERUSTIC_PATTERN = re.compile(r"python([0123456789\.]*)")


def expand_executable(executable: str, arg: str) -> str:
    # Replace '{executable}' with the expanded executable path
    if REPL_PATTERN.match(arg) is not None:
        return REPL_PATTERN.sub(executable, arg)

    # Use a heuristic to determine if the argument points to a Python executable
    if HERUSTIC_PATTERN.match(os.path.basename(arg)) is not None:
        get_logger().info(
            f"Heuristically identified argument '{arg}' as a Python executable; "
            f"it will be replaced with with '{executable}'"
        )
        return executable

    return arg


class TempVenvProvisioner(LocalProvisioner):
    temp_dir: Optional[TemporaryDirectory] = None

    async def pre_launch(self, **kwargs: Any) -> dict[str, Any]:
        if self.temp_dir is None:
            self.temp_dir = TemporaryDirectory()
            venv.create(self.temp_dir.name, system_site_packages=True)

        results = await super().pre_launch(**kwargs)

        # Update the command to use the virtual environment's python
        executable = os.path.join(self.temp_dir.name, "bin", "python")
        results["cmd"] = [expand_executable(executable, arg) for arg in results["cmd"]]

        return results

    async def cleanup(self, restart: bool = False) -> None:
        if not restart and self.temp_dir is not None:
            self.temp_dir.cleanup()
            self.temp_dir = None
        return await super().cleanup(restart=restart)
