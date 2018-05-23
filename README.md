# Standalone Asset Manager for Google Earth Engine
###### *Made with kivy framework*
#### It's main purpose is to perform some task over many assets, like delete or share.

## How to run it

### Install dependencies
1. [Kivy](https://kivy.org/docs/installation/installation.html)
2. [Google Earth Engine Python API](https://developers.google.com/earth-engine/python_install)

*Tested only in Linux Mint 18 MATE (more coming..)*

### Download source code 
######*(not binaries yet)*
If you have [git](https://git-scm.com/) do:

> git clone https://github.com/fitoprincipe/AssetManagerKV

If you have not git and don't want to install it, download from [github](https://github.com/fitoprincipe/AssetManagerKV)

### Execute

- Open a terminal (in Windows a *prompt* or *cmd*)
- Navigate to the source code folder
- Write:

> python main.py

## Some aspects

### Colors

- **Folders** are blue
- **ImageCollection** are green
- **Image** are red

The header color is random

### Others
- Refresh button don't work yet
- When you delete or share several assets it seems like it hungs, and may hang, but usually does not hang