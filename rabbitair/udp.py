import asyncio
import socket
from typing import Any, Dict

from .client import Client

UDP_RETRY_COUNT = 3
UDP_TIMEOUT = 1.5


class UdpClient(Client):
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
        for i in range(UDP_RETRY_COUNT):
            try:
                return await asyncio.wait_for(
                    super()._exchange(request_id, data), UDP_TIMEOUT
                )
            except asyncio.TimeoutError as e:
                error = e
        raise error
