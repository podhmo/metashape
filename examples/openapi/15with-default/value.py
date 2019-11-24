from metashape.declarative import field


class Value:
    name: str
    name_with_default: str = field("", metadata={"openapi": {"maxlength": 255}})
    name_with_metadata_only: str = field(metadata={"openapi": {"maxlength": 255}})
