"""Rabbit Air responses."""

import inspect
from enum import Enum, unique
from typing import Generic, List, Optional, TypeVar

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

T = TypeVar("T")


@unique
class Model(Enum):
    """Device model."""

    MinusA2 = 1
    BioGS = 2
    A3 = 3


@unique
class Mode(Enum):
    """Mode of operation."""

    Auto = 0
    Pollen = 1
    Manual = 2


@unique
class Speed(Enum):
    """Fan speed.

    Note: SuperSilent mode cannot be set manually.
    """

    SuperSilent = 0
    Silent = 1
    Low = 2
    Medium = 3
    High = 4
    Turbo = 5


@unique
class Quality(Enum):
    """Air quality.

    Note: the Lowest value is not actually used.
    """

    Lowest = 0
    Low = 1
    Medium = 2
    High = 3
    Highest = 4


@unique
class Sensitivity(Enum):
    """Sensitivity level of the sensors."""

    High = 0
    Medium = 1
    Low = 2


class Moodlight(Enum):
    """Mood Light mode."""

    Off = 0
    On = 1
    Auto = 2
    Preset1 = 2
    Preset2 = 3
    Preset3 = 4


@unique
class Lights(Enum):
    """Light settings."""

    Off = 0
    On = 1
    Auto = 2


@unique
class Error(Enum):
    """Internal error codes."""

    NoError = 0
    DustSensor = 1
    GasSensor = 2
    GasAndDust = 3
    FanLow = 4
    NFC = 5
    HallSensor = 8


@unique
class FilterType(Enum):
    """Filter type."""

    Unknown = 0
    ToxinAbsorber = 1
    OdorRemover = 2
    GermDefense = 3
    PetAllergy = 4


@unique
class Gas(Enum):
    """Gas sensor readings."""

    Preheat = 0
    Level1 = 1
    Level2 = 2
    Level3 = 3
    Level4 = 4


@unique
class TimerMode(Enum):
    """Timer mode."""

    Off = 0
    On = 1
    Schedule = 2


class StateDict(TypedDict, total=False):
    """State response typing."""

    model: int
    firmware: List[int]
    power: bool
    mode: int
    speed: int
    quality: int
    sensitivity: int
    ionizer: bool
    idle: int
    moodlight: int
    sleep: bool
    filter_cleaning: bool
    filter_replacement: bool
    filter_life: int
    light_sensor: bool
    particulate_sensor: int
    filter_timer: int
    all_light_off: int
    error: int
    tag_state: int
    tag_uid: List[int]
    filter_type: int
    pm_sensor: List[int]
    color: List[int]
    lsens_ctl: bool
    filter_ctl: bool
    buzzer: bool
    gas: int
    lock: bool
    open: bool
    timer_mode: int
    timer: int
    schedule: str
    rssi: int
    v: str


class RssiDict(TypedDict, total=False):
    """RSSI typing."""

    cur: int
    min: int
    max: int
    avg: int


class InfoDict(TypedDict, total=False):
    """Info response typing."""

    name: str
    mcu: str
    build: str
    mac: str
    time: str
    uptime: int
    mup: int
    wup: int
    iup: int
    cup: int
    fv: str
    rssi: RssiDict


class Response(Generic[T]):
    """Base class for the device response."""

    def __init__(self, data: T) -> None:
        """Initialize."""
        self.data = data

    def __repr__(self) -> str:
        """Return the string representation of the object."""
        items = []
        props = inspect.getmembers(type(self), lambda x: isinstance(x, property))
        for name, prop in props:
            try:
                value = prop.fget(self)
            except Exception as ex:
                value = repr(ex)
            items.append(f"{name}={value}")
        return f"<{type(self).__name__} {' '.join(items)}>"


