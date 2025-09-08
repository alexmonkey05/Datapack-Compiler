from logger import L, LOGLEVEL
import os
import shutil
from transform import DatapackGenerater, error_as_txt, modify_file_data, filedata
from consts import planet_parser, NEW_LINE
import datetime
import sys

  
logger = L()
COMET_CACHE_FILE = "./comet_cache.txt"
existing_functions = {}


datapack_versions = {
    "1.20.4": "26",
    "1.20.6": "41",
    "1.21": "48",
    "1.21.1": "48",
    "1.21.2": "57",
    "1.21.3": "57",
    "1.21.4": "61",
    "1.21.5": "71",
    "1.21.6": "71",
    "1.21.7": "80",
    "1.21.8": "80"
}

def search_functions(function_folder_dir):
    global existing_functions
    if not os.path.exists(function_folder_dir):
        existing_functions = {}
        return
    filenames = os.listdir(function_folder_dir)
    for filename in filenames:
        if filename == "tick.mcfunction" or filename == "load.mcfunction": continue
        full_filename = os.path.join(function_folder_dir, filename)
        full_filename = full_filename.replace("\\", "/")
        if filename.split(".")[-1] != "mcfunction": search_functions(full_filename)
        else: existing_functions[full_filename] = True
# 네임스페이스/functions, tick.json, load.json 삭제 후 재생성
def make_basic_files(version, file_dir, namespace = "pack"):
    logger.debug("make_basic_files", f"version: {version}, file_dir: {file_dir}, namespace: {namespace}")

    function_folder = "function"
    if version[:4] == "1.20": function_folder = "functions"

    function_folder_dir = os.path.join(file_dir, namespace, "data", namespace, function_folder)
    tag_folder_dir = os.path.join(file_dir, namespace, "data", "minecraft", "tags", function_folder)
    

    # if os.path.exists(file_dir + f"{namespace}/data/{namespace}/{function_folder}"): shutil.rmtree(file_dir + f"{namespace}/data/{namespace}/{function_folder}")
    search_functions(function_folder_dir)
    if os.path.exists(function_folder_dir): shutil.rmtree(function_folder_dir)
    

    if not os.path.exists(tag_folder_dir): os.makedirs(tag_folder_dir)
    if not os.path.exists(function_folder_dir): os.makedirs(function_folder_dir)

    load_json = file_dir + f"{namespace}/data/minecraft/tags/{function_folder}/load.json"
    tick_json = file_dir + f"{namespace}/data/minecraft/tags/{function_folder}/tick.json"
    load_mcfunction = file_dir + f"{namespace}/data/{namespace}/{function_folder}/load.mcfunction"
    tick_mcfunction = file_dir + f"{namespace}/data/{namespace}/{function_folder}/tick.mcfunction"
    pack_mcmeta = file_dir + f"{namespace}/pack.mcmeta"
    file = open(load_json, "w+")
    file.write(f"{{\"values\": [\"{namespace}:load\"]}}")
    file.close()
    file = open(tick_json, "w+")
    file.write(f"{{\"values\": [\"{namespace}:tick\"]}}")
    file.close()
    if not os.path.isfile(load_mcfunction):
        file = open(load_mcfunction, "w+")
        file.write(f"\
# This data pack was compiled with the 40planet's compiler.\n\
# https://github.com/alexmonkey05/Datapack-Compiler\n\nscoreboard objectives add 40planet_num dummy\n")
        file.close()
    if not os.path.isfile(tick_mcfunction):
        file = open(tick_mcfunction, "w+")
        file.close()
    if not os.path.isfile(pack_mcmeta):
        file = open(pack_mcmeta, "w+")
        file.write('{ "pack": {"pack_format": ' + datapack_versions[version] + ', "description": "by 40planet"} }')
        file.close()


