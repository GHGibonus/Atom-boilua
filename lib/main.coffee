{CompositeDisposable, BufferedProcess} = require 'atom'

provider = require './provider'

{launch_isaac} = require './idelike'
{createModgenPane, removeModgenPane} = require './modgen'
{findModDir, isaacmodLoc, boiluaLoc} = require './modutils'

path = require 'path'
os = require 'os' # os.platform(), os.homedir()
fs = require 'fs' #fs.statSync(), fs.unlinkSync(), fs.existsSync

BOI_CMD = null
MOD_PATH = null
BOI_PATH = "steamapps/common/The Binding of Isaac Rebirth"
if os.platform() == "win32"
    MOD_PATH = "Documents/My Games/Binding of Isaac Afterbirth+ Mods"
    BOI_PATH = path.join("C:/Program Files/Steam", BOI_PATH)
    BOI_CMD = "C:/Program\\ Files/Steam/Steam.exe steam://run/250900"
else if os.platform() == "darwin"
    MOD_PATH = "Library/Application Support/Binding of Isaac Afterbirth+ Mods"
    BOI_PATH = path.join(os.homedir(), "Library/Application Support/Steam",
                         BOI_PATH)
    BOI_CMD = "steam steam://run/250900"
else if os.platform() == "linux"
    MOD_PATH = ".local/share/binding of isaac afterbirth+ mods"
    BOI_PATH = path.join(os.homedir(), ".local/share/Steam", BOI_PATH)
    BOI_CMD = "steam steam://run/250900"

MOD_PATH = path.join(os.homedir(), MOD_PATH)

#verify if doc is newer than .luacompleterc
verify_docupdate = (docDir, modDir) ->
    if not fs.existsSync(docDir)
        atom.notifications.addWarning('Atom-boilua couldn\'t find the doc path')
        return
    docDate = fs.statSync(docDir)['mtime']
    completercPath = path.join(modDir, '.luacompleterc')
    moduleDate = fs.statSync(boiluaLoc())['mtime']
    if not fs.existsSync(completercPath) #if file does not exist, returns
        return true
    else
        completercDate= fs.statSync(completercPath)['mtime']
        if moduleDate.getTime() > completercDate.getTime()
            return true
        else
            return docDate.getTime() > completercDate.getTime()

rebuild = (docDir, modDir) ->
    command = atom.config.get('Atom-boilua.pythonPath')
    args = [
        path.join(boiluaLoc(), 'lib/scraper/main.py'),
        docDir,
        path.join(modDir, '.luacompleterc')
    ]
    stdout = (output) -> console.log(output)
    stderr = (output) ->
        errOptions = {
            text: 'Failure in Atom-boilua caught',
            description: '''The python scraper n\' serializer failed. Please
            report issues at https://github.com/GHGibonus/Atom-boilua/issues

            Atom might be modest and pretend it is its own fault, but it is
            lying if the traceback you see is Python source code.''',
            detail: output,
            dismissable: true
        }
        atom.notifications.addFatalError('Failure in Atom-boilua',errOptions)
    exit = (code) ->
        if code != 0
            console.log("something happend")
        if code == 0
            atom.notifications.addInfo(
                'Atom-boilua successfully generated the luacompleterc file')
    process = new BufferedProcess({command, args, stdout, stderr, exit})

#returns the path to the doc file
docPath = () ->
    path.join(atom.config.get('Atom-boilua.isaacPath'), 'tools/LuaDocs')

# deletes the annoying 'update.it' file that marks mods as out of date,
# which breaks the flow of developpement.
deleteUpdateIt = (event) ->
    mod_path = isaacmodLoc()
    updateit_path = path.join(findModDir(event.path, mod_path), 'update.it')
    if updateit_path and fs.existsSync(updateit_path)
        # double check we are indeed deleting an 'update.it' file,
        # to make 100% sure we don't fuck up users' file system.
        if path.basename(updateit_path) == 'update.it'
            fs.unlinkSync(updateit_path)
        else
            console.log('almost deleted ', updateit_path, '!!! close one.')

