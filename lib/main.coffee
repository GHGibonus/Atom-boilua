{CompositeDisposable, BufferedProcess} = require 'atom'
path = require 'path'
os = require 'os' # os.platform(), os.homedir()
fs = require 'fs' #fs.stat()

MOD_PATH = null
BOI_PATH = "steamapps/common/The Binding of Isaac Rebirth"
if os.platform() == "win32"
  MOD_PATH = "Documents/My Games/Binding of Isaac Afterbirth+ Mods"
  BOI_PATH = path.join("Program Files/steam", BOI_PATH)
else if os.platform() == "darwin"
  MOD_PATH = "Library/Application Support/Binding of Isaac Afterbirth+ Mods"
  BOI_PATH = path.join(os.homedir(), "Library/Application Support/Steam",
                       BOI_PATH)
else if os.platform() == "linux"
  MOD_PATH = ".local/share/binding of isaac afterbirth+ mods"
  BOI_PATH = path.join(os.homedir(), ".local/share/Steam", BOI_PATH)

MOD_PATH = path.join(os.homedir(), MOD_PATH)

#verify if doc is newer than .luacompleterc
verify_docupdate = (docDir, modDir) ->
  console.log "Verifiy Update"
  if not fs.existsSync(docDir)
    throw console.error
  docDate = fs.statSync(docDir)['mtime']

  completercPath = path.join(modDir, '.luacompleterc')
  if not fs.existsSync(completercPath) #if file does not exist, returns directly
    return true
  else
    completercDate= fs.statSync(completercPath)['mtime']
    return docDate.getTime() > completercDate.getTime()


rebuild = (docDir, modDir) ->
  console.log "Rebuild"
  pythonPath = atom.config.get('atom-boilua.pythonPath')
  provider = new BufferedProcess
    command: pythonPath #Launches the python doc scraper
    args: [
      path.join(
        atom.packages.resolvePackagePath('atom-boilua')
        'lib/scraper.py')
      docDir,
      path.join(modDir, '.luacompleterc')
    ]
    stdout: (data) ->
      console.log data
      null
  provider.onWillThrowError (error, __) ->
    throw error
  provider.process?.stdin.on 'error', (err) ->
    console.log 'stdin', err

#returns the path to the doc file
docPath = ->
  path.join(atom.config.get('atom-boilua.isaacPath'), 'tools/LuaDocs')


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
      default: BOI_PATH
      type: 'string'
    pythonPath:
      title: 'Python path'
      description: '''The path to your Python executable, if you are on
      Windows, the default value is not enough, please provide it.

      Remember that your Python version must be 3.5 or higher!'''
      default: 'python3'
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
    rebuild(docPath(), atom.config.get('atom-boilua.modPath'))
    null

  #verify if we are in the modding directory
  verify_path: (editor) ->
    cur_path = editor.getPath()
    cur_path = path.resolve(cur_path)
    modPath = atom.config.get('atom-boilua.modPath')
    console.log "verify Path"
    if cur_path.startsWith(modPath) and verify_docupdate(docPath(), modPath)
      rebuild(docPath(), modPath)
    null
