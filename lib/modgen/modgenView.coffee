{View} = require 'atom-space-pen-views'

module.exports = class ModgenView extends View
    @content: () ->
        @div =>
            @h1 'Spacecraft'
            @ol =>
                @li 'Apollo'
                @li 'Soyuz'
                @li 'Space Shuttle'
