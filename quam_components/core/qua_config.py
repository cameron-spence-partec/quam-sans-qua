

qua_config_template = {
    "version": 1,
    "controllers": {
        "con1": {
            "analog_outputs": {},
            "digital_outputs": {},
            "analog_inputs": {},
        }
    },
    "elements": {},
    "pulses": {
        "const_pulse": {
            "operation": "control",
            "length": 1000,
            "waveforms": {"I": "const_wf", "Q": "zero_wf"},
        }
    },
    "waveforms": {
        "zero_wf": {"type": "constant", "sample": 0.0},
        "const_wf": {"type": "constant", "sample": 0.1},
    },
    "digital_waveforms": {
        "ON": {"samples": [(1, 0)]},
    },
    "integration_weights": {},
    "mixers": {}
}


def build_config(quam, qua_config=None):
    from .quam_base import iterate_quam_elements

    if qua_config is None:
        qua_config = qua_config_template.copy()

    for quam_element in iterate_quam_elements(quam):
        quam_element.apply_to_config(qua_config)
        
    return qua_config
