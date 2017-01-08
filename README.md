# **Atom-boilua**
==

An Atom package to improve your Binding of Isaac modding experience.


## **Contents**
- [Description](#description)
- [Configuration](#configuration)
- [Inner Workings](#inner workings)
- [License](#license)

## **Description**
Atom-boilua is a package for the text editor [Atom](https://atom.io/) enabling autocompletion for the Lua modding API introduced in the Binding of Isaac: Rebirth dlc Afterbirth+.

The core documentation scraping functionality (specifically the regex paterns) is based on Kapiainen's Sublime plug-in [The Subliming of Isaac](https://github.com/Kapiainen/The-Subliming-Of-Isaac).

## **Installation**

# **Requirements**
- Python3 installed on your system.
- The atom-lua-autocomplete Atom package.
- The game that this package is supposed to help you mod!
- The [Atom editor](https://atom.io/)

# **Download**
(currently, this package is under developpement, this will become trivial when the package is released)

**Pre release:**

Open your Atom package folder in a terminal and type `git clone https://github.com/GHGibonus/Atom-boilua.git`
Congratulation, it is now setup correctly!

**post release:**

`apm install atom-boilua` et voila!

You can also search for `atom-boilua` in the install tab and install it through the UI.

# **Configuration**
Please look into the package's settings to configure your installation.

## **Inner Workings**
The package creates a .luacompleterc file in your `binding of isaac afterbirth+ mod` folder, which the atom-lua-autocomplete package will use to provide you with proper mod API suggestions.

To create the .luacompleterc file, atom-boilua first checks in your Steam BoI:Rebirth file if the lua api doc is more recent than the .luacompleterc file in your `binding of isaac afterbirth+ mod` folder when you open a file in the modding folder. If it is the case, it will update your .luacompleterc, otherwise it does nothing.

## **Improvement leads**
- The atom-lua-autocomplete package provides an interface to programmatically feed autocompletion suggestion, it would be wise to use it instead of hardcodding a .luacompleterc file.
- It is definitely possible to port the Python code to coffree/javascript, and remove the python dependency. I personally cannot do so, given that I do not have any experience with javascript.

## **License**
See [**LICENSE.md**](LICENSE.md) for more information.
