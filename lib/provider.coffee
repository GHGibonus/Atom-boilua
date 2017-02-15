{currentFile, isaacmodLoc} = require './modutils'

customSnippets = [
    {
        snippet: 'local ${1:player} = Isaac.GetPlayer(0)${2:}',
        rightLabel: 'local player = Isaac.GetPlayer(0)',
        displayText: 'setplayer',
        type: 'snippet'
    }, {
        snippet: '''for i, entity in ipairs(Isaac.GetRoomEntities()) do
        \t${1:-- manipulate entity}
        end''',
        rightLabel: 'for i, ent in ipairs(Isaac.GetRoomEntities())',
        displayText: 'forentityroom',
        type: 'snippet'
    }
]

module.exports = provider =
    suggestionPriority: 100
    inclusionPriority: 2
    selector: '.source.lua'
    disableForSelector: '.source.lua .comment'

    #returns a subset of 'customSnippets' which starts with 'prefix'
    #read 'resolve()' as 'return'
    getSuggestions: ({editor, bufferPosition, scopeDescriptor, prefix}) ->
        new Promise((resolve) ->
            modPath = isaacmodLoc()
            edPath = currentFile()
            if edPath.startsWith(modPath)
                resolve(customSnippets.filter((snippetName) ->
                    if snippetName.displayText.startsWith(prefix)
                        snippetName.replacementPrefix = prefix
                        return true
                    else
                        return false
                ))
        )
