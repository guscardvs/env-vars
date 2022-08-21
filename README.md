# env-vars

Simplified config for python projects based on starlette config

# Installation

```shell
pip install env-star
```

# Usage

```python
from config import Config

config = Config()

MY_CONST = config(
    'MY_ENV', cast=my_callable_or_class, default=any_castable)
```

