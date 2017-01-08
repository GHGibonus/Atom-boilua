## **Atom-boilua**
==

An Atom package to improve your Binding of Isaac modding experience.


# **Contents**
- [Description](#description)
- [Configuration](#configuration)
- [Inner Workings](#inner workings)
- [License](#license)

# **Description**
Atom-boilua is a package for the text editor [Atom](https://atom.io/) enabling autocompleting for the Lua modding API introduced in the Binding of Isaac: Rebirth dlc Afterbirth+.

The core documentation scraping functionality (specifically the regex patters) is based on Kapiainen's Sublime plug-in [The Subliming of Isaac](https://github.com/Kapiainen/The-Subliming-Of-Isaac).

# **Configuration**
This package requires the atom-lua-autocomplete package to work properly, it uses its handy .luacompleterc config file to interface cleanly with the autocomplete-plus suggestion provider.

Please look into the package's settings to configure your installation

# **Inner Workings**
The package creates a .luacompleterc file in your `binding of isaac afterbirth+ mod` folder, which the atom-lua-autocomplete package will use to provide you with proper mod API suggestions.

To create the .luacompleterc file, atom-boilua first checks in your Steam BoI:Rebirth file if the lua api doc is more recent than the .luacompleterc file in your `binding of isaac afterbirth+ mod` when you open a file in the modding folder. If it is the case, it will update your .luacompleterc, otherwise it does nothing.


# **License**
See [**LICENSE.md**](LICENSE.md) for more information.
