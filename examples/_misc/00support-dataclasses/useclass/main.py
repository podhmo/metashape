from dictknife import loading
from metashape.analyze.collector import Collector, _Value
from metashape.analyze.walker import Walker
from metashape.runtime import get_walker
from conf import Toplevel as target


@Collector
def collect(cls: _Value, *, w: Walker) -> _Value:
    props = {}
    for name, typeinfo, metadata in w.walk_fields(cls):
        fieldname = w.resolver.metadata.resolve_name(metadata, default=name)
        props[fieldname] = collect(getattr(cls, name, None) or typeinfo.raw, w=w)
    return props


d = {}
w = get_walker(target)
for cls in w.walk():
    d.update(collect(cls, w=w))
loading.dumpfile(d, format="yaml")
