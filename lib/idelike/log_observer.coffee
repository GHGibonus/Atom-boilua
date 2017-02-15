fs = require 'fs'

# NOTE: OMG MAKE SURE TO USE THE .close()
# METHOD IF YOU WANT TO DELETE AN INSTANCE OF THIS CLASS!!
# NODE.JS'S FS.WATCH DO NOT FORGET!!!
module.exports = class LogObserver
    # Opens a listener to the given logFile and setups callbacks.
    constructor: (logFile) ->
        @listeners = []
        @deef = true
        @watched = fs.openSync(logFile, 'r')
        @watcher = fs.watch(logFile, {presistent: true}, @_onLogChange)
        @deef = false
        return this.constructor

    # Adds a function to call when regPattern.test(line) is true.
    # The arguments of the function is the return value of regPattern.exec(line)
    addRegexListener: (regPattern, callback) =>
        @listeners.push({pattern: regPattern, callback: callback})

    # Temporarely inhibits any callback from the instance, untill it is told
    # to wake up.
    mute: () =>
        @deef = true

    # Reenables callbacks from this instance
    unmute: () =>
        @deef = false

    # Close the log's file descriptors
    close: () =>
        @watcher.close()
        fs.closeSync(@watched)

    # Invoked every time node's fs.watch detects a change on the observed log.
    # It verifies the change is indeed a 'change' and then it dispatches each
    # line to be treated separately. by _onNewLine
    _onLogChange: (eventType, filename) =>
        if eventType == 'change'
            # Read line AND advances the pointer to the current end of the file
            newBuffer = Buffer.alloc(3000)
            readBytes = fs.readSync(@watched, newBuffer, 0, 3000)
            if readBytes != 0
                newBuffer.toString('UTF-8').split('\n').forEach(@_onNewLine)

    # Invoked at each new line appened to the file. Calls the callback for
    # successful line matches, ONLY IF the logger is not deef.
    _onNewLine: (lineContent) =>
        for pair in @listeners when pair.pattern.test(lineContent)
            unless @deef
                pair.callback(pair.pattern.exec(lineContent))
