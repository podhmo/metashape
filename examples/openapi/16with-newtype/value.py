from metashape.outputs.openapi import types


class Value:
    number_value: types.Number
    float_value: types.Float
    double_value: types.Double

    int_value: types.Integer
    int32_value: types.Int32
    int64_value: types.Int64

    string_value: types.String
    date_value: types.Date
    datetime_value: types.DateTime
    password_value: types.Password
    byte_value: types.Byte
    binary_value: types.Binary
    email_value: types.Email
    uuid_value: types.UUID
    uri_value: types.URI
    hostname_value: types.Hostname
    ipv4_value: types.IPV4
    ipv6_value: types.IPV6
