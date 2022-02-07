"""Rabbit Air protocol client."""

import asyncio
import json
import os
import socket
import time
from abc import ABC, abstractmethod
from random import SystemRandom
from types import TracebackType
from typing import Any, Dict, List, Optional, Type

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .exceptions import ProtocolError
from .response import (
    Info,
    Lights,
    Mode,
    Moodlight,
    Sensitivity,
    Speed,
    State,
    TimerMode,
)


class Client(ABC):
    """Base class for the Rabbit Air protocol client.

    To create an instance of the class use UdpClient or TcpClient."""

    _sock: Optional[socket.socket] = None
    _ts_diff: Optional[float] = None

    def __init__(self, host: str, token: Optional[str], port: int = 9009) -> None:
        """Initialize the client."""
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
        response = await self._exchange(request["id"], data)
        if response.get("error"):
            raise ProtocolError()
        return response

    async def command(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send raw command to the device."""
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
        except ProtocolError:
            raise
        except Exception:
            self._stop()
            raise

    async def get_state(self) -> State:
        """Get the current state of the device."""
        response = await self.command({"cmd": 4})
        return State(response["data"])

    async def set_state(
        self,
        power: Optional[bool] = None,
        mode: Optional[Mode] = None,
        speed: Optional[Speed] = None,
        sensitivity: Optional[Sensitivity] = None,
        ionizer: Optional[bool] = None,
        moodlight: Optional[Moodlight] = None,
        filter_cleaning: Optional[bool] = None,
        filter_replacement: Optional[bool] = None,
        filter_life: Optional[int] = None,
        filter_timer: Optional[int] = None,
        lights: Optional[Lights] = None,
        color: Optional[List] = None,
        light_sensor_ctl: Optional[bool] = None,
        filter_ctl: Optional[bool] = None,
        buzzer: Optional[bool] = None,
        child_lock: Optional[bool] = None,
        timer_mode: Optional[TimerMode] = None,
        timer: Optional[int] = None,
        schedule: Optional[str] = None,
    ) -> None:
        """Change the state of the device."""
        data: Dict[str, Any] = dict()
        if power is not None:
            data["power"] = power
        if mode is not None:
            data["mode"] = mode.value
        if speed is not None:
            data["speed"] = speed.value
        if sensitivity is not None:
            data["sensitivity"] = sensitivity.value
        if ionizer is not None:
            data["ionizer"] = ionizer
        if moodlight is not None:
            data["moodlight"] = moodlight.value
        if filter_cleaning is not None:
            data["filter_cleaning"] = filter_cleaning
        if filter_replacement is not None:
            data["filter_replacement"] = filter_replacement
        if filter_life is not None:
            if filter_life < 0 or filter_life > 525600:
                raise ValueError("The filter life value must be in the range 0-1440")
            data["filter_life"] = filter_life
        if filter_timer is not None:
            if filter_timer < 0 or filter_timer > 525600:
                raise ValueError("The filter timer value must be in the range 0-1440")
            data["filter_timer"] = filter_timer
        if lights is not None:
            data["all_light_off"] = lights.value
        if color is not None:
            if len(color) != 9:
                raise ValueError("The color length must be 9")
            for v in color:
                if v < 0 or v > 40:
                    raise ValueError("The color values must be in the range 0-40")
            data["color"] = color
        if light_sensor_ctl is not None:
            data["lsens_ctl"] = light_sensor_ctl
        if filter_ctl is not None:
            data["filter_ctl"] = filter_ctl
        if buzzer is not None:
            data["buzzer"] = buzzer
        if child_lock is not None:
            data["lock"] = child_lock
        if timer_mode is not None:
            data["timer_mode"] = timer_mode.value
        if timer is not None:
            if timer < 0 or timer > 1440:
                raise ValueError("The timer value must be in the range 0-1440")
            data["timer"] = timer
        if schedule is not None:
            if len(schedule) != 24:
                raise ValueError("The schedule length must be 24")
            for v in schedule:
                if (v < "0" or v > "5") and v != "A":
                    raise ValueError("The schedule values must be 0-5,A")
            data["schedule"] = schedule
        await self.command({"cmd": 4, "data": data})

    async def get_info(self) -> Info:
        """Get information about the device."""
        response = await self.command({"cmd": 255})
        return Info(response["data"])
