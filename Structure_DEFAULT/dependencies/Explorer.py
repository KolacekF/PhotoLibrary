import os
import pathlib

class Explorer:
    def __init__(self):
        self.dot = "."
        self.workingPath = []
        self.iteration= 0

    #accepts string, name of subfolder, which to go in
    def downLevel(self, l):
        self.workingPath.append(l)

    #.pop() last record from workingPath = go up one leve
    def upLevel(self):
        self.workingPath.pop()

    #return UNIX formated path string
    def path(self):
        pathString = self.dot
        for l in self.workingPath:
            pathString += f"/{l}"
        return pathString
    
    #scan current directory, return dictionary of folders
    def scan(self):
        fileTree = {}
        files = next(os.walk(self.path()))[1]
        i = 1
        for filename in files:
            fileTree[i] = filename
            i += 1
        return fileTree
    
    #print() commands, current directory tree and dictionary of scaned files
    def start(self):
        self.iteration += 1
        print("______________________________")
        print(f"Explorer-iteration:-{self.iteration}".center(30, "-"))
        print(self.path())
        print("   Q for quit; S for start; U for one level up")
        if (pathlib.Path(self.path()) / "photo_index.db").is_file(): print("`photo_index.db` found. START?")
        files = self.scan()
        print(f"   folders: {files}")
        x = input() #x is string
        if x == "Q": #I have to old python for match - case
            return 0
        if x == "S":
            return self.path()
        elif x == "U":
            self.upLevel()
            return self.start()
        else:
            self.downLevel(files[int(x)])
            return self.start()
        

class ExplorerNew(Explorer):
    def __init__(self, scriptPath):
        super().__init__()
        self.absolutepath = pathlib.Path(scriptPath).parent

    def downLevel(self, l):
        self.absolutepath = self.absolutepath / l

    def upLevel(self):
        self.absolutepath = self.absolutepath.parent

    def path(self):
        return str(self.absolutepath)




#e = Explorer()
#print(e.start())