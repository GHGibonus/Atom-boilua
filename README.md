# **Atom-boilua**
==

An Atom package to improve your Binding of Isaac modding experience.


## **Contents**
- [Description](#description)
- [Installation](#installation)
- [License](#license)


## **Description**
Atom-boilua is a package for the text editor [Atom](https://atom.io/) enabling autocompletion for the Lua modding API introduced in the Binding of Isaac: Rebirth dlc Afterbirth+.

The core documentation scraping functionality (specifically the regex paterns) is based on Kapiainen's Sublime plug-in [The Subliming of Isaac](https://github.com/Kapiainen/The-Subliming-Of-Isaac).

All the code has been refactored to adhere to a more readable standard and to improve the life of people who want to contribute or fork this package for other purposes. Note that however the two code-bases might look completly different, most of the scraper codes are stricly identical in logic.


## **Installation**

### **Requirements**
- A Python3.5 or higher interpreter avaliable on the system.
- The autocomplete-lua and language-lua packages.
- The game that this package is supposed to help you mod!
- The [Atom editor](https://atom.io/)

Aquire all the forementioned software before going to the next section.

### **Download**

`apm install atom-boilua` et voila!

You can also search for `atom-boilua` in the install tab and install it through the UI.

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

When you open a file in the isaac mod folder, atom-boilua will check if it needs to create or update a .luacompleterc by comparing the last modification time of the API documentation and the .luacompleterc file.

It will then scrap the necessary informations from the doc and convert them into data readable by the autocomplete-lua package.

This package uses pylint and MyPy to guarentee quality code and easy maintainability.

## **Improvement leads**
- It is definitely possible to port the Python code to coffee/javascript, and remove the Python dependency. I personally cannot do so, given that I do not have any experience with javascript.
- The package is only tested on Linux, and Windows, however I'm working to make it work on all platforms, so contribute by submitting your bug report!

### **Progress**
`Atom API       [###############] 💯%`

`scraper        [#######################] 💯%`

`completerc gen [###############] 💯%` ← Usability milestone

`Testing        [#####--------------] 25%`

`Time wasted making pretty ascii arts [##########] too much%`

## **License**
See [**LICENSE.md**](LICENSE.md) for more information.
