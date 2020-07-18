from dictknife import loading
from metashape.analyze.collector import Collector, _Value
from metashape.analyze.walker import Walker
from metashape.runtime import get_walker
from conf import toplevel


@Collector
def collect(cls: _Value, *, w: Walker) -> _Value:
    props = {}
    for name, typeinfo, metadata in w.walk_fields(cls):
        fieldname = w.resolver.metadata.resolve_name(metadata, default=name)
        value = getattr(cls, name, None)
        if value is None:
            value = typeinfo.raw
        props[fieldname] = collect(value, w=w)
    return props


d = {}
w = get_walker({"toplevel": toplevel})
for cls in w.walk(nocheck=True):
    d.update(collect(cls, w=w))
loading.dumpfile(d, format="yaml")
