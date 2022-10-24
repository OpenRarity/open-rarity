JsonEncodable = str | float | int
JsonContainer = list[JsonEncodable] | dict[JsonEncodable]

JsonEncodable = (
    list[JsonContainer | JsonEncodable]
    | dict[JsonContainer | JsonEncodable]
    | JsonEncodable
)


__all__ = ["JsonEncodable"]