module.exports =
    #config schema
    config:
        modPath:
            title: 'Isaac Afterbirth+ mod folder'
            description: '''This is your Isaac mod folder, where your
            mod folders are located. Leave empty if you want to use your
            platform default (which should work out of the box in all
            circumstances)'''
            default: MOD_PATH
            type: 'string'
            order: 2

        isaacPath:
            title: 'Isaac Game folder'
            description: '''This is the path to your Binding of Isaac:Rebirth
            game location. You need to change this if you installed Rebirth
            on a custom location or if Atom is reporting you issues of not
            finding the "documentation pages".

            The proper path is the location of the isaac executable (the folder
            that Steam calls "Local Files")'''
            default: BOI_PATH
            type: 'string'
            order: 1
        # This is not used. Planned™ feature.
        # resourcePath:
        #     title: 'Isaac resource folder'
        #     description: '''The path in which the isaac resources were
        #     extracted to, using the ResourceExtractor tool.

        #     This is used to setup default files when you create a mod with
        #     templates.'''
        #     default: path.join(BOI_PATH, 'resources')
        #     type: 'string'
        pythonPath:
            title: 'Python path'
            description: '''The path to your Python executable, if you are on
            Windows, the default value is not enough, please provide it.

            Remember that your Python version must be 3.5 or higher!'''
            default: 'python3'
            type: 'string'
            order: 5

        isaacStartCommand:
            title: 'Isaac launch command'
            description: '''The command to use to launch isaac, the game.'''
            default: BOI_CMD
            type: 'string'
            order: 3

        additionalCommands:
            title: 'Additional commands'
            description: '''Additional commands to run when you start isaac.
            For exemple, this could be a program you use to view the log file.
            This is a semicolon separated list of commands, use '\\' to escape
            spaces.'''
            default: ''
            type: 'string'
            order: 4

    #members
    subscriptions: null
    editor: null

    activate: (state) ->
        @subscriptions = new CompositeDisposable()
        @subscriptions.add atom.commands.add 'atom-workspace',
            'Atom-boilua:force-rebuild' : => @force_rebuild()
        @subscriptions.add atom.commands.add 'atom-workspace',
            'Atom-boilua:open-mod-creator' : => @open_modgen()
        @subscriptions.add atom.commands.add \
            'boilua-mod-creator, atom-workspace',
            'Atom-boilua:close-mod-creator' : => @close_modgen()
        @subscriptions.add atom.commands.add 'atom-workspace',
            'Atom-boilua:launch-game' : => @launch_isaac()
        @subscriptions.add(
            atom.workspace.observeTextEditors((editor) =>
                @register_editor_callbacks(editor, @verify_path)
            )
        )

    # Registers functions to call when stuff happen in text editors
    register_editor_callbacks: (editor, verify_path) ->
        verify_path(editor)
        editor.onDidChangePath(() -> verify_path(editor))
        editor.onDidSave(() ->
            # editor inside the mod folder
            if fs.realpathSync(editor.getPath())?.startsWith(isaacmodLoc())
                deleteUpdateIt(path: editor.getPath())
        )

    open_modgen: () ->
        createModgenPane()

    close_modgen: () ->
        removeModgenPane()

    force_rebuild: () ->
        rebuild(docPath(), isaacmodLoc())

    launch_isaac: () ->
        launch_isaac()

    getOptionProvider: () ->
        return provider

    # verify if we are in the modding directory, if so, we check the API doc
    # updateness
    verify_path: (editor) ->
        cur_path = editor.getPath()
        if cur_path != undefined and fs.existsSync(cur_path)
            cur_path = fs.realpathSync(cur_path)
            modPath = isaacmodLoc()
            if cur_path.startsWith(modPath)
                if verify_docupdate(docPath(), modPath)
                    console.log modPath + '/.luacompleterc needs an update'
                    rebuild(docPath(), modPath)
        else
            console.log cur_path + ' is undefined...'
        null
