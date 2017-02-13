path = require 'path'

{BufferedProcess} = require 'atom'

IsaacLogObserver = require './isaac_log_observer'

module.exports = class GameLauncher
    constructor: () ->
        @subcommands = []
        @runAdditionalCmds()
        @launchGame()

    # Run additional commands set by the user.
    # parses the input into a list of plain text commands and then separates
    # command and arguments, then launches them into a subshell.
    runAdditionalCmds: () ->
        cmdList = atom.config.get('Atom-boilua.additionalCommands'\
                                 ).split(/\s*;\s*/)
        for i, cmd of cmdList
            if cmd == '' then continue
            toExec = ''
            inQuote = false
            for char in cmd
                if char in '\'"`'
                    inQuote = not inQuote
                else if char == ' ' and inQuote
                    toExec += '__SPACE__'
                else
                    toExec += char
            toExec = toExec.replace(/\\ /g, '__SPACE__')
            splitCmd = toExec.split(/\s+/)
            splitCmd = (arg.replace(/__SPACE__/g, ' ') for arg in splitCmd)
            @subcommands[i] = new BufferedProcess({
                command: splitCmd[0],
                args: splitCmd[1..]
            })
        null

    # Runs the game, and setup the log reader
    launchGame: () =>
        command = atom.config.get('Atom-boilua.isaacStartCommand').split(' ')
        args = command[1..]
        cmd = command[0]
        @boiProc = new BufferedProcess({
            command: cmd,
            args: args,
            exit: @postGame
        })
        window.setTimeout(@launchLogReader, '2000')

    launchLogReader: () =>
        @logreader = new IsaacLogObserver()

    killGame: () =>
        @logreader = null
        @boiProc.kill()

    # called when the process terminates
    postGame: () ->
        no
