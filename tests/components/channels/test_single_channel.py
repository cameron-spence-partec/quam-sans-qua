import pytest
from copy import deepcopy

from quam.components import *
from quam.core import quam_dataclass, QuamRoot
from quam.core.qua_config_template import qua_config_template


@pytest.fixture
def bare_cfg():
    return {
        "controllers": {},
        "elements": {},
    }


def test_single_channel_no_name(bare_cfg):
    channel = SingleChannel(opx_output=("con1", 1))

    with pytest.raises(AttributeError):
        channel.apply_to_config(bare_cfg)

    channel.id = "channel"
    channel.apply_to_config(bare_cfg)


def test_single_channel_offset(bare_cfg):
    channel = SingleChannel(id="channel", opx_output=("con1", 1))

    cfg = deepcopy(bare_cfg)
    channel.apply_to_config(cfg)

    expected_cfg = {
        "controllers": {
            "con1": {
                "analog_inputs": {},
                "digital_outputs": {},
                "analog_outputs": {1: {}},
            }
        },
        "elements": {
            "channel": {
                "singleInput": {"port": ("con1", 1)},
                "operations": {},
            }
        },
    }
    assert cfg == expected_cfg

    cfg = deepcopy(bare_cfg)
    channel.opx_output_offset = 0.1
    expected_cfg["controllers"]["con1"]["analog_outputs"][1]["offset"] = 0.1
    channel.apply_to_config(cfg)
    assert cfg == expected_cfg


def test_single_channel_differing_offsets(bare_cfg):
    channel1 = SingleChannel(id="channel", opx_output=("con1", 1))
    channel2 = SingleChannel(id="channel", opx_output=("con1", 1))

    cfg = deepcopy(bare_cfg)
    channel1.apply_to_config(cfg)
    channel2.apply_to_config(cfg)
    assert cfg["controllers"]["con1"]["analog_outputs"][1] == {}

    channel1.opx_output_offset = 0.1

    cfg = deepcopy(bare_cfg)
    channel1.apply_to_config(cfg)
    channel2.apply_to_config(cfg)
    assert cfg["controllers"]["con1"]["analog_outputs"][1] == {"offset": 0.1}

    channel2.opx_output_offset = 0.1

    cfg = deepcopy(bare_cfg)
    channel1.apply_to_config(cfg)
    channel2.apply_to_config(cfg)
    assert cfg["controllers"]["con1"]["analog_outputs"][1] == {"offset": 0.1}

    channel2.opx_output_offset = 0.2

    cfg = deepcopy(bare_cfg)
    channel1.apply_to_config(cfg)
    with pytest.raises(ValueError):
        channel2.apply_to_config(cfg)
    channel2.opx_output_offset = 0.1 + 0.5e-4
    channel2.apply_to_config(cfg)
    assert cfg["controllers"]["con1"]["analog_outputs"][1] == {"offset": 0.1 + 0.5e-4}


def test_single_channel_offset_quam(bare_cfg):
    @quam_dataclass
    class QuamTest(QuamRoot):
        channel: SingleChannel

    channel = SingleChannel(id="channel", opx_output=("con1", 1))
    machine = QuamTest(channel=channel)

    cfg = machine.generate_config()

    expected_cfg = deepcopy(qua_config_template)
    expected_cfg["controllers"] = {
        "con1": {
            "analog_inputs": {},
            "digital_outputs": {},
            "analog_outputs": {1: {"offset": 0.0}},
        }
    }
    expected_cfg["elements"] = {
        "channel": {
            "singleInput": {"port": ("con1", 1)},
            "operations": {},
        }
    }

    assert cfg == expected_cfg

    channel.opx_output_offset = 0.1

    cfg = machine.generate_config()
    expected_cfg["controllers"]["con1"]["analog_outputs"][1]["offset"] = 0.1
    assert cfg == expected_cfg