"""Rabbit Air Python library exceptions."""


class NetworkError(Exception):
    """The network connection behaved in an unexpected way."""

    pass


class ProtocolError(Exception):
    """The protocol message was recognized but has invalid parameters."""

    pass
