from shortuuid.main import int_to_string, string_to_int

import logging

error_logger = logging.getLogger("error_logger")


def limit_string(string: str, length: int = 1024) -> str:
    if len(string) > length:
        return string[: length - 3].rstrip(" .,\n") + "..."
    else:
        return string


# base on https://github.com/skorokithakis/shortuuid
_alphabet = list("23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")


def encode_snowflake(snowflake: int) -> str:
    return int_to_string(snowflake, _alphabet, padding=11)


def decode_snowflake(string: str) -> int:
    return string_to_int(string, _alphabet)


def encode_button_id(label: str, *args, **kwargs) -> str:
    id = ":".join([label, *args, *[f"{key}={value}" for key, value in kwargs.items()]])

    if len(id) > 100:
        raise ValueError("Button ID too long, must be <= 100 characters.")

    return id


def decode_button_id(custom_id: str) -> tuple[str, list[str], dict[str, str]]:
    label, *split = custom_id.split(":")
    args = []
    kwargs = {}

    for arg in split:
        if "=" not in arg:
            args.append(arg)
            continue

        key, value = arg.split("=")
        kwargs[key] = value

    return label, args, kwargs
