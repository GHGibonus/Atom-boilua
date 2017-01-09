# **Atom-boilua**
==

An Atom package to improve your Binding of Isaac modding experience.


## **Contents**
- [Description](#description)
- [Installation](#installation)
- [Inner Workings](#inner workings)
- [License](#license)


## **Description**
Atom-boilua is a package for the text editor [Atom](https://atom.io/) enabling autocompletion for the Lua modding API introduced in the Binding of Isaac: Rebirth dlc Afterbirth+.

The core documentation scraping functionality (specifically the regex paterns) is based on Kapiainen's Sublime plug-in [The Subliming of Isaac](https://github.com/Kapiainen/The-Subliming-Of-Isaac).


## **Installation**

### **Requirements**
- A Python3 interpreter avaliable on the system.
- The autocomplete-lua and language-lua packages.
- The game that this package is supposed to help you mod!
- The [Atom editor](https://atom.io/)

### **Download**
(currently, this package is under developpement, this will become trivial when the package is released)

**Pre release:**
Open your Atom package folder in a terminal and type `git clone https://github.com/GHGibonus/Atom-boilua.git`
Congratulation, it is now setup correctly!

**post release:**
`apm install atom-boilua` et voila!

You can also search for `atom-boilua` in the install tab and install it through the UI.

### **Configuration**
Please look into the package's settings to configure your installation. If you are under Windows, you probably need to set the Python path. If you use a custom location for your Steam folder, you surely need to update the Isaac path. If you would like to use a different directory than the default one to develop your Afterbirth mods, you need to change the `isaac mod` path.


## **Inner Workings**
The package creates a .luacompleterc file in your `binding of isaac afterbirth+ mod` folder, which the autocomplete-lua package will use to provide you with proper mod API suggestions.

When you open a file in the isaac mod folder, atom-boilua will check if it needs to create or update a .luacompleterc by comparing the last modification time of the API documentation and the .luacompleterc file.

It will then scrap the necessary informations from the doc and convert them into data readable by the autocomplete-lua package.

## **Improvement leads**
- The atom-lua-autocomplete package provides an interface to programmatically feed autocompletion suggestion, it would be wise to use it instead of hardcodding a .luacompleterc file.
- It is definitely possible to port the Python code to coffee/javascript, and remove the Python dependency. I personally cannot do so, given that I do not have any experience with javascript.
- The package is only tested on Linux, however I'm working to make it work on all platforms, so contribute by submitting your bug report!


## **License**
See [**LICENSE.md**](LICENSE.md) for more information.
