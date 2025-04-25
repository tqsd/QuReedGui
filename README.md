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

## Caveats

When running the app for the first time it takes some time to compile the flet libraries

On windows if using conda make sure to use the python supported by conda, you might need to explicitly state the version:
```bash
conda create -n qureed_env python=3.12 -y
conda activate qureed_env
```
(At the moment of writing Python 3.13 is not supported by Anaconda)

Icon uploads are not yet supported in the web app. To use custom icons, move the images to the
`<NAME>/custom/icons?` folder.


