# QuReed GUI

This repository contains the code for QuReed GUI. Qureed contains only the 'business logic'.

Depencencies:
	- QuReed GUI relies on the QuReedGUIServer, which is essential for the communication between the GUI and the project runtime. It is responsible for separating the GUI runtime and the project runtime. This prevents the runtime pollution.


## Installation

If using windows, I recommend using Anaconda for venv management (see Caveats). In Linux/MacOs use your preffered venv manager.

After the venv was created and activated simply run:

```bash
pip install "git+ssh://git@github.com/tqsd/QuReedGui.git@strip"
```

## Usage

To create a new project run:
```bash
qureed create-project <NAME>
```
This will create a new project with the given name and folder structure.

To start the gui, move to the root of the new project and then run:
```bash
qureed run
```

### Creating Schemes

When creating the project with the `qureed create-project` utility, the default scheme `main.json` is already created. If more schemes are needed you can create them manually in the root of the project `<scheme-name>.json`. Newly created file must contain valid json scheme, so you must populate the new file with `{}`. Gui application must be reloaded in order to see the new empty scheme.

### Adding custom icons
QuReed already ships with built-in icons. If more icons are needed, you can simply add them to the `<project-name>/custom/icons` folder. Builtin utility for adding the icons is not working in the browser mode.

### Creating new devices
QuReed already ships with built-in devices. If more devices are neede, you can use the Gui to create the device. When the dialog is opened you must choose a name, icon, ports (optional) and parameters (optional).

When specifying the ports you define what kind of data you intend to receive at the port (input case) and what kind of data you intend produce (output case).

When defining parameters (settings) you can define a value which is set once per simulation. Every device has a default parameters `name`.

Logic of the device needs to be defined in the method `des(self, time, *args, **kwargs)`. In order for the logic to work the method must be decorated with the `schedule_next_event` decorator. The outcome must be passed from the method in a list of tuples, specifying the output port, signal (containing the data) and time. [See the example](https://github.com/tqsd/QuReed/blob/standardization/qureed/devices/beam_splitters/ideal_beam_splitter.py).

### Logging the data in the simulation
You can use three different logging methods implemented in the [`GenericDevice`](https://github.com/tqsd/QuReed/blob/standardization/qureed/devices/generic_device.py) class.
1. `log_message`: Simly logs the given string as the message.
2. `log_state`: Logs the state, you can pass in the message as well as the state.
3. `log_plot`: Logs the message and the figure `matplotlib.Figure` as well as the figure name, which is used to save the logged figure.

### Assembling the simulation
The simulation can be assembled by opening a scheme and adding the devices and then connecting the ports which are of the same type or type of one port is inherits from the type of the other port.
The device instances can be created by dragging the devices from the file explorer tab or by pressing the `+` icon and then pressing the correct device name. You can create more devices, when you press on the device the correct instance is created, but the dialog does not close by default and you can create multiple devices. The devices might be created under the dialog so you might not see anything when pressing the device name, but they appear after you have closed the dialog.

### Variables
Some 'devices' can encode some value, this can be set by clicking on the device icon on the scheme and then setting the value in the top right corner. The value is then displayed in the device icon.
In the same way you can set another predefined property (setting) for one device.

### Saving the Scheme
The scheme can be saved when by pressing file menu and then selecting 'save scheme'. Schemes are not saved automatically. Before running the simulation or exiting you need to manually save the schemes.

### Running the simulation
In order to run the simulation, open the simulation tab, select the scheme and the duration of the simulation. The simulation will end when there is no next event scheduled or if the time exceeds the selected duration. All of the logs will display in bellow the tab.

## Caveats

When running the app for the first time it takes some time to compile the flet libraries.

On windows if using conda make sure to use the python supported by conda, you might need to explicitly state the version:
```bash
conda create -n qureed_env python=3.12 -y
conda activate qureed_env
```
(At the moment of writing Python 3.13 is not supported by Anaconda)

Icon uploads are not yet supported in the web app. To use custom icons, move the images to the
`<NAME>/custom/icons?` folder.

# Notes

1. QuReed is in the process of development, so changes can occur in the process.
2. [PhotonWeave](https://photon-weave.readthedocs.io/en/master/) is the preffered quantum simulation engine and comes preinstalled, implemented devices already use this backend. It is advised that this backend be used for custom devices aswell.

