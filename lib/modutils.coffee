# A collection of functions useful to process mods in general
fs = require 'fs'
path = require 'path'

module.exports =
    # finds the directory of the mod we are editing, returns false if
    # cur_path is not a subfolder of mod_path.
    findModDir: (cur_path, mod_path) ->
        while cur_path.startsWith(mod_path)
            if path.dirname(cur_path) == mod_path
                return cur_path
            else
                cur_path = path.dirname(cur_path)
        return false

    # returns true if a file with the given mod_name exists in the mod path
    # otherwise returns false
    existsMod: (mod_name) ->
        mod_path = atom.config.get('Atom-boilua.modPath')
        for mod_candidate in fs.readdirSync(mod_path)
            if mod_name == mod_candidate
                return true
        return false

    # if all file names present in file_name_list are in dir, returns true
    # otherwise, returns false
    arePresentFiles: (dir, file_name_list) ->
        if not fs.existsSync(dir)
            return null
        dir_file_names_list = fs.readdirSync(dir)
        for file_name in file_name_list
            foundFile = false
            for dir_file_name in dir_file_names_list
                if file_name == dir_file_name
                    foundFile = true
                    break
            if not foundFile
                return false
        return true

    # Copies src into dst, but only if dst doesn't already exists.
    # Throws an error in that case.
    copyToFrom: (dst, src) ->
        fwrite = fs.openSync(dst, 'wx')
        fs.readFile(src, (err, data) ->
            fs.writeFileSync(fwrite, data)
            fs.closeSync(fwrite)
        )
        null

    # Creates an empty file at the given location
    # does nothing if that file already exists
    createEmptyFile: (new_file) ->
        try
            fd = fs.openSync(new_file, 'wx')
        catch
            return
        fs.closeSync(fd)
        null

    # Creates recursively the folders necessary for the creation.
    # of newFolder
    createFileStruct: (new_folder) ->
        if fs.existsSync(new_folder)
            return
        cur_path = new_folder
        found_proper_path = false
        # Bottom to top discovery of the first existing enclosing directory.
        while path.parse(cur_path).root != cur_path
            cur_path = path.dirname(cur_path)
            if fs.existsSync(cur_path)
                found_proper_path = true
                break

        if found_proper_path
            left_to_make = path.relative(cur_path, new_folder).split(path.sep)
            base_dir = cur_path
            for dir in left_to_make
                base_dir = path.join(base_dir, dir)
                fs.mkdirSync(base_dir)
        else
            throw new Error('Cannot create a folder without parents.')
        null


    # Convenience function, returns the path to the Atom-boilua package
    boiluaLoc: () ->
        return fs.realpathSync(atom.packages.resolvePackagePath('Atom-boilua'))

    # Convenience function, returns the path to the isaac mod folder
    isaacmodLoc: () ->
        return fs.realpathSync(atom.config.get('Atom-boilua.modPath'))

    # Returns the file open in the current text buffer
    currentFile: () ->
        return fs.realpathSync(atom.workspace.getActiveTextEditor().getPath())
