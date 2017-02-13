fs = require 'fs'

module.exports = class LogObserver
    # Opens a listener to the given logFile and setups callbacks.
    constructor: (logFile) ->
        @listeners = []
        @deef = true
        @watched = fs.openSync(logFile, 'r')
        @watcher = fs.watch(logFile, {presistent: true}, @_onLogChange)
        @deef = false
        @cooldown = false
        return this.constructor

    # Add a function to call when regPattern.test(line) is true.
    # The arguments of the function is the return value of regPattern.exec(line)
    addRegexListener: (regPattern, callback) =>
        @listeners.push({pattern: regPattern, callback: callback})

    # Temprarely inhibits any callback from the instance, untill it is told
    # to wake up.
    mute: () =>
        @deef = true

    # Reenables callbacks from this instance
    unmute: () =>
        @deef = false

    # Schedules the unsetting of the cooldown
    _coolup: () =>
        window.setTimeout((() => @cooldown = false), 100)

    # Close the log's file descriptors
    close: () =>
        fs.closeSync(@watcher)
        fs.closeSync(@watched)

    # Listen to modifications to the log file, sorts what is pertinent and
    # what isn't. Then calls _onNewLine with each newly added lines
    # to the watched file
    _onLogChange: (eventType, filename) =>
        if eventType == 'change' and not @cooldown
            # We set a cooldown to avoid calling this too much
            @cooldown = true; @_coolup()

            # Read line AND advances the pointer to the current end of the file
            newBuffer = Buffer.alloc(3000)
            readBytes = fs.readSync(@watched, newBuffer, 0, 3000)
            if readBytes != 0 and not @deef
                newBuffer.toString('UTF-8').split('\n').forEach(@_onNewLine)

    # invoked at each new line appened to the file.
    _onNewLine: (lineContent) =>
        for pair in @listeners when pair.pattern.test(lineContent)
            pair.callback(pair.pattern.exec(lineContent))
