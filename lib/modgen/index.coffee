ModgenModel = require './modgenModel'
ModgenView = require './modgenView'

module.exports =
    toggleModgenPane: () ->

    createModgenPane: () ->
        @model = new ModgenModel()
        @view = new ModgenView()
        atom.views.addViewProvider(ModgenModel, (modgen_model) =>
            view = @view
            modgen_model.setView(view)
            return view
        )
        active_pane = atom.workspace.addModalPanel({item: @view})
        null
