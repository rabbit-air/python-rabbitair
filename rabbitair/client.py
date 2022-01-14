import asyncio
import json
import os
import socket
import time
from abc import ABC, abstractmethod
from random import SystemRandom
from types import TracebackType
from typing import Any, Dict, Optional, Type

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class Client(ABC):

    _sock: Optional[socket.socket] = None
    _ts_diff: Optional[float] = None

    def __init__(self, host: str, token: Optional[str], port: int = 9009) -> None:
        self._host = host
        self._token = bytes.fromhex(token) if token else None
        self._port = port
        self._id = SystemRandom().randrange(0x1000000)

    def __enter__(self) -> "Client":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        if self._sock is not None:
            self._sock.close()
        return None

    @classmethod
    @abstractmethod
    def _create_socket(cls) -> socket.socket:
        pass

    async def _start(self) -> None:
        assert self._sock is None
        self._sock = self._create_socket()
        self._sock.setblocking(False)
        loop = asyncio.get_running_loop()
        await loop.sock_connect(self._sock, (self._host, self._port))

    def _stop(self) -> None:
        assert self._sock is not None
        self._sock.close()
        self._sock = None
        self._ts_diff = None

    @staticmethod
    def _clock() -> float:
        return time.clock_gettime(time.CLOCK_BOOTTIME)

    def _get_ts(self) -> int:
        assert self._ts_diff is not None
        return round(self._clock() + self._ts_diff)

    def _next_id(self) -> int:
        value = self._id
        self._id += 1
        return value

    def _decrypt(self, msg: bytes) -> bytes:
        assert self._token is not None
        iv = msg[-16:]
        msg = msg[:-16]
        cipher = Cipher(algorithms.AES(self._token), modes.CBC(iv), default_backend())
        decryptor = cipher.decryptor()
        msg = decryptor.update(msg) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(msg) + unpadder.finalize()

    def _encrypt(self, msg: bytes) -> bytes:
        assert self._token is not None
        padder = padding.PKCS7(128).padder()
        msg = padder.update(msg) + padder.finalize()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self._token), modes.CBC(iv), default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(msg) + encryptor.finalize() + iv

    @abstractmethod
    async def _recvmsg(self) -> bytes:
        pass

    @abstractmethod
    async def _sendmsg(self, data: bytes) -> None:
        pass

    async def _exchange(self, request_id: int, data: bytes) -> Dict[str, Any]:
        await self._sendmsg(data)
        while True:
            data = await self._recvmsg()
            if self._token:
                data = self._decrypt(data)
            try:
                response = json.loads(data)
                if response["id"] == request_id:
                    return response
            except (json.JSONDecodeError, KeyError):
                # Ignore any garbage or unexpected responses
                pass

    async def _command(self, request: Dict[str, Any]) -> Dict[str, Any]:
        data = json.dumps(request, separators=(",", ":")).encode()
        if self._token:
            data = self._encrypt(data)
        return await self._exchange(request["id"], data)

    async def command(self, request: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self._sock:
                await self._start()
            if self._token:
                if self._ts_diff is None:
                    ts_request = {"id": self._next_id(), "cmd": 9}
                    response = await self._command(ts_request)
                    ts = response["data"]["ts"]
                    self._ts_diff = ts - self._clock()
                    request["ts"] = ts
                else:
                    request["ts"] = self._get_ts()
            request["id"] = self._next_id()
            return await self._command(request)
        except Exception:
            self._stop()
            raise