class State(Response[StateDict]):
    """Device state."""

    @property
    def model(self) -> Optional[Model]:
        """Device model."""
        value = self.data.get("model")
        return None if value is None else Model(value)

    @property
    def main_firmware(self) -> Optional[str]:
        """Version of the main board firmware."""
        value = self.data.get("firmware")
        if value is None:
            return None
        return ".".join(str(x) for x in value)

    @property
    def power(self) -> Optional[bool]:
        """Power on/off."""
        return self.data.get("power")

    @property
    def mode(self) -> Optional[Mode]:
        """Mode of operation."""
        value = self.data.get("mode")
        return None if value is None else Mode(value)

    @property
    def speed(self) -> Optional[Speed]:
        """Fan speed."""
        value = self.data.get("speed")
        return None if value is None else Speed(value)

    @property
    def quality(self) -> Optional[Quality]:
        """Air quality."""
        value = self.data.get("quality")
        if value is None:
            return None
        if self.model is Model.BioGS:
            return Quality(value - 1)
        else:
            return Quality(value)

    @property
    def sensitivity(self) -> Optional[Sensitivity]:
        """Sensitivity level of the sensors."""
        value = self.data.get("sensitivity")
        return None if value is None else Sensitivity(value)

    @property
    def ionizer(self) -> Optional[bool]:
        """Negative ion on/off."""
        return self.data.get("ionizer")

    @property
    def idle(self) -> Optional[bool]:
        """Device is in idle mode."""
        value = self.data.get("idle")
        return None if value is None else bool(value)

    @property
    def moodlight(self) -> Optional[Moodlight]:
        """Mood Light mode."""
        value = self.data.get("moodlight")
        return None if value is None else Moodlight(value)

    @property
    def sleep(self) -> Optional[bool]:
        """Device is in sleep mode."""
        return self.data.get("sleep")

    @property
    def filter_cleaning(self) -> Optional[bool]:
        """Filter cleaning required."""
        return self.data.get("filter_cleaning")

    @property
    def filter_replacement(self) -> Optional[bool]:
        """Filter replacement required."""
        return self.data.get("filter_replacement")

    @property
    def filter_life(self) -> Optional[int]:
        """Remaining filter lifetime."""
        return self.data.get("filter_life")

    @property
    def light_sensor(self) -> Optional[bool]:
        """Light sensor readings."""
        return self.data.get("light_sensor")

    @property
    def particulate_sensor(self) -> Optional[int]:
        """Particle sensor readings."""
        return self.data.get("particulate_sensor")

    @property
    def filter_timer(self) -> Optional[int]:
        """Nominal filter lifetime."""
        return self.data.get("filter_timer")

    @property
    def lights(self) -> Optional[Lights]:
        """Turn all light on/off."""
        value = self.data.get("all_light_off")
        return None if value is None else Lights(value)

    @property
    def error(self) -> Optional[Error]:
        """Internal error codes."""  # noqa: D401
        value = self.data.get("error")
        return None if value is None else Error(value)

    @property
    def tag_state(self) -> Optional[bool]:
        """Filter tag state."""
        value = self.data.get("tag_state")
        return None if value is None else bool(value)

    @property
    def tag_uid(self) -> Optional[List[int]]:
        """Filter tag unique identifier."""
        return self.data.get("tag_uid")

    @property
    def filter_type(self) -> Optional[FilterType]:
        """Filter type."""
        value = self.data.get("filter_type")
        return None if value is None else FilterType(value)

    @property
    def pm_sensor(self) -> Optional[List[int]]:
        """Extended particle sensor readings."""  # noqa: D401
        return self.data.get("pm_sensor")

    @property
    def color(self) -> Optional[List[int]]:
        """Color palette for Mood Light."""
        return self.data.get("color")

    @property
    def light_sensor_ctl(self) -> Optional[bool]:
        """Activate/deactivate light sensor."""
        return self.data.get("lsens_ctl")

    @property
    def filter_ctl(self) -> Optional[bool]:
        """Activate/deactivate notification about filter replacement condition."""
        return self.data.get("filter_ctl")

    @property
    def buzzer(self) -> Optional[bool]:
        """Buzzer sound on/off."""
        return self.data.get("buzzer")

    @property
    def gas(self) -> Optional[Gas]:
        """Gas sensor readings."""
        value = self.data.get("gas")
        return None if value is None else Gas(value)

    @property
    def child_lock(self) -> Optional[bool]:
        """Child lock on/off."""
        return self.data.get("lock")

    @property
    def open(self) -> Optional[bool]:
        """Front panel is removed or open."""
        return self.data.get("open")

    @property
    def timer_mode(self) -> Optional[TimerMode]:
        """Timer mode."""
        value = self.data.get("timer_mode")
        return None if value is None else TimerMode(value)

    @property
    def timer(self) -> Optional[int]:
        """Time, in minutes, remaining until the unit is turned off."""
        return self.data.get("timer")

    @property
    def schedule(self) -> Optional[str]:
        """24-h schedule.

        This is a 24-character string in which each character specifies the speed for a specific hour.
        Acceptable values are 1-5 and A (auto). The time is in UTC.
        """
        return self.data.get("schedule")

    @property
    def rssi(self) -> Optional[int]:
        """Wi-Fi RSSI value averaged over an hour."""
        return self.data.get("rssi")

    @property
    def wifi_firmware(self) -> Optional[str]:
        """Version of the Wi-Fi board firmware."""
        return self.data.get("v")


class RSSI(Response[RssiDict]):
    """Detailed information about Wi-Fi RSSI."""

    @property
    def current(self) -> Optional[int]:
        """Current RSSI value."""  # noqa: D401
        return self.data.get("cur")

    @property
    def min(self) -> Optional[int]:
        """Minimal RSSI value for an hour."""
        return self.data.get("min")

    @property
    def max(self) -> Optional[int]:
        """Maximal RSSI value for an hour."""
        return self.data.get("max")

    @property
    def average(self) -> Optional[int]:
        """RSSI value averaged over an hour."""
        return self.data.get("avg")


class Info(Response[InfoDict]):
    """Information about the device."""

    @property
    def name(self) -> str:
        """Device ID."""
        return self.data["name"]

    @property
    def wifi_firmware(self) -> str:
        """Version of the Wi-Fi board firmware."""
        return self.data["mcu"]

    @property
    def build(self) -> str:
        """Build date of the Wi-Fi board firmware."""
        return self.data["build"]

    @property
    def mac(self) -> str:
        """MAC address."""
        return self.data["mac"]

    @property
    def time(self) -> Optional[str]:
        """Current time."""  # noqa: D401
        return self.data.get("time")

    @property
    def uptime(self) -> int:
        """Total uptime."""
        return self.data["uptime"]

    @property
    def motor_uptime(self) -> int:
        """Total motor runtime."""
        return self.data["mup"]

    @property
    def wifi_uptime(self) -> int:
        """Total Wi-Fi uptime."""
        return self.data["wup"]

    @property
    def internet_uptime(self) -> Optional[int]:
        """Total internet uptime."""
        return self.data.get("iup")

    @property
    def cloud_uptime(self) -> Optional[int]:
        """Total cloud uptime."""
        return self.data.get("cup")

    @property
    def main_firmware(self) -> Optional[str]:
        """Version of the main board firmware."""
        return self.data.get("fv")

    @property
    def rssi(self) -> Optional[RSSI]:
        """Detailed information about Wi-Fi RSSI."""
        value = self.data.get("rssi")
        return None if value is None else RSSI(value)
