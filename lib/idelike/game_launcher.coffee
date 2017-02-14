path = require 'path'

{BufferedProcess} = require 'atom'

IsaacLogObserver = require './isaac_log_observer'

# Parses the input into a list of plain text commands and then separates
# command and arguments, returns an array of subcommands
parseCmd = (cmdString) ->
    cmdList = cmdString.split(/\s*;\s*/)
    parsedCmdList = []
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
        parsedCmdList[i] = splitCmd
    return parsedCmdList

module.exports = class GameLauncher
    constructor: () ->
        @subcommands = []
        @runAdditionalCmds()
        @launchGame()

    # Run additional commands set by the user.
    runAdditionalCmds: () ->
        toRun = parseCmd(atom.config.get('Atom-boilua.additionalCommands'))
        for i, cmd of toRun
            @subcommands[i] = new BufferedProcess({
                command: cmd[0],
                args: cmd[1..]
            })

    # Runs the game, and setup the log reader
    launchGame: () =>
        toRun = parseCmd(atom.config.get('Atom-boilua.isaacStartCommand'))[0]
        @boiProc = new BufferedProcess({
            command: toRun[0],
            args: toRun[1..],
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
