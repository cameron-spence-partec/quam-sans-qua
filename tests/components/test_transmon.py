import pytest
from dataclasses import dataclass
from copy import deepcopy
from quam_components.components import *


def test_basic_transmon():
    transmon = Transmon(id=1)
    assert transmon.name == "q1"
    assert transmon.id == 1
    assert transmon.frequency is None
    assert transmon.xy is None
    assert transmon.z is None

    transmon.id = "Q1"
    assert transmon.name == "Q1"


def test_transmon_xy():
    transmon = Transmon(
        id=1,
        xy=IQChannel(
            mixer=Mixer(
                id=1,
                port_I=1,
                port_Q=2,
                frequency_drive=5e9,
                local_oscillator=LocalOscillator(),
            )
        ),
    )

    assert transmon.xy.name == "q1_xy"
    assert transmon.xy.mixer.name == "mixer1"
    assert not transmon.xy.pulses
    assert transmon.frequency == None
    assert transmon.xy.mixer.frequency_drive == 5e9
    assert transmon.z is None

    config = {"elements": {}}
    with pytest.raises(TypeError):
        transmon.xy.apply_to_config(config)

    transmon.xy.mixer.local_oscillator.frequency = 4.6e9

    transmon.xy.apply_to_config(config)
    assert config == {
        "elements": {
            "q1_xy": {
                "mixInputs": {
                    "I": ("con1", 1),
                    "Q": ("con1", 2),
                    "lo_frequency": 4600000000.0,
                    "mixer": "mixer1",
                },
                "intermediate_frequency": 400e6,
                "operations": {},
            },
        }
    }


def test_transmon_add_pulse():
    transmon = Transmon(
        id=1,
        xy=IQChannel(
            mixer=Mixer(
                id=1,
                port_I=1,
                port_Q=2,
                frequency_drive=5e9,
                local_oscillator=LocalOscillator(frequency=4.6e9),
            )
        ),
    )
    transmon.xy.pulses["X180"] = pulses.DragPulse(
        amplitude=1, sigma=4, alpha=2, anharmonicity=200e6, length=20, rotation_angle=0
    )

    quam_dict = transmon.to_dict()
    assert quam_dict == {
        "id": 1,
        "xy": {
            "mixer": {
                "id": 1,
                "local_oscillator": {"frequency": 4600000000.0},
                "port_I": 1,
                "port_Q": 2,
                "frequency_drive": 5000000000.0,
            },
            "pulses": {
                "X180": {
                    "__class__": "quam_components.components.pulses.DragPulse",
                    "amplitude": 1,
                    "sigma": 4,
                    "alpha": 2,
                    "anharmonicity": 200000000.0,
                    "rotation_angle": 0.0,
                    "length": 20,
                }
            },
        },
    }

    config = {"elements": {}, "pulses": {}, "waveforms": {}}
    transmon.xy.apply_to_config(config)

    assert config["elements"] == {
        "q1_xy": {
            "mixInputs": {
                "I": ("con1", 1),
                "Q": ("con1", 2),
                "lo_frequency": 4600000000.0,
                "mixer": "mixer1",
            },
            "intermediate_frequency": 400e6,
            "operations": {"X180": "q1_xy_X180_pulse"},
        },
    }

    assert config["pulses"] == {
        "q1_xy_X180_pulse": {
            "operation": "control",
            "length": 20,
            "waveforms": {"I": "q1_xy_X180_wf_I", "Q": "q1_xy_X180_wf_Q"},
        }
    }

    from qualang_tools.config.waveform_tools import drag_gaussian_pulse_waveforms

    I, Q = drag_gaussian_pulse_waveforms(
        amplitude=1, sigma=4, alpha=2, anharmonicity=200e6, length=20
    )

    assert list(config["waveforms"]) == ["q1_xy_X180_wf_I", "q1_xy_X180_wf_Q"]
    assert config["waveforms"]["q1_xy_X180_wf_I"] == {"type": "arbitrary", "sample": I}
    assert config["waveforms"]["q1_xy_X180_wf_Q"] == {"type": "arbitrary", "sample": Q}


@dataclass
class QuamTestSingle(QuamRoot):
    qubit: Transmon


quam_dict_single = {
    "qubit": {
        "id": 0,
        # "xy": {
        #     "pi_amp": 10e-3,
        #     "pi_length": 40,
        #     "anharmonicity": 200e6,
        # }
    },
}

quam_dict_single_nested = {
    "qubit": {
        "id": 0,
        "xy": {
            "pi_amp": 10e-3,
            "pi_length": 40,
            "anharmonicity": 200e6,
        },
    },
}


def test_instantiation_single_element():
    quam = QuamTestSingle.load(quam_dict_single)

    assert isinstance(quam.qubit, Transmon)
    assert quam.qubit.id == 0
    assert quam.qubit.xy is None

    assert quam.qubit._quam is quam


def test_instantiation_single_nested_element():
    with pytest.raises(AttributeError):
        quam = QuamTestSingle.load(quam_dict_single_nested)

    quam_dict = deepcopy(quam_dict_single_nested)
    quam_dict["qubit"]["xy"]["mixer"] = {
        "id": 0,
        "port_I": 0,
        "port_Q": 1,
        "frequency_drive": 5e9,
        "local_oscillator": {"power": 10, "frequency": 6e9},
    }
    quam = QuamTestSingle.load(quam_dict)

    assert quam.qubit.xy.mixer.id == 0
    assert quam.qubit.xy.mixer.name == "mixer0"
    assert quam.qubit.xy.mixer.local_oscillator.power == 10
    assert quam.qubit.xy.mixer.local_oscillator.frequency == 6e9

    assert quam.qubit._quam is quam
    assert quam.qubit.xy._quam is quam
    assert quam.qubit.xy.mixer._quam is quam


def test_instantiate_quam_dict():
    @dataclass
    class QuamTest(QuamRoot):
        qubit: Transmon
        wiring: dict

    quam_dict = deepcopy(quam_dict_single_nested)
    quam_dict["qubit"]["xy"]["mixer"] = {
        "id": 0,
        "port_I": ":wiring.port_I",
        "port_Q": ":wiring.port_Q",
        "frequency_drive": 5e9,
        "local_oscillator": {"power": 10, "frequency": 6e9},
    }
    quam_dict["wiring"] = {
        "port_I": 0,
        "port_Q": 1,
    }
    QuamTest.load(quam_dict)