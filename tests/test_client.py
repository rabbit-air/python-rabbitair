import asyncio
import json
from typing import Any, Callable, Dict, Optional
from unittest.mock import Mock, patch

import pytest
from rabbitair import (
    Error,
    FilterType,
    Gas,
    Info,
    Lights,
    Mode,
    Model,
    Moodlight,
    ProtocolError,
    Quality,
    Sensitivity,
    Speed,
    State,
    TimerMode,
    UdpClient,
)

TEST_IP = "192.0.2.1"
TEST_TOKEN = "0123456789ABCDEF0123456789ABCDEF"

TEST_STATE_RESPONSE_A2 = """{
    "id": 0,
    "data": {
        "model": 1,
        "firmware": [3],
        "power": true,
        "mode": 0,
        "speed": 1,
        "quality": 4,
        "sensitivity": 0,
        "ionizer": false,
        "moodlight": 0,
        "sleep": false,
        "filter_replacement": false,
        "filter_life": 525600,
        "light_sensor": true,
        "particulate_sensor": 0,
        "filter_timer": 525580,
        "all_light_off": 2,
        "error": 0,
        "timer_mode": 0,
        "timer": 1,
        "schedule": "AAAAAAAAAAAAAAAAAAAAAAAA",
        "rssi": -61,
        "v": "2.3.17"
    }
}"""

TEST_STATE_RESPONSE_A3 = """{
    "id": 0,
    "data": {
        "model": 3,
        "firmware": [1, 0, 0, 4],
        "power": true,
        "mode": 2,
        "speed": 4,
        "quality": 3,
        "sensitivity": 2,
        "ionizer": true,
        "idle": 0,
        "moodlight": 1,
        "filter_cleaning": false,
        "filter_replacement": false,
        "filter_life": 525600,
        "light_sensor": true,
        "filter_timer": 525580,
        "all_light_off": 1,
        "error": 0,
        "tag_state": 0,
        "tag_uid": [0, 0, 0, 0, 0, 0, 0],
        "filter_type": 0,
        "pm_sensor": [19, 29, 31],
        "color": [31, 0, 20, 0, 22, 40, 22, 30, 6],
        "lsens_ctl": false,
        "filter_ctl": false,
        "buzzer": false,
        "gas": 0,
        "lock": false,
        "open": false,
        "timer_mode": 0,
        "timer": 0,
        "schedule": "AAAAAAAAAAAAAAAAAAAAAAAA",
        "rssi": -52,
        "v": "2.3.17"
    }
}"""

TEST_TS_RESPONSE = """{
    "id": 0,
    "data": {
        "v": 1,
        "ts": 103431
    }
}"""

TEST_INFO_RESPONSE_A2 = """{
    "id": 0,
    "data": {
        "name": "1234567890_123456789012345678",
        "mcu": "2.3.17",
        "build": "Nov 29 2021 21:41:45",
        "wifi": "v3.3.2",
        "mac": "01:23:45:67:89:AB",
        "time": "22:35:29",
        "heap": 69304,
        "hmin": 57004,
        "stack": 1372,
        "clk": 80000000,
        "uptime": 314070,
        "mup": 65174,
        "wup": 306293,
        "iup": 294213,
        "cup": 297758,
        "flc": 1,
        "ftc": 0,
        "errb": 8,
        "errw": 1263,
        "rssi": {
            "cur": -68,
            "min": -78,
            "max": -58,
            "avg": -66
        }
    }
}"""

TEST_INFO_RESPONSE_A3 = """{
    "id": 0,
    "data": {
        "name": "1234567890_123456789012345678",
        "mcu": "2.3.17",
        "build": "Nov 29 2021 21:41:45",
        "wifi": "v3.3.2",
        "mac": "01:23:45:67:89:AB",
        "time": "22:35:29",
        "heap": 69304,
        "hmin": 57004,
        "stack": 1372,
        "clk": 80000000,
        "uptime": 314070,
        "mup": 65174,
        "wup": 306293,
        "iup": 294213,
        "cup": 297758,
        "flc": 1,
        "ftc": 0,
        "errb": 8,
        "errw": 1263,
        "fv":"1.0.0.4",
        "rssi": {
            "cur": -68,
            "min": -78,
            "max": -58,
            "avg": -66
        }
    }
}"""


