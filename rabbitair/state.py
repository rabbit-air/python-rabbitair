import inspect
from enum import Enum, unique
from typing import Any, Dict, List, Optional


@unique
class Model(Enum):
    MinusA2 = 1
    BioGS = 2
    MinusA3 = 3


@unique
class Mode(Enum):
    Auto = 0
    Pollen = 1
    Manual = 2


@unique
class Speed(Enum):
    Standby = 0
    Silent = 1
    Low = 2
    Medium = 3
    High = 4
    Turbo = 5


@unique
class Sensitivity(Enum):
    High = 0
    Medium = 1
    Low = 2


class Moodlight(Enum):
    Off = 0
    On = 1
    Auto = 2
    Preset1 = 2
    Preset2 = 3
    Preset3 = 4


@unique
class Lights(Enum):
    Off = 0
    On = 1
    Auto = 2


@unique
class Error(Enum):
    NoError = 0
    DustSensor = 1
    GasSensor = 2
    GasAndDust = 3
    FanLow = 4
    NFC = 5
    HallSensor = 8


@unique
class FilterType(Enum):
    Unknown = 0
    ToxinAbsorber = 1
    OdorRemover = 2
    GermDefense = 3
    PetAllergy = 4


@unique
class Gas(Enum):
    Preheat = 0
    Level1 = 1
    Level2 = 2
    Level3 = 3
    Level4 = 4


@unique
class TimerMode(Enum):
    Off = 0
    On = 1
    Schedule = 2


class State:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    def __repr__(self):
        items = []
        props = inspect.getmembers(type(self), lambda x: isinstance(x, property))
        for name, prop in props:
            try:
                value = prop.fget(self)
            except Exception as ex:
                value = repr(ex)
            items.append(f"{name}={value}")
        return f"<{type(self).__name__} {' '.join(items)}>"

    @property
    def model(self) -> Optional[Model]:
        value = self.data.get("model")
        return None if value is None else Model(value)

    @property
    def firmware(self) -> Optional[List]:
        return self.data.get("firmware")

    @property
    def power(self) -> Optional[bool]:
        return self.data.get("power")

    @property
    def mode(self) -> Optional[Mode]:
        value = self.data.get("mode")
        return None if value is None else Mode(value)

    @property
    def speed(self) -> Optional[Speed]:
        value = self.data.get("speed")
        return None if value is None else Speed(value)

    @property
    def quality(self) -> Optional[int]:
        return self.data.get("quality")

    @property
    def sensitivity(self) -> Optional[Sensitivity]:
        value = self.data.get("sensitivity")
        return None if value is None else Sensitivity(value)

    @property
    def ionizer(self) -> Optional[bool]:
        return self.data.get("ionizer")

    @property
    def idle(self) -> Optional[bool]:
        return self.data.get("idle")

    @property
    def moodlight(self) -> Optional[Moodlight]:
        value = self.data.get("moodlight")
        return None if value is None else Moodlight(value)

    @property
    def sleep(self) -> Optional[bool]:
        return self.data.get("sleep")

    @property
    def filter_cleaning(self) -> Optional[bool]:
        return self.data.get("filter_cleaning")

    @property
    def filter_replacement(self) -> Optional[bool]:
        return self.data.get("filter_replacement")

    @property
    def filter_life(self) -> Optional[int]:
        return self.data.get("filter_life")

    @property
    def light_sensor(self) -> Optional[bool]:
        return self.data.get("light_sensor")

    @property
    def particulate_sensor(self) -> Optional[int]:
        return self.data.get("particulate_sensor")

    @property
    def filter_timer(self) -> Optional[int]:
        return self.data.get("filter_timer")

    @property
    def lights(self) -> Optional[Lights]:
        value = self.data.get("all_light_off")
        return None if value is None else Lights(value)

    @property
    def error(self) -> Optional[Error]:
        value = self.data.get("error")
        return None if value is None else Error(value)

    @property
    def tag_state(self) -> Optional[int]:
        return self.data.get("tag_state")

    @property
    def tag_uid(self) -> Optional[List]:
        return self.data.get("tag_uid")

    @property
    def filter_type(self) -> Optional[FilterType]:
        value = self.data.get("filter_type")
        return None if value is None else FilterType(value)

    @property
    def pm_sensor(self) -> Optional[List]:
        return self.data.get("pm_sensor")

    @property
    def color(self) -> Optional[List]:
        return self.data.get("color")

    @property
    def lsens_ctl(self) -> Optional[bool]:
        return self.data.get("lsens_ctl")

    @property
    def filter_ctl(self) -> Optional[bool]:
        return self.data.get("filter_ctl")

    @property
    def buzzer(self) -> Optional[bool]:
        return self.data.get("buzzer")

    @property
    def gas(self) -> Optional[Gas]:
        value = self.data.get("gas")
        return None if value is None else Gas(value)

    @property
    def lock(self) -> Optional[bool]:
        return self.data.get("lock")

    @property
    def open(self) -> Optional[bool]:
        return self.data.get("open")

    @property
    def timer_mode(self) -> Optional[TimerMode]:
        value = self.data.get("timer_mode")
        return None if value is None else TimerMode(value)

    @property
    def timer(self) -> Optional[int]:
        return self.data.get("timer")

    @property
    def schedule(self) -> Optional[str]:
        return self.data.get("schedule")

    @property
    def rssi(self) -> Optional[int]:
        return self.data.get("rssi")

    @property
    def v(self) -> Optional[str]:
        return self.data.get("v")
