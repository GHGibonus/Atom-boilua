# **Atom-boilua**
==

An Atom package to improve your Binding of Isaac modding experience.


## **Contents**
- [Description](#description)
- [Installation](#installation)
- [Patch notes](#Patch notes)
- [License](#license)


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
| Isaac AB+ mod editing folder | The directory in which you edit your mods, by default, it is the Afterbirth+ mod folder. |
| Isaac Game folder            | The directory in which Rebirth is installed, if you use a custom Steam location, this must be changed.
| Python path                  | The Python executable path, Windows users must specify it |

## **Inner Workings**
The package creates a .luacompleterc file in your `binding of isaac afterbirth+ mod` folder, which the autocomplete-lua package will use to provide you with proper mod API suggestions.

When you open a file in the isaac mod folder, Atom-boilua will check if it needs to create or update a .luacompleterc by comparing the last modification time of the API documentation and the .luacompleterc file.

It will then scrap the necessary informations from the doc and convert them into data readable by the autocomplete-lua package.

If the package successfully create the luacompleterc file, it will notify you with a blue pop-up. If the blue pop-up didn't appear when you expected to, right click on your file and click `Rebuild BoI API` in the context menu. It should then work, or break, if it breaks report the issue.


## **Patch notes**

See the patch notes on Github: https://github.com/GHGibonus/Atom-boilua/releases

## **License**
See [**LICENSE.md**](LICENSE.md) for more information.
