path = require 'path'

{Range, Point} = require 'atom'

{isaacmodLoc, currentFile, findModDir} = require '../modutils'

# Displays a blinking red line at the given lineNumber in the editor for
# a two seconds.
highlightLine = (lineNumber) ->
    atom.focus()
    editor = atom.workspace.getActiveTextEditor()
    mrange = new Range([lineNumber - 1, 0], [lineNumber, 0])
    marker = editor.markBufferRange(mrange, invalidate: 'never')

    editor.decorateMarker(marker,
                          type: 'line',
                          class: 'error-highlighted-line')
    window.setTimeout((() -> marker.destroy()), 2000)
    null

module.exports =
    # Focus on line lineNumber in file located in mod folder and displays
    # a notification containing errorMessage
    # If the faulty file is the one currently open in the editor, then will
    # immediately jump to lineNumber.
    # If the editor is opened on another file present in the given mod folder
    # it will switch to the faulty file and jump to lineNumber
    # If the editor is opened on a file not present in the given mod folder
    # the editor will give the user the choice to jump to the file.
    focusError: (mod, file, lineNumber, errorMessage) ->
        editorFilePath = currentFile()
        modFolderPath = path.join(isaacmodLoc(), mod)
        faultyFilePath = path.join(modFolderPath, file)
        if editorFilePath.startsWith(modFolderPath)
            atom.notifications.addWarning(errorMessage, dismissable: false)
            if faultyFilePath == editorFilePath
                atom.workspace.getActiveTextEditor().setCursorBufferPosition(
                    new Point(lineNumber - 1, 0)
                )
                highlightLine(lineNumber)
            else
                atom.workspace.open(
                    faultyFilePath,
                    searchAllPanes: true,
                    initialLine: lineNumber - 1
                ).then(() -> highlightLine(lineNumber))
        else
            atom.notifications.addWarning(
                'Error in **' + mod + '**',
                buttons: [{
                    onDidClick: () ->
                        atom.workspace.open(
                            faultyFilePath,
                            searchAllPanes: true,
                            initialLine: lineNumber - 1
                        ).then(() -> highlightLine(lineNumber))
                    ,
                    text: 'jump to file'
                }],
                description: errorMessage,
                dismissable: false
            )
