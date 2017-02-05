path = require 'path'
fs = require 'fs'

{findModDir, isaacmodLoc, boiluaLoc} = require '../modutils'
ModgenModel = require './modgenModel'
ModgenView = require './modgenView'
# Coordinates actions between model, view and data for modgen

index_locals = {}
removeModgenPane = () ->
    atom.workspace.getActivePane().activate()
    index_locals.my_panel.hide()
    index_locals.my_panel.destroy()
    null

module.exports =
    createModgenPane: () ->
        mod_path = isaacmodLoc()
        cur_path = atom.workspace.getActiveTextEditor()?.getPath()
        purposeFile = path.join(boiluaLoc(), 'lib/modgen/xmlpurposes.json')
        data = JSON.parse(fs.readFileSync(purposeFile))
        cur_mod_name = if cur_path?\
            then path.basename(findModDir(cur_path, mod_path))
            else ''
        index_locals.model = \
            new ModgenModel(cur_mod_name, data, removeModgenPane)
        atom.views.addViewProvider(ModgenModel, (modgenModel) ->
            return modgenModel.createView()[0]
        )
        index_locals.my_panel = atom.workspace.addModalPanel({
            item: index_locals.model,
            visible: false
        })
        index_locals.my_panel.onDidChangeVisible((visible) ->
            if visible
                index_locals.model.takeFocus()
            null
        )
        index_locals.my_panel.show()
        index_locals.model.takeFocus()
        null

    removeModgenPane: removeModgenPane