def generate_datapack(filename, version, result_dir = "./", namespace = "pack"):
    # 파일 경로 가공
    result_dir = result_dir.strip()
    namespace = namespace.strip()
    if result_dir == "" or namespace == "":
        logger.critical("\n\nresult directory and namespace can not be empty string\n")
        return
    if result_dir[-1] != "/" and result_dir[-1] != "\\":
        result_dir += "/"

    # 데이터팩 기본 경로 만들기
    make_basic_files(version, result_dir, namespace)

    # 파일 경로 가공
    if len(filename) < 7 or filename[-7:] != ".planet": filename += ".planet"

    # .planet 파일 존재 확인
    if not os.path.isfile(filename):
        raise ValueError(error_as_txt(None, f"\"{filename}\" does not exist", filename, "", "fdsa"))


    # 파싱
    now = datetime.datetime.now()
    parser_tree = None
    with open(filename, "r", encoding="utf-8") as file:
        logger.debug("open_file", f"{logger.fit(filename, 20)} took {logger.prYello(int((datetime.datetime.now() - now).total_seconds() * 1000) / 1000)}s")
        
        now = datetime.datetime.now()
        file_data = modify_file_data(file.read())

    parser_tree = planet_parser.parse(file_data + "\n")
    logger.debug("parse_file",f"{logger.fit(filename, 20)} took {logger.prYello(int((datetime.datetime.now() - now).total_seconds() * 1000) / 1000)}s")

    # make_basic_files("1.21", "./", "pack")

    # 트랜스폼
    now = datetime.datetime.now()
    # print(parser_tree.pretty())
    datapack_generator = DatapackGenerater(version, result_dir, namespace, filename, logger_level=logger)
    datapack_generator.transform(parser_tree)
    logger.debug("interprete_file", f"{logger.fit(filename, 20)} took {logger.prYello(int((datetime.datetime.now() - now).total_seconds() * 1000) / 1000)}s")
    write_all_files()
    return parser_tree

def write_all_files():
    now = datetime.datetime.now()
    for filename in filedata:
        if filename in existing_functions: del existing_functions[filename]
        # if filename in comet_cache and filedata[filename] == comet_cache[filename]: continue
        with open(filename, "a+", encoding="utf-8") as file:
            file.write(filedata[filename])
    # with open(COMET_CACHE_FILE, "w+", encoding="utf-8") as file:
    #     file.write(str(filedata))
    # for filename in existing_functions:
    #     os.remove(filename)
    logger.debug("write_datapack", f"Took {logger.prYello(int((datetime.datetime.now() - now).total_seconds() * 1000) / 1000)}s")

