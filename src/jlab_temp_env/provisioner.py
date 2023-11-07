from typing import Any

from jupyter_client import LocalProvisioner
from traitlets import Unicode


class TempEnvProvisioner(LocalProvisioner):
    role: str = Unicode(config=True)

    async def pre_launch(self, **kwargs: Any) -> dict[str, Any]:
        if not self.user_in_role(self.role):
            raise PermissionError(
                f"User is not in role {self.role} and " f"cannot launch this kernel."
            )

        return await super().pre_launch(**kwargs)
