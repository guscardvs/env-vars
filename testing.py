from typing import Literal

from config.utils import literal_cast

literal_cast(Literal["asyncio", "sync"])("sync")
