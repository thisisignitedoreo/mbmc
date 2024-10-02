# MewnBase Mod-Creator
Simplify the creation of mods for MBML

## Requirements
1. `java` binary (e.g. adoptium jdk)
2. Python installed (should work on older versions though latest one is recommended as it is tested on such)

## Quickstart
1. Create a new folder and copy `main.py` into it
2. `$ python main.py init` and put all the info in
3. If you dont want to change anything in the source code - put your modified json and locale files into `data/` and skip to step 7
4. Copy file `game/desktop-1.0.jar` from game files to mod folder
5. `$ python main.py decompile`, the script will download decompiler and decompile game jar
6. Write the mod itself in the `code/` folder, adding all changed files to `changed_files.txt`, e.g. `com/cairn4/moonbase/Player.java`
7. `$ python main.py compile` will create .mbm file in the mod folder. You can now install it through MBMLs Local Mods tab.
