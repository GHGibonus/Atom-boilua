fs = require 'fs'
path = require 'path'

{isaacmodLoc} = require '../modutils'
LogObserver = require './log_observer'
{focusError} = require './isaac_error_handling'
# 1. mod in which the syntax error lies
# 2. file in which the syntax error lies
# 3. line where the parser failed
# 4. error message
syntaxErrorsPattern =\
/^\[INFO\] - ERR:.*\+ [mM]ods\/([\w ]+)\/([\w. \/]+):([\d]+):(.*)$/

# 1. mod name
# 2. In which call the error occured
# 3. The folder name of the mod
# 4. the file in which the error occured
# 5. the line number where the issue occured
# 6. additional error message.
runtimeErrorsPattern =\
/^\[INFO\] - \[([\w ]+)\] Error in \"([\w ]+)\" call:.*\+ [mM]ods\/([\w ]+)\/([\w. \/]+):([\d]+):(.*)$/


# Calls callback when fileToWatch is saved uppon (but only once)
callWhenSaved = (fileToWatch, callback) ->
    atom.workspace.observeTextEditors((editor) ->
        dispose = editor.onDidSave(() ->
            curPath = editor.getPath()
            if curPath == fileToWatch
                callback()
                dispose.dispose()
        )
    )
    null

module.exports = class IsaacLogObserver extends LogObserver
    constructor: () ->
        logFile = path.resolve(isaacmodLoc(),
                               '../binding of isaac afterbirth+/log.txt')
        super(logFile)
        @addRegexListener(syntaxErrorsPattern, @handleSyntaxErrors)
        @addRegexListener(runtimeErrorsPattern, @handleRuntimeErrors)
        return this.constructor

    # If the user has a file in modName open, does the following:
    # Move cursor to the incrimined line, highlights it, show error message
    # otherwise, indicates where the issue lied in a popup message.
    handleSyntaxErrors: (matchArray) ->
        modFolder = matchArray[1]
        faultyFile = matchArray[2]
        faultyLine = Number(matchArray[3])
        errorMessage = matchArray[4]
        focusError(modFolder, faultyFile, faultyLine, errorMessage)
        null

    # Same as above, but for runtime errors.
    # Additionally, will prevent any more callbacks from being made.
    # This will be canceled once the user saves a modifyed version of the
    # file in which the error occured.
    # Note: there is a delay between the moment the file is saved and the
    # listener is unmuted. This should give the time to the user to reload
    # the mod in-game using `luamod` and typing real fast
    # Some callbacks do not generate infinite errors, so we don't use that
    # behaviors under certain circumstances
    handleRuntimeErrors: (matchArray) =>
        @mute()
        callback = matchArray[2]
        modFolder = matchArray[3]
        faultyFile = matchArray[4]
        faultyLine = Number(matchArray[5])
        errorMessage = matchArray[6]
        fileToWatch = path.join(isaacmodLoc(), modFolder, faultyFile)
        if callback in ['PostUseItem', 'PostUsePill', 'PostUseCard']
            @unmute()
        else
            callWhenSaved(fileToWatch, () => window.setTimeout(@unmute, 7000))
        focusError(modFolder, faultyFile, faultyLine,
                   'error in callback ' + callback + ': ' + errorMessage)
        null
