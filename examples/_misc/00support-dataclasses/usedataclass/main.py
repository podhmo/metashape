import dataclasses
import logging
from dictknife import loading

from conf import toplevel as target

logging.basicConfig(level=logging.DEBUG)
d = dataclasses.asdict(target)
loading.dumpfile(d, format="yaml")
