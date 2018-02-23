import sys as _sys
from distutils.version import LooseVersion as __LV

#from . import conv
from . import geo
#import geo
from .parsers.dvl_parser import DVLparser
from .parsers.dbd_parsers import DbaDataParser
from .parsers.gliderstate_parser import GSxml
#from .parsers.dbd_parsers import DataVizDataParser

# seawater 3 uses the GSW package that only works for version 3.5 and higher
_ver = "%d.%d" % (_sys.version_info.major, _sys.version_info.minor)
if __LV(_ver) >= __LV("3.5"):
    from . import seawater3 as sw
else:
    try:
        from . import seawater2 as sw
    except ImportError:
        pass