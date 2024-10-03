
import os, json, subprocess, shutil
import datetime, sys, tarfile, zipfile
import requests, io

def log(*f, sep=" ", end="\n"):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [i]", *f, sep=sep, end=end)

def warn(*f, sep=" ", end="\n"):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [w]", *f, sep=sep, end=end)

def ask(string, default_no=False):
    a = input(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [?] " + string + " [" + ("yN" if default_no else "Yn") + "] ")
    if a.lower() in "y1":
        return True
    elif a.lower() in "n0":
        return False
    else:
        return not default_no

def log_input(string):
    return input(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [?] " + string)

def log_input_multiline(string, newlines):
    retval = []
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [?] " + string)
    newline = 0
    while newline < newlines:
        string = input(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ? ")
        if string == "": newline += 1
        else: newline = 0
        retval.append(string)
    for _ in range(newlines): retval.pop()
    return retval

def non_lethal_error(*f, sep=" ", end="\n"):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [e]", *f, sep=sep, end=end)

def error(*f, sep=" ", end="\n"):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [e]", *f, sep=sep, end=end)
    sys.exit(1)

def compile_changed_files(jar, code, out, files):
    popen = subprocess.run(["javac", "-cp", jar, *map(lambda x: os.path.join(code, x), files), "-d", out], capture_output=True)
    if popen.returncode != 0:
        for i in popen.stderr.decode().split("\n"):
            non_lethal_error(i)
        error("process exited with non-zero code, bailing out")

def compress_into_jar(folder, file):
    out_dir = os.getcwd()
    os.chdir(folder)
    
    if os.path.isfile(os.path.join(out_dir, file)): os.remove(os.path.join(out_dir, file))

    popen = subprocess.run(["7z", "a", os.path.join(out_dir, file), *os.listdir(".")], capture_output=True)
    if popen.returncode != 0:
        for i in popen.stderr.decode().split("\n"):
            non_lethal_error(i)
        error("process exited with non-zero code, bailing out")

    os.chdir(out_dir)

def make_mbm(output_file, slug, add_jar=True, add_data=True):
    with tarfile.TarFile(output_file, "w") as f:
        f.add("manifest.json")
        if add_jar: f.add(slug + ".jar")
        if add_data: f.add("data")

def conv_bytes(b):
    if b < 1024:
        return f"{b} bytes"
    elif b < 1024**2:
        return f"{b/1024:0.2f} kB"
    elif b < 1024**3:
        return f"{b/(1024**2):0.2f} MB"
    elif b < 1024**4:
        return f"{b/(1024**3):0.2f} GB"
    elif b < 1024**5:
        return f"{b/(1024**4):0.2f} TB"

def compile():
    if not os.path.isfile("manifest.json"):
        error("cant find manifest. probably not a mod folder.")
    
    out = os.path.abspath("out")
    jar = os.path.abspath("jar")
    code = os.path.abspath("code")

    manifest = json.load(open("manifest.json"))
    
    files = list(map(lambda x: x.strip(), filter(lambda x: bool(x), open("changed_files.txt").readlines())))

    if len(files) != 0:
        log("compiling changed files...")
        compile_changed_files(jar, code, out, files)
        log("compressing compiled classes...")
        compress_into_jar(out, manifest['slug'] + ".jar")
    else:
        log("no changed files, assuming data-only mod")
    
    log("making final mod file...")
    make_mbm(F"{manifest['slug']}.mbm", manifest["slug"], len(files) != 0, len(os.listdir("data")) != 0)
    log(f"done! see {manifest['slug']}.mbm")

def print_help(program_name):
    log(f"usage: {program_name} <keyword>")
    log( "  valid keywords are:")
    log( "    init      - initialize cwd as a mod")
    log( "    decompile - decompile and extract jar, second stage of init")
    log( "    compile   - compile into an .mbm mod")
    log( "    help      - show this message")

def print_process(program_name):
    log( "to create a mod:")
    log( "1. copy this script to a new folder")
    log(f"2. run $ {program_name} init, put all details in")
    log(f"3. copy %MEWNBASE%/game/desktop-1.0.jar to cwd and run $ {program_name} decompile")
    log( "4. it will download decompiler and decompile the game into code/ folder")
    log( "5. to actually write a mod:")
    log( "  1. write all custom code in the code/ directory")
    log( "  2. add json/translation files that will be replaced in game's data/ folder to data/ folder")
    log( "  3. add all edited files to changed_files.txt, e.g. com/cairn4/moonbase/Player.java")
    log(f"6. $ {program_name} compile")

if __name__ == "__main__":
    program_name = sys.argv.pop(0)
    if len(sys.argv) == 0:
        print_help(program_name)
        error("expected a keyword in arguments")
    
    keyword = sys.argv.pop(0)

    if keyword == "init":
        if len(os.listdir()) != 1:
            if ask("this folder is not empty. clear it?", True):
                for i in os.listdir():
                    if i == os.path.basename(__file__): continue
                    if os.path.isfile(i): os.remove(i)
                    else: shutil.rmtree(i)
            else:
                sys.exit()
        mname = log_input("mod name? ")
        slug_invalid = True
        mslug = ""
        while slug_invalid:
            slug_invalid = False
            mslug = log_input("mod slug? ")
            for i in mslug:
                if i not in "1234567890qwertyuiopasdfghjklzxcvbnm-_":
                    warn("the slug contains invalid charachters")
                    warn("slug should contain only lowercase letters, numbers, underscores and dashes")
                    slug_invalid = True
                    break
        mdesc = "\n".join(log_input_multiline("write a mod description, end with a double-newline", 2))
        mauthors = log_input_multiline("write all authors of the mod on each line, end with a newline", 1)
        manifest = {"name": mname, "description": mdesc, "authors": mauthors, "slug": mslug, "version": 1}
        json.dump(manifest, open("manifest.json", "w"))
        os.mkdir("jar")
        os.mkdir("data")
        os.mkdir("code")
        log(f"copy %MEWNBASE%/game/desktop-1.0.jar here, and run $ {program_name} decompile")
        open("changed_files.txt", "w").close()
    elif keyword == "decompile":
        if not os.path.isfile("desktop-1.0.jar"):
            error("no desktop-1.0.jar is found")
        if not os.path.isfile("cfr.jar"):
            warn("no cfr.jar is found.")
            if ask("download it?"):
                link = "https://www.benf.org/other/cfr/cfr-0.152.jar"
                log(f"downloading {link.rsplit('/', 1)[1]}...")
                
                try: request = requests.get(link, stream=True)
                except: error("error downloading!")
                if not request.ok:
                    error("error downloading!")

                length = request.headers.get('content-length')
                data = b""

                if length is None:
                    data += request.content
                else:
                    dl = 0
                    length = int(length)
                    for d in request.iter_content(chunk_size=65536):
                        dl += len(d)
                        data += d

                        print(" " * (os.get_terminal_size().columns - 1), end="\r")
                        log(f"{dl/length*100:0.0f}%, {conv_bytes(dl)}", end="\r")
                
                open("cfr.jar", "wb").write(data)
                print(" " * (os.get_terminal_size().columns - 1), end="\r")
                log("done")
            else:
                sys.exit(1)

        log("extracting jar w/resources & classes to jar/")
        subprocess.run(["7z", "x", "desktop-1.0.jar", "-ojar", "-y"])
        
        log("decompiling jar w/o resources to code/")
        subprocess.run(["java", "-jar", "cfr.jar", "--outputdir", "code", "desktop-1.0.jar"])
    elif keyword == "compile": compile()
    elif keyword == "help": print_help(program_name)
