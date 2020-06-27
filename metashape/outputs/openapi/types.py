import typing as t

# see: https://swagger.io/docs/specification/data-models/data-types/
number = float
double = t.NewType("double", number)
float = t.NewType("float", number)

integer = int
int32 = t.NewType("int32", int)
int64 = t.NewType("int64", int)

string = str
date = t.NewType("date", str)
date_time = t.NewType("date_time", str)
password = t.NewType("password", str)

byte = bytes
binary = t.NewType("binary", byte)
email = t.NewType("email", str)
uuid = t.NewType("uuid", str)
uri = t.NewType("uri", str)
hostname = t.NewType("hostname", str)
ipv4 = t.NewType("ipv4", str)
ipv6 = t.NewType("ipv6", str)
