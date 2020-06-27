from metashape.outputs.openapi import types


class Value:
    number_value: types.number
    float_value: types.float
    double_value: types.double

    int_value: types.integer
    int32_value: types.int32
    int64_value: types.int64

    string_value: types.string
    date_value: types.date
    datetime_value: types.date_time
    password_value: types.password
    byte_value: types.byte
    binary_value: types.binary
    email_value: types.email
    uuid_value: types.uuid
    uri_value: types.uri
    hostname_value: types.hostname
    ipv4_value: types.ipv4
    ipv6_value: types.ipv6
