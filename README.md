# PSICalc Viewer

This is the GUI tree viewing system for the psicalc algorithm. For details on the
algorithm, see the psicalc package: https://pypi.org/project/psicalc/. You can find
prebuilt PSICalc Viewer binaries
[here](https://github.com/jdeweeselab/psicalc-package/releases).

## Building

PSICalc Viewer is supported on macOS, Windows, and Linux. The build system uses
[just](https://github.com/casey/just). It's not required but will make your life easier.

### macOS

_**Note:** To build a DMG, codesign, etc, you'll need to setup a dotenv file. Copy
`.build.env` to `.env` and edit accordingly._

Install the prerequisites via Homebrew:

``` bash
brew install pyenv
brew install pyenv-virtualenv
eval "$(pyenv init -)"

MACOSX_DEPLOYMENT_TARGET=12.5 PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.12.2
```

Optionally, setup a virtualenv:

``` bash
pyenv virtualenv 3.12.2 psicalc-viewer
pyenv local psicalc-viewer
```

The rest:

``` bash
brew install graphviz
brew install just
brew install create-dmg
pip install -r requirements.txt
```

When developing locally you can run the app via `just run` or:

``` bash
PYTHONPATH=src python3 src/ps_app/main.py
```

If you want to use a local version of psicalc:

``` bash
PYTHONPATH=src:../path/to/psicalc-package python3 src/ps_app/main.py
```

To build the app:
``` bash
just build
```

If you need to edit anything in `resources/resources.qrc`, make sure regenerate with:
``` bash
just build-resources
```

To build a DMG:

``` bash
just build-dmg
```

See the `Justfile` for other uses.

### Windows

Install the prerequisites via Chocolatey and winget:

```
choco install pyenv-win
pyenv update
pyenv install 3.12.2
pyenv local 3.12.2
choco install just
choco install graphviz
winget install Microsoft.VisualStudio.2022.BuildTools
```

_**Note:** When running the Visual Studio Installer, you only need to select "Desktop
development with C++". This is a requirement for PyGraphviz._

Optionally, setup a virtualenv:

```
python -m venv venv
.\venv\Scripts\activate
```

The rest:
```
pip install --use-pep517 --config-settings="--global-option=build_ext" --config-settings="--global-option=-IC:\Program Files\Graphviz\include" --config-settings="--global-option=-LC:\Program Files\Graphviz\lib" pygraphviz
pip install -r requirements.txt
```

When developing locally you can run the app via `just run` or:

```
$env:PYTHONPATH = "src"; python .\src\ps_app\main.py
```

If you want to use a local version of psicalc:

```
$env:PYTHONPATH = "src;..\psicalc-package\src"; python .\src\ps_app\main.py
```

To build an exe:
```
just build
```

If you need to edit anything in `resources/resources.qrc`, make sure regenerate with:
```
just build-resources
```

See the `Justfile` for other uses.

Installer is created with [InstallForge](https://installforge.net/). Use
`packaging/psicalc-windows.ifp` to start.

### Linux

These instructions assume an APT based system. Adjust as needed.

Install the prerequisites:

``` bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
eval "$(pyenv init -)"

pyenv install 3.12.2
```

Optionally, setup a virtualenv:

``` bash
pyenv virtualenv 3.12.2 psicalc-viewer
pyenv local psicalc-viewer
```

The rest:

``` bash
sudo apt install graphviz
sudo apt install just
# make linuxdeploy executable and move into your $PATH
wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
pip install -r requirements.txt
```

When developing locally you can run the app via `just run` or:

``` bash
PYTHONPATH=src python3 src/ps_app/main.py
```

If you want to use a local version of psicalc:

``` bash
PYTHONPATH=src:../path/to/psicalc-package python3 src/ps_app/main.py
```

There is an odd issue with PyInstaller and GraphViz currently. In
`_pyinstaller_hooks_contrib/hooks/stdhooks/hook-pygraphviz.py`, you need to replace:

``` python
graphviz_bindir = os.path.dirname(os.path.realpath(shutil.which("dot")))
```

with:

``` python
graphviz_bindir = os.path.dirname(shutil.which("dot"))
```

and ensure the GraphViz path is right in `packaging/psicalc-linux.spec`.

To build the app:

``` bash
just build
```

If you need to edit anything in `resources/resources.qrc`, make sure regenerate with:
``` bash
just build-resources
```

To build an AppImage:

``` bash
just build-appimage
```

See the `Justfile` for other uses.
