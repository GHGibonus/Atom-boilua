fs = require 'fs'
path = require 'path'

{TextBuffer} = require 'atom'

{ existsMod, arePresentFiles, copyToFrom, boiluaLoc,
    isaacmodLoc, createFileStruct, createEmptyFile
} = require '../modutils'
ModgenView = require './modgenView'
modTemplates = require './xmlpurposes.json'

module.exports = class ModgenModel
    constructor: (mod_name, data, selfDestructionCallback) ->
        @killYourself = selfDestructionCallback
        @data = data
        @cur_mod_name = mod_name
        # @res_path = atom.config.get('Atom-boilua.resourcePath')
        @name_buffer = new TextBuffer(mod_name)
        @name_buffer.onDidChange(@watchBuffer)

    createView: () =>
        @view = new ModgenView(this, @data)
        @_updateTitle(@cur_mod_name)
        @_updateModState(@cur_mod_name)
        # adds callback to pressing the confirm button
        @view.find('#generate-file')[0].onclick = @watchConfirmButton
        @view.find('#cancel')[0].onclick = @watchCancelButton
        return @view

    takeFocus: () =>
        editor = @view.find('#name-editor')[0].childNodes[1]
        editor.focus()

    close: () =>
        @killYourself()

    getTitle: () ->
        return 'boilua-mod-creator'

    setView: (view) =>
        @view = view

    getView: () =>
        return @view

    _generateFilesFor: (feature) =>
        template_loc = path.join(boiluaLoc(), 'templates')
        content_loc = path.join(isaacmodLoc(), @formatted_mod_name(), 'content')
        resource_loc =path.join(isaacmodLoc(),@formatted_mod_name(),'resources')

        if not fs.existsSync(content_loc)
            fs.mkdirSync(content_loc)

        requires = @data[feature]?.requires || []
        for contentxml in requires
            try
                copyToFrom(path.join(content_loc, contentxml),
                           path.join(template_loc, contentxml))
            catch error
                if error.code != 'EEXIST'
                    throw error

        resourceFolders = @data[feature]?.resourceFolders || []
        for resourceDir in resourceFolders
            createFileStruct(path.join(resource_loc, resourceDir))

        contentsGfxs = @data[feature]?.contentsGfx || []
        for contentgfx in contentsGfxs[0..1]
            if not fs.existsSync(path.join(content_loc, 'gfx'))
                fs.mkdirSync(path.join(content_loc, 'gfx'))
        #     try
        #         copyToFrom(path.join(content_loc, contentgfx),
        #                    path.join(@res_path, contentgfx))
        #     catch error
        #         if error.code != 'EEXIST'
        #             throw error

    watchBuffer: () =>
        modName = @name_buffer.getText()
        @cur_mod_name = modName
        @_updateTitle(modName)
        @_updateModState(modName)

    # Updates the view title, according to the inputed name, and whether
    # it corresponds to an existing mod title.
    _updateTitle: () =>
        title = @view.find("#title")[0]
        if @formatted_mod_name() == ''
            title.textContent = 'Creating a new mod'
        else if existsMod(@formatted_mod_name())
            title.textContent = 'Modifying ' + @cur_mod_name
        else
            title.textContent = 'Creating ' + @cur_mod_name

    # Updates the checkboxes in the view according to the currently existing
    # files in the mod directory.
    # Does nothing if the cur_mod_name doesn't exists.
    _updateModState: () =>
        if not existsMod(@formatted_mod_name())
            return null
        contentFolder =path.join(isaacmodLoc(),@formatted_mod_name(),'content')
        button = {}
        button[label] = @view.find('#'+label)[0] for label, __ of @data
        for label, check of button
            xmls = @data[label].requires
            if arePresentFiles(contentFolder, xmls)
                check.checked = true
            else
                check.checked = false

    # Callback to the `generate files` button.
    watchConfirmButton: () =>
        selectedFeatures = (label for label, __ of @data when \
                                @view.find('#'+label)[0].checked)
        try
            @_createCurrentMod()
        catch error
            if error.message == 'Cannot create a mod with an empty name'
                atom.notifications.addWarning(error.message)
                @killYourself()
                return
            else
                throw error
        for feature in selectedFeatures
            @_generateFilesFor(feature)
        @killYourself()
        @displaySuccess()

    watchCancelButton: () =>
        @killYourself()

    # displays a little windows assessing that the creation of new files
    # was successful.
    displaySuccess: () =>
        if fs.existsSync(path.join(isaacmodLoc(), @formatted_mod_name()))
            atom.notifications.addSuccess(
                'The new **' + @cur_mod_name + '** files were created 👌 💯'
            )

    # Returns the mod name, apt to be used as a directory name for isaac.
    formatted_mod_name: () =>
        return @cur_mod_name.replace(/[ _]/g, '').toLowerCase()

    # Imports a metadata.xml formatted to give isaac a clue about the
    # name the mod author wants to give to their mod.
    _create_metadata: () =>
        metaf = fs.readFileSync(path.join(boiluaLoc(),
                                          'templates/metadata.xml'),
                                encoding: 'UTF-8')
                    .replace(/\$__MOD_NAME__\$/g, @cur_mod_name)
                    .replace(/\$__MOD_LOCATION__\$/g, @formatted_mod_name())
        target = path.join(isaacmodLoc(), @formatted_mod_name(), 'metadata.xml')
        fs.writeFileSync(target, metaf)

    # Creates the directory for the currently selected mod
    _createCurrentMod: () =>
        if @formatted_mod_name() == ''
            throw new Error('Cannot create a mod with an empty name')
        cur_mod_dir = path.join(isaacmodLoc(), @formatted_mod_name())
        if not fs.existsSync(cur_mod_dir)
            fs.mkdirSync(cur_mod_dir)
            @_create_metadata()
        createEmptyFile(path.join(cur_mod_dir, 'main.lua'))
