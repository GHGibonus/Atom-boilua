'use babel'

const customSnippets = [
  {
    snippet: 'local ${1:player} = Isaac.GetPlayer(0)${2:}',
    rightLabel: 'local player = Isaac.GetPlayer(0)',
    displayText: 'setplayer',
    type: 'snippet'
  }, {
    snippet: 'for i, entity in ipairs(Isaac.GetRoomEntities()) do\n\t${1:-- manipulate entity}\nend',
    rightLabel: 'for i, ent in ipairs(Isaac.GetRoomEntities())',
    displayText: 'forentityroom',
    type: 'snippet'
  }
]

export default class AbpModdingSnippets {
  suggestionPriority = 2;
  selector = '.source.lua';
  disableForSelector = '.source.lua .comment'

  getSuggestions = ({
    editor, bufferPosition, scopeDescriptor, prefix, activatedManually
  }) => {
    var modPath = atom.config.get('Atom-boilua.modPath')
    if (editor.buffer.file.path.startsWith(modPath)) {
      return customSnippets.filter(snippetName => {
        if (snippetName.displayText.startsWith(prefix)) {
          snippetName.replacementPrefix = prefix
          return true
        } else {
          return false
        }
      })
    }
  };
}
