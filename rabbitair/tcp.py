"""Rabbit Air TCP-based client."""

import asyncio
import socket
import struct
from typing import Any, Dict

from .client import Client
from .exceptions import NetworkError


class TcpClient(Client):
    """TCP-based client."""

    timeout: float = 5.0

    @classmethod
    def _create_socket(cls) -> socket.socket:
        return socket.socket(type=socket.SOCK_STREAM)

    @staticmethod
    async def _recvall(sock: socket.socket, size: int) -> bytes:
        data = b""
        loop = asyncio.get_running_loop()
        while len(data) < size:
            chunk = await loop.sock_recv(sock, size - len(data))
            if not chunk:
                break
            data += chunk
        if len(data) != size:
            raise NetworkError("Connection was unexpectedly closed")
        return data

    async def _recvmsg(self) -> bytes:
        assert self._sock is not None
        header = await self._recvall(self._sock, 2)
        size = struct.unpack("<H", header)[0]
        return await self._recvall(self._sock, size)

    async def _sendmsg(self, data: bytes) -> None:
        assert self._sock is not None
        loop = asyncio.get_running_loop()
        await loop.sock_sendall(self._sock, struct.pack("<H", len(data)) + data)

    async def _exchange(self, request_id: int, data: bytes) -> Dict[str, Any]:
        return await asyncio.wait_for(super()._exchange(request_id, data), self.timeout)
