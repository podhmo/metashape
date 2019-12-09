import sys
from dictknife import loading
from magicalimport import import_symbol
from metashape.analyze.collector import Collector, _Value
from metashape.analyze.walker import Walker
from metashape.runtime import get_walker


if len(sys.argv) > 1:
    cls = import_symbol(sys.argv[1])
else:
    cls = import_symbol("./conf.py:Toplevel", here=__file__)


@Collector
def collect(target: _Value, *, w: Walker) -> _Value:
    props = {}
    for name, typeinfo, metadata in w.for_type(target).walk():
        fieldname = w.resolver.metadata.resolve_name(metadata, default=name)
        props[fieldname] = collect(getattr(target, name), w=w)
    return props


d = {}
w = get_walker(cls)
for cls in w.walk():
    d.update(collect(cls, w=w))
loading.dumpfile(d, format="yaml")
