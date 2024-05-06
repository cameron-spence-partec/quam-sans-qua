# QuAM: Quantum Abstract Machine

## Overview
QuAM (Quantum Abstract Machine) is an innovative software framework designed to provide an abstraction layer over the QUA programming language, facilitating a more intuitive interaction with quantum computing platforms. Aimed primarily at physicists and researchers, QuAM allows users to think and operate in terms of qubits and quantum operations rather than the underlying hardware specifics.

Explore detailed documentation and get started with QuAM here: [QuAM Documentation](ENTER_URL_HERE).
<!-- TODO -->

## Key Features
- **Abstraction Layer**: Simplifies quantum programming by providing higher-level abstractions for qubit operations.
- **Component-Based Structure**: Utilize modular components like Mixers and IQChannels for flexible quantum circuit design.
- **Automated Configuration**: Generate QUA configurations from QuAM setups seamlessly.
- **Extensibility**: Extend QuAM with custom classes to handle complex quantum computing scenarios.
- **State Management**: Features robust tools for saving and loading your quantum states, promoting reproducibility and consistency.

## Installation
To install QuAM, follow these simple steps:

1. Ensure you have Python ≥ 3.8 installed on your system.
2. Clone the repository:
   ```bash
   git clone https://github.com/qua-platform/quam.git
   ```
3. Navigate to the cloned directory and install the required dependencies:
   ```bash
   cd quam
   pip install .
   ```

## Quick Start
Here’s a basic example to get you started with QuAM:

```python
from quam.components import BasicQuAM, SingleChannel, pulses

# Create a root-level QuAM instance
machine = BasicQuAM()

# Add an OPX output channel
channel = SingleChannel(opx_output=("con1", 1))
machine.channels["output"] = channel

# Add a Gaussian pulse to the channel
channel.operations["gaussian"] = pulses.Gaussian(
    length=100,  # Pulse length in ns
    amplitude=0.5,  # Peak amplitude of Gaussian pulse
    sigma=20,  # Standard deviation of Guassian pulse
)

# Play the Gaussian pulse on the channel within a QUA program
with program() as prog:
    channel.play("gaussian")

# Generate the QUA configuration from QuAM
qua_configuration = machine.generate_config()
```


## License
QuAM is released under the BSD-3 License. See the LICENSE file for more details.
