import pathlib
import shutil
try:
    from dependencies.Explorer import Explorer, ExplorerNew
    from dependencies.index_photos import Index_photos
    from dependencies.create_html import Create_HTML
except ImportError:
    print("Error when importing python modules")

import os


#e = Explorer()
#e = ExplorerNew(__file__)
#print(next(os.walk(e.path())))     #os.walk(self.path())
#print(e.start())

def integrityTests():
    test = True
    files = ["create_html.py", "index_photos.py", "Explorer.py", "index_TEMPLATE.html", "photo_index_TEMPLATE.db"] #necessary files    

    for f in files:
        if testFileExists(basePath, f) == False: test = False

    return test



def main():
    e = ExplorerNew(__file__) #returns string absolute path
    setPath = ""
    
    print("______________________________")
    print("Welcome in setup. Do you want to create new database, or update current?")
    if query("N", "New", "U", "Update") == "N":
        input(f"in next step, choose path, where the base folder is. Press any key to continue..")
        setPath = e.start()
        if setPath == 0: print("Quiting"); return #if quited from explorer, return is =0
        if testFileExists(setPath, html, False): #test if index.html already exists (it should not when creating new)
            print(f"in choosen `{html}` already exist, didn`t you want to Update? Do you want to continue?")
            if query("C", "Continue", "Q", "Quit") == "Q": #else quit because .html file already exists
                return  
        
        shutil.copy(pathlib.Path(basePath) / "photo_index_TEMPLATE.db", pathlib.Path(setPath) / db)
    else:
        input(f"in next step, choose path, in which `{db}` and `{html}` are saved. Press any key to continue..")
        setPath = e.start()
        if setPath == 0: print("Quiting"); return #if quited from explorer, return is =0

    if not testFileExists(setPath, db): #test if .db file exists in given path
        return

    #INDEX_PHOTOS.PY
    print("---START of index_photos.py")
    a = Index_photos(setPath, db)
    print("---END of index_photos.py")

    #CREATE_HTML.PY
    print("---START of create_html.py")
    Create_HTML(pathlib.Path(setPath) / db, html, basePath)
    print("---END of create_html.py")



def query(a, aString, b, bString):
    answer = input(str(a) + " " + aString + ";   " + str(b) + " " + bString + " : ")
    if answer.lower() == a.lower():
        return a
    elif answer.lower() == b.lower():
        return b
    else:
        return query(a, aString, b, bString)
    
def testFileExists(path, file, verbose = True):
    #file = "photo_index.db"

    if (pathlib.Path(path) / file).is_file():
        return True
    else:
        if verbose: print(f"there was no `{file}` found in `{path}`. Please fix the problem. The script will now Quit.")
        return False



if __name__ == "__main__":
    #ABSOLUTELY DEFINED VARIABLES
    html = "index.html" #default name of index.html
    db = "photo_index.db" #default name of database
    #AUTOMATICALLY DEFINED VARIABLES
    basePath = pathlib.Path(__file__).parent / "dependencies"


    if integrityTests():
        main()
    else:
        print("SOME FILES ARE MISSING! The script will now end.")