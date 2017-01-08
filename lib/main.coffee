{CompositeDisposable, BufferedProcess} = require 'atom'
path = require 'path'
os = require 'os' # os.platform()

MOD_PATH = null
if os.platform() == "win32"
  MOD_PATH = "Documents\\My Games\\Binding of Isaac Afterbirth+ Mods"
else if os.platform() == "darwin"
  MOD_PATH = "Library/Application Support/Binding of Isaac Afterbirth+ Mods"
else if os.platform() == "linux"
  MOD_PATH = ".local/share/binding of isaac afterbirth+ mods"

MOD_PATH = path.join(os.homedir(), MOD_PATH)

#verify if doc is newer than .luarc
verify_docupdate = (docDir, modDir) ->
  console.log "Verifiy Update"
  provider = new BufferedProcess
    command: 'python3'
    args: [path.join(__dirname, 'updateChecker.py'),
           docDir, path.join(modDir, '.luacompleterc')]
    stderr: (data) ->
      console.log data
      null


rebuild = (docDirectory, modDir) ->
  console.log "Rebuild"
  provider = new BufferedProcess
    command: 'python3'
    args: [path.join(__dirname, 'scraper.py'),
           docDir, path.join(modDir, '.luacompleterc')]
    stderr: (data) ->
      console.log data
      null


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
    isaacPath:
      title: 'Isaac Game folder'
      description: '''This is the path to your Binding of Isaac:Rebirth
      game location. You need to change this if you installed Rebirth
      on a custom location or if Atom is reporting you issues of not finding
      the "documentation pages".
      \n
      The proper path is the location of the isaac executable (the folder
      that Steam calls "Local Files")'''
      default: ''
      type: 'string'
  #members
  subscriptions: null
  editor: null

  activate: (state) ->
    @subscriptions = new CompositeDisposable
    @subscriptions.add atom.commands.add 'atom-workspace',
      'atom-boilua:force-rebuild' : => @force_rebuild()
    atom.workspace.observeTextEditors @verify_path
    null

  force_rebuild: ->
    console.log "Force rebuild"
    doc_path = atom.config.get('isaacPath')
    doc_path = path.join(doc_path, 'tools/LuaDocs')
    rebuild(doc_path, atom.config.get('modPath'))

  #verify if we are in the modding directory
  verify_path: (editor) ->
    cur_path = editor.getPath()
    cur_path = path.resolve(cur_path)
    console.log cur_path + ":" + atom.config.get('atom-boilua.modPath')
    if cur_path.startsWith(atom.config.get('atom-boilua.modPath'))
      if verify_docupdate()
        rebuild()
    null