import argparse
values = ["1.20.4", "1.20.6", "1.21", "1.21.1", "1.21.2", "1.21.3", "1.21.4", "1.21.5", "1.21.6", "1.21.7", "1.21.8"]
if __name__ == "__main__":
    
    # if os.path.isfile(COMET_CACHE_FILE):
    #     with open(COMET_CACHE_FILE, "r+", encoding="utf-8") as file:
    #         comet_cache = eval(file.read())
    # else:
    #     comet_cache = {}

    parser = argparse.ArgumentParser(
                    prog='comet_compiler',
                    description='Compile .planet files')
    parser.add_argument('--cli', action='store_true', help="Use cli instead of gui")      # option that takes a value
    parser.add_argument('-p', '--planet', help="Select file to compile")
    parser.add_argument('-v', '--version', help="Select minecraft version")
    parser.add_argument('-d', '--dist', help="Select folder to locate output")
    parser.add_argument('-n', '--name', help="Input namespace. Default value is \"pack\".")
    parser.add_argument('-l', '--logger', help="Input logger level. Default value is \"INFO\".")
    args = parser.parse_args()
    if args.cli:
        logger.log("===============================================")
        logger.log("  ██████╗ ██████╗ ███╗   ███╗███████╗████████╗ ")
        logger.log(" ██╔════╝██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝ ")
        logger.log(" ██║     ██║   ██║██╔████╔██║█████╗     ██║    ")
        logger.log(" ██║     ██║   ██║██║╚██╔╝██║██╔══╝     ██║    ")
        logger.log(" ╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗   ██║    ")
        logger.log("  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝    ")
        logger.log("===============================================")

        now = datetime.datetime.now()

        v = args.version
        if v not in values or v == "":
            logger.critical(f"Invalid version: {v} / Required version: {values}")
            sys.exit(0)
        p = args.planet
        d = args.dist
        if p == None:
            logger.critical("planet file(-p / --planet) is required")
            sys.exit(0)
        if d == None:
            logger.critical("dist folder(-d / --dist) is required")
            sys.exit(0)
        n = args.name
        if n == None: 
            n = "pack"
            logger.info("namespace", f"namespace is not defined, using default namespace: {logger.prGreen(n)}")
        l = args.logger
        if l == None: l = "INFO"
        logger.verboseLevel = LOGLEVEL[l]
            
        
        try:
            interprete_result = generate_datapack(p, v, d, n)
        except ValueError as err:
            print(err)
            sys.exit()
            logger.critical(err)
        took = int((datetime.datetime.now() - now).total_seconds() * 1000) / 1000
        logger.log(f"Done! Took {logger.prYello(took)}s")


        sys.exit(0)

    import eel
    import tkinter
    import json
    from tkinter import filedialog
    from eel import chrome, edge

    CONFIG_FILE = "./settings.json"

    @eel.expose
    def load_settings():
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            default_settings = {
                "file": "",
                "folder": "",
                "namespace": "pack"
            }
            save_settings(default_settings)
            return default_settings

    @eel.expose
    def save_settings(settings):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

    parentDir = os.path.dirname(__file__)

    eel.init(os.path.join(parentDir, "web"));

    @eel.expose
    def event(name, dir, version, namespace):
        try:
            generate_datapack(name, version, dir, namespace)
            return "success"
        except BaseException as error:
            logger.critical(str(error));
            return str(error)
        

    @eel.expose
    def select_planet_file():
        root = tkinter.Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        result = filedialog.askopenfile(
            title="파일 선택창",
            filetypes=(('planet files', '*.planet'), ('all files', '*.*'))
        )
        if result:
            return result.name
        else:
            return ""

    @eel.expose
    def select_folder():
        root = tkinter.Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        directory_path = filedialog.askdirectory()
        return directory_path


    import webbrowser
    @eel.expose
    def open_folder(path):
        webbrowser.open(f"file:///{path}")

    def __can_use_chrome():
        """Identify if Chrome is available for Eel to use"""
        chrome_instance_path = chrome.find_path()
        return chrome_instance_path is not None and os.path.exists(chrome_instance_path)


    def __can_use_edge():
        """Identify if Edge is available for Eel to use"""
        return edge.find_path()
    
    import socket 

    def get_port():
        """Get an available port by starting a new server, stopping and and returning the port"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
        sock.close()
        return port
    
    class UIOpenMode:
        NONE = 0
        CHROME_OR_EDGE = 1
        DEFAULT_BROWSER = 2

    # try:
    chrome_available = __can_use_chrome()
    edge_available = __can_use_edge()
    open_mode = UIOpenMode.CHROME_OR_EDGE

    if open_mode == UIOpenMode.CHROME_OR_EDGE and chrome_available:
        logger.info("The interface is being opened in a new Chrome window")
        logger.info(
            "Please do not close this terminal while using this compiler - the process will end when the window is closed"
        )
        eel.start("index.html", size=(600, 800), port=0, mode="chrome")
    elif open_mode == UIOpenMode.CHROME_OR_EDGE and edge_available:
        logger.info("The interface is being opened in a new Edge window")
        logger.info(
            "Please do not close this terminal while using this compiler - the process will end when the window is closed"
        )
        eel.start("index.html", size=(600, 800), port=0, mode="edge")
    elif open_mode == UIOpenMode.DEFAULT_BROWSER or (
        open_mode == UIOpenMode.CHROME_OR_EDGE and not chrome_available and not edge_available
    ):
        logger.info("The interface is being opened in your default browser")
        logger.info(
            "Please do not close this terminal while using this compiler - the process will end when the window is closed"
        )
        eel.start("index.html", size=(600, 800), port=0, mode="user default")
    else:
        port = get_port()
        logger.info(f"Server starting at http://localhost:{port}/index.html")
        logger.info("You may end this process using Ctrl+C when finished using auto-py-to-exe")
        eel.start("index.html", host="localhost", port=port, mode=None, close_callback=lambda x, y: None)