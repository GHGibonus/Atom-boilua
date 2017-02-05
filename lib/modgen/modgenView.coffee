{TextEditor} = require 'atom'

{View, TextEditorView} = require 'atom-space-pen-views'

ModgenModel = require './modgenModel'

module.exports = class ModgenView extends View
    @content: (model, entryList) =>
        return @_genLayout(model, entryList)

    @_genLayout: (model, spanList) =>
        @div class: 'boilua-mod-creator', () =>
            @_title(model.cur_mod_name)
            @_modnameInput(model.name_buffer)
            @_genButton(key, value) for key, value of spanList
            @_confirmButton()

    @_title: (title) =>
        return @div class: 'modgen-entry', () =>
            @h1 class: 'modgen-title', id: 'title', 'Modifying ' + title

    @_modnameInput: (modnameBuffer) ->
        modnameEditor = new TextEditor(
            mini: true
            buffer: modnameBuffer
            placeholderText: 'Your mod\'s name'
            text: 'modname'
        )
        modnameEditor.selectAll()
        return @div id: 'name-editor', class: 'modgen-entry', () =>
            @div 'Mod name:'
            @subview 'modnameEditor',
                     new TextEditorView(editor: modnameEditor)

    @_genButton: (entryName, entryPurpose) =>
        title = 'Has custom ' + entryName
        return @div class: 'modgen-entry', () =>
            @div class: 'checkbox', () =>
                @label for: entryName, () =>
                    @input id: entryName,
                           id: entryName,
                           class: 'input-checkbox',
                           type: 'checkbox'
                    @div class: 'setting-title', title
                @section class: 'setting-description', () =>
                    @div class: 'setting-entry',
                        'Creates the following xml files in content: ' \
                         + @_prettyFileInfo(entryPurpose.requires),
                    @div class: 'setting-entry',
                         if entryPurpose.resourceFolders? then \
                          'Creates the following folders in resources: ' \
                           + @_prettyFileInfo(entryPurpose.resourceFolders)
                         else ''

    @_confirmButton: () ->
        return @div class: 'modgen-entry modgen-buttons', () =>
            @button class: 'btn', id: 'generate-file', 'generate files'
            @button class: 'btn', id: 'cancel', 'cancel'

    @_prettyFileInfo: (fileList) ->
        ret = fileList[0]
        for entry in fileList[1..]
            ret += ', ' + entry
        return ret
