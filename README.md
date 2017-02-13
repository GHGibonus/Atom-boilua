# **Atom-boilua**
==

An Atom package to improve your Binding of Isaac modding experience.


## **Contents**
- [Description](#Description)
- [Installation](#Installation)
- [Patch notes](#Patch)
- [Suggesting improvements](#Suggesting)
- [Licenses](#Licenses)


## **Description**
[Atom-boilua](https://github.com/GHGibonus/Atom-boilua) is a package for the text editor [Atom](https://atom.io/) enabling autocompletion for the Lua modding API introduced in the Binding of Isaac: Rebirth dlc Afterbirth+.

The core documentation scraping functionality (specifically the regex patterns) is based on Kapiainen's Sublime plug-in [The Subliming of Isaac](https://github.com/Kapiainen/The-Subliming-Of-Isaac).

All the code has been refactored to adhere to a more readable standard.

### **Features**
 - Smart, type-based autocompletion.
 - Transparent (Runs automatically when an update of the doc or the package is detected).
 - In-editor description of the functions (well, as documented as the API can get)
 - Quality of life features, such as the deletion of the `update.it` file or the addition of very commonly used snippets.
 - Automatic template mod generation with an UI! (right click and select 'Create new BoI mod' or search `open mod creator` in the command palette)
 - IDE-like features, such as an hotkey to launch the game, in addition to customizable extra commands. When an error is found in the log file when running the game, it will also automatically focus Atom and highlight the line where the error occurred.

![Documentation scraping functionality](https://raw.githubusercontent.com/GHGibonus/Atom-boilua/master/resources/demo_doc.png)

![Mod template creation functionality](https://raw.githubusercontent.com/GHGibonus/Atom-boilua/master/resources/demo_mod_creation.png)

![Smart typing & documentation link](https://raw.githubusercontent.com/GHGibonus/Atom-boilua/master/resources/demo_newmod.png)


## **Installation**

### **Prerequisites**
- A [Python](https://www.python.org)3.5 or higher interpreter available on the system.

- Note, on **Windows**, Python 3.5 might cause issues, install Python 3.6 instead. On Linux, the most recent version available in your distro should work fine.

- The autocomplete-lua and language-lua packages.

- The game that this package is supposed to help you mod, already installed.

- The [Atom editor](https://atom.io/)

### **Recommended packages**

Those packages are not require to run properly Atom-boilua but they will help you improve your modding experience.
 - [linter](https://atom.io/packages/linter) + [linter-lua](https://atom.io/packages/linter-lua)

    linter-lua provides real-time syntax checking using luac. Currently, Afterbirth+ uses lua 5.3, so make sure to get 5.3 luac binaries!

    This speeds up the debugging process (you'll immediately be notified of your mistake rather than after running your mod and testing it). It also prevents a bug in autocomplete-lua stopping autocompletion suggestions.

   - On Windows, you can download them [here](http://lua-users.org/wiki/LuaBinaries).

   - On Linux, you are better off downloading the source and compiling the binaries for yourself. The sources are [here](https://www.lua.org/ftp/). Just uncompress the archive, go in the target directory and type `make linux`.

   You then need to specify in the linter-lua settings the path to the `luac` executable.

 - [linter-xmllint](https://atom.io/packages/linter-xmllint)

   This helps a lot. Issues in the xml files in isaac will usually crash the game, without a crash log :). Having linter in your xmls won't prevent all the crashes, but it will definitely prevent some simple mistakes that might take hours to fix.

### **Download**

`apm install Atom-boilua` et voilà!

You can also search for `Atom-boilua` in the install tab and install it through the UI.

### **Configuration**
Please look into the package's settings to configure your installation.

Here is what you can find in the settings tab:

| Setting                      | Description                         |
| ---------------------------- | ----------------------------------- |
| Isaac AB+ mod editing folder | The directory in which you edit your mods, by default, it is the Afterbirth+ mod folder. Note that setting this to something different than your mod folder might cause issues with the log reading feature.|
| Isaac Game folder            | The directory in which Rebirth is installed, if you use a custom Steam location, this must be changed.
| Python path                  | The Python executable path, Windows users must specify it |

## **Patch notes**
See the patch notes on Github: https://github.com/GHGibonus/Atom-boilua/releases

## **Suggesting improvements**
All improvement suggestions goes on the issue tracker: https://github.com/GHGibonus/Atom-boilua/issues

## **Licenses**
This package has several components under several different licenses. First off, **at the exception of contrary notice**, the code is licensed under the MIT (Expat) license.

 - The Python scraper code's license is specified in [SCRAPER_LICENSE](#lib/scraper/SCRAPER_LICENSE)
 - The template xml files that the user might use in a mod that they distribute on any platform is under an even more permissive license (a derivative of the WTFPL). No restriction is given on redistributing/modifying/selling/claiming as your own (not even including copyright notices). See [TEMPLATES_LICENSE](#templates/TEMPLATES_LICENSE) for more informations.
 - Every other code in this repository reposes on [LICENSE](#lib/LICENSE). This is an MIT license, the difference with the SCRAPER_LICENSE being the copyright attribution.
