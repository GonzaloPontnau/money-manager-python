import os
import sys

env = os.environ.get("APP_ENV", os.environ.get("DJANGO_ENV", "development")).lower()

if "test" in sys.argv:
    from .test import *  # noqa: F401,F403
elif env in {"prod", "production"}:
    from .prod import *  # noqa: F401,F403
elif env in {"test", "testing"}:
    from .test import *  # noqa: F401,F403
else:
    from .dev import *  # noqa: F401,F403
