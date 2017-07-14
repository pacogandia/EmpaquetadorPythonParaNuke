# Empaquetador Python Para Nuke

PROJECT PACKAGER 1.0   

By Disposable Apps

 

This script creates a copy of the files used in the project,
while keeping the folder structure.

It prompts for a source folder and a destination folder,
runs through every node in the open nuke file,
and creates the necessary folders
to build a copy with every file the project uses.

 

Restrictions:

- The destination folder cannot be a subfolder of the source folder

- If a file is located outside the source folder,
the code copies it in a folder called COMPLEMENTOS (the spanish word for Accesories)

 

 

Installation Notes:

1. Copy 'ProjectPackager.py” to your nuke plugins directory
2. Open 'Init.py' located on your nuke plugins directory
3. Paste:
import ProjectPackager
nuke.menu( 'Nuke' ).addCommand('Edit/ProjectPackager', 'ProjectPackager.clone_project()' )
4. Restart Nuke
5. Under the Edit menu you will find the option “ProjectPackager”

 

 

Run:
clone_project()
