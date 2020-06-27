import typing as t

# see: https://swagger.io/docs/specification/data-models/data-types/
Number = float
Double = t.NewType("double", float)
Float = t.NewType("float", float)

Integer = int
Int32 = t.NewType("int32", int)
Int64 = t.NewType("int64", int)

String = str
Date = t.NewType("date", str)
DateTime = t.NewType("date-time", str)
Password = t.NewType("password", str)

Byte = bytes
Binary = t.NewType("binary", bytes)
Email = t.NewType("email", str)
UUID = t.NewType("uuid", str)
URI = t.NewType("uri", str)
Hostname = t.NewType("hostname", str)
IPV4 = t.NewType("ipv4", str)
IPV6 = t.NewType("ipv6", str)
