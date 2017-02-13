GameLauncher = require './game_launcher'

local = undefined

module.exports =
    launch_isaac : () ->
        local = new GameLauncher()
        null
