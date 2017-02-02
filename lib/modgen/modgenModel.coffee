fs = require 'fs'
path = require 'path'

ModgenView = require './modgenView'
modTemplates = require './xmlpurposes.json'

module.exports = class ModgenModel
    constructor: () ->
        @

    getTitle: () ->
        return 'AB+ templates'

    _copy_res: (src_files) ->
        cont_path = path.join(atom.config.get('Atom-boilua.modPath'), 'content')
        res_path = atom.config.get('Atom-boilua.resourcePath')
        try
            for file in src_files
                fwrite = fs.openSync(path.join(cont_path,file), 'wx')
                # writes into fwrite the content of file in res foler
                fs.write(fwrite, fs.readFileSync(path.join(res_path, file)))
                fs.closeSync(fwrite)
        catch error
            errOptions = {
                text: 'Failure in Atom-boilua',
                description: '''Please enter in Atom-boilua's settings
                menu the location of your extracted.''',
                detail: error,
                dismissable: true
            }
            atom.notifications
                .addFatalError('Failure in Atom-boilua',errOptions)