def mock_command(model: Optional[Model]) -> Callable:
    if model is Model.MinusA2:
        state_response = TEST_STATE_RESPONSE_A2
        info_response = TEST_INFO_RESPONSE_A2
    elif model is Model.A3:
        state_response = TEST_STATE_RESPONSE_A3
        info_response = TEST_INFO_RESPONSE_A3
    else:
        state_response = "{}"
        info_response = "{}"

    async def command(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if request["cmd"] == 4:
            response = state_response
        elif request["cmd"] == 9:
            response = TEST_TS_RESPONSE
        elif request["cmd"] == 255:
            response = info_response
        else:
            assert False
        result = json.loads(response)
        result["id"] = request["id"]
        return result

    return command


@pytest.mark.parametrize("token", [TEST_TOKEN.lower(), TEST_TOKEN.upper(), "", None])
def test_create(token: str) -> None:
    client = UdpClient(TEST_IP, token)


@pytest.mark.parametrize(
    "token", [TEST_TOKEN[:30], TEST_TOKEN + TEST_TOKEN, TEST_TOKEN.replace("1", "x")]
)
def test_create_fail(token: str) -> None:
    with pytest.raises(ValueError):
        client = UdpClient(TEST_IP, token)


async def test_zeroconf() -> None:
    info = Mock()
    info.parsed_addresses.return_value = [TEST_IP]

    async def async_get_service_info(type: str, name: str) -> Mock:
        return info

    zc = Mock()
    zc.async_get_service_info = async_get_service_info
    with patch(
        "rabbitair.Client._command", new_callable=mock_command, model=Model.MinusA2
    ):
        with UdpClient("test.local", TEST_TOKEN, zeroconf=zc) as client:
            state = await client.get_state()

    assert len(info.parsed_addresses.mock_calls) == 1


async def test_state_a2() -> None:
    with patch(
        "rabbitair.Client._command", new_callable=mock_command, model=Model.MinusA2
    ):
        with UdpClient(TEST_IP, TEST_TOKEN) as client:
            state = await client.get_state()

    assert state.model is Model.MinusA2
    assert state.main_firmware == "3"
    assert state.power is True
    assert state.mode is Mode.Auto
    assert state.speed is Speed.Silent
    assert state.quality is Quality.Highest
    assert state.sensitivity is Sensitivity.High
    assert state.ionizer is False
    assert state.idle is None
    assert state.moodlight is Moodlight.Off
    assert state.sleep is False
    assert state.filter_cleaning is None
    assert state.filter_replacement is False
    assert state.filter_life == 525600
    assert state.light_sensor is True
    assert state.particulate_sensor == 0
    assert state.filter_timer == 525580
    assert state.lights is Lights.Auto
    assert state.error is Error.NoError
    assert state.tag_state is None
    assert state.tag_uid is None
    assert state.filter_type is None
    assert state.pm_sensor is None
    assert state.color is None
    assert state.light_sensor_ctl is None
    assert state.filter_ctl is None
    assert state.buzzer is None
    assert state.gas is None
    assert state.child_lock is None
    assert state.open is None
    assert state.timer_mode is TimerMode.Off
    assert state.timer == 1
    assert state.schedule == "AAAAAAAAAAAAAAAAAAAAAAAA"
    assert state.rssi == -61
    assert state.wifi_firmware == "2.3.17"


async def test_state_a3() -> None:
    with patch("rabbitair.Client._command", new_callable=mock_command, model=Model.A3):
        with UdpClient(TEST_IP, TEST_TOKEN) as client:
            state = await client.get_state()

    assert state.model is Model.A3
    assert state.main_firmware == "1.0.0.4"
    assert state.power is True
    assert state.mode is Mode.Manual
    assert state.speed is Speed.High
    assert state.quality is Quality.High
    assert state.sensitivity is Sensitivity.Low
    assert state.ionizer is True
    assert state.idle is False
    assert state.moodlight is Moodlight.On
    assert state.sleep is None
    assert state.filter_cleaning is False
    assert state.filter_replacement is False
    assert state.filter_life == 525600
    assert state.light_sensor is True
    assert state.particulate_sensor is None
    assert state.filter_timer == 525580
    assert state.lights is Lights.On
    assert state.error is Error.NoError
    assert state.tag_state is False
    assert state.tag_uid == [0, 0, 0, 0, 0, 0, 0]
    assert state.filter_type is FilterType.Unknown
    assert state.pm_sensor == [19, 29, 31]
    assert state.color == [31, 0, 20, 0, 22, 40, 22, 30, 6]
    assert state.light_sensor_ctl is False
    assert state.filter_ctl is False
    assert state.buzzer is False
    assert state.gas is Gas.Preheat
    assert state.child_lock is False
    assert state.open is False
    assert state.timer_mode is TimerMode.Off
    assert state.timer == 0
    assert state.schedule == "AAAAAAAAAAAAAAAAAAAAAAAA"
    assert state.rssi == -52
    assert state.wifi_firmware == "2.3.17"


@pytest.mark.parametrize("model,fv", [(Model.MinusA2, None), (Model.A3, "1.0.0.4")])
async def test_info(model, fv) -> None:
    with patch("rabbitair.Client._command", new_callable=mock_command, model=model):
        with UdpClient(TEST_IP, TEST_TOKEN) as client:
            info = await client.get_info()

    assert info.name == "1234567890_123456789012345678"
    assert info.wifi_firmware == "2.3.17"
    assert info.build == "Nov 29 2021 21:41:45"
    assert info.mac == "01:23:45:67:89:AB"
    assert info.time == "22:35:29"
    assert info.uptime == 314070
    assert info.motor_uptime == 65174
    assert info.wifi_uptime == 306293
    assert info.internet_uptime == 294213
    assert info.cloud_uptime == 297758
    assert info.main_firmware == fv
    assert info.rssi.current == -68
    assert info.rssi.min == -78
    assert info.rssi.max == -58
    assert info.rssi.average == -66


async def test_no_response() -> None:
    with patch("rabbitair.Client._command", side_effect=asyncio.TimeoutError):
        with UdpClient(TEST_IP, TEST_TOKEN) as client:
            with pytest.raises(asyncio.TimeoutError):
                state = await client.get_state()


async def test_protocol_error() -> None:
    with patch("rabbitair.Client._command", side_effect=ProtocolError):
        with UdpClient(TEST_IP, TEST_TOKEN) as client:
            with pytest.raises(ProtocolError):
                state = await client.get_state()


async def test_sequential_requests() -> None:
    with patch(
        "rabbitair.Client._command", new_callable=mock_command, model=Model.MinusA2
    ):
        with UdpClient(TEST_IP, TEST_TOKEN) as client:
            state = await client.get_state()
            info = await client.get_info()


async def test_set_state() -> None:
    with patch("rabbitair.Client._command", new_callable=mock_command, model=Model.A3):
        with UdpClient(TEST_IP, TEST_TOKEN) as client:
            await client.set_state(
                power=True,
                mode=Mode.Manual,
                speed=Speed.Medium,
                sensitivity=Sensitivity.Medium,
                ionizer=True,
                moodlight=Moodlight.On,
                filter_cleaning=False,
                filter_replacement=False,
                filter_life=525600,
                filter_timer=0,
                lights=Lights.Off,
                color=[31, 0, 20, 0, 22, 40, 22, 30, 6],
                light_sensor_ctl=True,
                filter_ctl=True,
                buzzer=True,
                child_lock=False,
                timer_mode=TimerMode.Schedule,
                timer=60,
                schedule="A012345A012345A012345A01",
            )
            with pytest.raises(ValueError):
                await client.set_state(filter_life=-1)
            with pytest.raises(ValueError):
                await client.set_state(filter_life=525601)
            with pytest.raises(ValueError):
                await client.set_state(filter_timer=-1)
            with pytest.raises(ValueError):
                await client.set_state(filter_timer=525601)
            with pytest.raises(ValueError):
                await client.set_state(color=[])
            with pytest.raises(ValueError):
                await client.set_state(color=[41, -1, 20, 0, 22, 40, 22, 30, 6])
            with pytest.raises(ValueError):
                await client.set_state(timer=-1)
            with pytest.raises(ValueError):
                await client.set_state(timer=1441)
            with pytest.raises(ValueError):
                await client.set_state(schedule="A12")
            with pytest.raises(ValueError):
                await client.set_state(schedule="ABC6789AAAAAAAAAAAAAAAAA")
