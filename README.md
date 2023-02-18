# PSICalc Viewer 

This is the GUI tree viewing system for the psicalc algorithm. For details on the algorithm, see the psicalc package: https://pypi.org/project/psicalc/ 

### Instructions for building:

This program uses the [fman build system](https://build-system.fman.io/) to compile targets for macOS, Windows, and Linux operating systems. 
In order to address the pain points associated with compiling python applicatons, the build system utilizes a combination of Qt and PyInstaller to 
build for the desired target. 

### Setup

Fman build system requires python 3.6, so you need to switch to that version if you don't have it already:
```
brew install pyenv
PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.6-dev
pyenv local 3.6-dev
eval "$(pyenv init -)"
```

Create a virtual environment within the psi-calc directory root and activate it:
```
pyenv virtualenv <python-version> <env-name>
pyenv activate <env-name>
```

Add the following to your ~/.zshrc and ~/.bashrc
```
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Install python dependencies:
```
pip install -r requirements.txt
```
Install graphviz binaries from source:
[Graphviz Installation instructions](https://github.com/mandosoft/psi-calc/wiki/Graphviz-Installation)

From there, run a test build using ```fbs run```

Freeze the application with ```fbs freeze``` and create the installer .dmg with ```fbs installer```

###Troubleshooting

####Virtual Environment Setup
A common occurrence is for the 3.6-dev virtual environment creation to stop working due to 
too many symbolic links. This can be fixed by completely uninstalling pyenv:

```
rm -rf $(pyenv root)
brew uninstall pyenv
```
