import sys
import typing as t
from dictknife import loading
from magicalimport import import_symbol
from metashape.analyze.collector import Collector, _Value
from metashape.runtime import get_walker


if len(sys.argv) > 1:
    cls = import_symbol(sys.argv[1])
else:
    cls = import_symbol("./conf.py:Toplevel", here=__file__)

w = get_walker(cls)


@Collector
def collect(target: _Value) -> _Value:
    props = {}
    for name, typeinfo, metadata in w.for_type(target).walk():
        fieldname = w.resolver.metadata.resolve_name(metadata, default=name)
        props[fieldname] = collect(getattr(target, name))
    return props


d = {}
for cls in w.walk():
    d.update(collect(cls))
loading.dumpfile(d, format="yaml")
