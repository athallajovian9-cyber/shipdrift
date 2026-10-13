"""shipdrift: did you release what you merged?"""

from .checks import CHECK_DOCS, CHECKS
from .finding import Finding

__all__ = ["Finding", "CHECKS", "CHECK_DOCS", "lint", "__version__"]
__version__ = "0.1.0"


def lint(repo=".", disabled=()):
    from .engine import lint as _lint

    return _lint(repo, disabled)
