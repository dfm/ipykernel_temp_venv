import venv
from tempfile import TemporaryDirectory
from typing import Any, Optional

from jupyter_client import KernelConnectionInfo, LocalProvisioner


class TempEnvProvisioner(LocalProvisioner):
    temp_dir: Optional[TemporaryDirectory] = None

    async def pre_launch(self, **kwargs: Any) -> dict[str, Any]:
        if self.temp_dir is None:
            self.temp_dir = TemporaryDirectory()
            venv.create(self.temp_dir.name, system_site_packages=True)
            print(self.temp_dir)

        return await super().pre_launch(**kwargs)

    async def launch_kernel(self, cmd: list[str], **kwargs: Any) -> KernelConnectionInfo:
        print(cmd)
        cmd = [self.temp_dir.name + "/bin/python"] + list(cmd[1:])
        print(cmd)
        return await super().launch_kernel(cmd, **kwargs)

    async def cleanup(self, restart: bool = False) -> None:
        if not restart and self.temp_dir is not None:
            self.temp_dir.cleanup()
            self.temp_dir = None
        return await super().cleanup(restart=restart)
