import sys
from os import path

sys.path.insert(0, path.dirname(__file__))

from version import version as __version__
from version import installpath as __installpath__

sys.path.pop(0)
