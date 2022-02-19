import pytest
from rabbitair import Model, Quality, State


def test_state_invalid_value() -> None:
    state = State({"mode": 10})
    assert repr(state)
    with pytest.raises(ValueError):
        assert state.mode is not None


def test_state_biogs_case() -> None:
    """This case is only defined in the protocol specification, but will never occur in real life."""
    state = State({"model": 2, "quality": 1})
    assert state.model is Model.BioGS
    assert state.quality is Quality.Lowest
