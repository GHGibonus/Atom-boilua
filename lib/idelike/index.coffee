GameHandler = require './game_handler'

module.exports =
    handle_isaac : () ->
        return new GameHandler()
