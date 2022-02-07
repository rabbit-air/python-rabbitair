"""Rabbit Air UDP-based client."""

import asyncio
import socket
from typing import Any, Dict

from .client import Client


class UdpClient(Client):
    """UDP-based client."""

    retry_count: int = 3
    timeout: float = 2.0

    @classmethod
    def _create_socket(cls) -> socket.socket:
        return socket.socket(type=socket.SOCK_DGRAM)

    async def _recvmsg(self) -> bytes:
        assert self._sock is not None
        loop = asyncio.get_running_loop()
        return await loop.sock_recv(self._sock, 2048)

    async def _sendmsg(self, data: bytes) -> None:
        assert self._sock is not None
        loop = asyncio.get_running_loop()
        await loop.sock_sendall(self._sock, data)

    async def _exchange(self, request_id: int, data: bytes) -> Dict[str, Any]:
        for i in range(self.retry_count):
            try:
                return await asyncio.wait_for(
                    super()._exchange(request_id, data), self.timeout
                )
            except asyncio.TimeoutError as e:
                error = e
        raise error
