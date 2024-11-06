import pathlib
import os
import re
import sqlite3
from PIL import Image
from pillow_heif import register_heif_opener
import datetime

class Index_photos:
    def __init__(self, starting_folder, database_filename):
        #SET STARTING FOLDER
        self.folder = starting_folder #"/Volumes/CaeMate/photos" #ABSOLUTE PATH FOR STARTING FOLDER WITH PHOTOS AND .db
        #self.database_name = "photo_index.db" #NAME OF .db FILE
        self.database_name = database_filename #NAME OF .db FILE
        #NAMING RULES
        self.file_extensions = ["jpg", "jpeg","png", "HEIC", "HEIF"]    #ALLOWING RULES   #can be added
        self.regex_omit = ["^\."]                                       #OMMITING RULES   #can be added


        #STARTING TESTS
        if not (pathlib.Path(f"{self.folder}/{self.database_name}").is_file()):
            input(f"{self.database_name} was not found in {self.folder}. Please fix problem and run script again. The script is now closing. Press any key to continue...")
            return
        
        self.Base__init__()
    def Base__init__(self): #run if everything is checked in __init__        
        self.files_list = [] #saving path of all files in subdirectories
        self.files_list_pruned = [] #only files based on naming rules
        self.new_files = [] #only files, that are not in .db

        self.FolderWalk()
        self.PruneFiles_list()
        self.NewFiles()
        if (len(self.new_files) > 0):
            input(f"{len(self.new_files)} files to loged to {self.database_name}. Press any key to continue...")
            self.Exif__init__()
            self.LogNewFiles()
    def Exif__init__(self):
        register_heif_opener()

        self.filesOBJ = [] #list of objects of new files to by written to database

    #LISTING ALL FILES IN SUBDIRECTORIES, THEN SAVING THEM TO FILES_LIST
    def FolderWalk(self):
        for path, subdirs, files in os.walk (self.folder): 
            for name in files:
                self.files_list.append(pathlib.PurePath(path, name)) #[PurePosixPath('/Volumes/CaeMate/photos/.DS_Store'),...]

    #BASED ON FILE NAMING RULES, ADD ONLY THOSE FILES, THAT I WANT
    def PruneFiles_list(self):
        for file in self.files_list:
            if self.TestFileName(file.name): #returning true/false based on rules for file naming
                self.files_list_pruned.append(file)

    def NewFiles(self):
        #query database and list all files paths
        connection = sqlite3.connect(f"{self.folder}/{self.database_name}")
        cursor = connection.cursor()
        cursor.execute("SELECT path FROM photos")
        loged_files = cursor.fetchall()
        print(f"loged_files: {loged_files if len(loged_files)<10 else len(loged_files)}") #IF logged_files will be >10, show only .length
        cursor.close()
        connection.close()
        
        #if there are no files in .db, copy all files from self.files_list_pruned to self.new_files
        if (len(loged_files) == 0):
            for file in self.files_list_pruned:
                self.new_files.append(file)
        #if there are some file in .db, choose which to copy from self.files_list_pruned to self.new_files
        for file_logged in loged_files:
            already_logged = False
            file_found_rel_path = None
            for file_found in self.files_list_pruned:
                file_found_rel_path = os.path.relpath(file_found, self.folder)

                if (str(file_logged[0]) == str(file_found_rel_path)): already_logged = True #compare this list with self.files_list_pruned and save only new one (which arent in .db) to self.files_list_new

            if not already_logged: self.new_files.append(file_found_rel_path)

        print(f"{len(self.new_files)} new files were updated to `{self.database_name}`.")

    def LogNewFiles(self):
        #for every self.files_list_new run exif method
        i = 0
        for file in self.new_files:
            self.Log_exif(file, i)
            i += 1

        #log new exif data to database
        connection = sqlite3.connect(f"{self.folder}/{self.database_name}")
        cursor = connection.cursor()
        date_format = "%Y-%m-%d %H:%M:%S"
        message = cursor.execute(f"INSERT INTO log (modified, count) VALUES('{datetime.datetime.now().strftime(date_format)}', '{len(self.filesOBJ)}')")
        #print(f"INSERT INTO log message: {message.fetchall()}")
        for file in self.filesOBJ:
            rel_path = os.path.relpath(file.pathOBJ, self.folder)
            lat_string = "lat"
            lon_string = "lon"
            message = cursor.execute((f"INSERT INTO photos (path, creation, name, gpslat, gpslon) VALUES ('{rel_path}','{file.date}','{file.name}','{file.gpsDD[lat_string]}','{file.gpsDD[lon_string]}')").replace('\0',''))
            #print(f"INSERT INTO photos message: {message.fetchall()}")
        connection.commit()
        cursor.close()
        connection.close()






    #LOGING EXIF DATA OF FILES, for every file create new object and add it to self.filesOBJ
    def Log_exif(self, filepath, name_unique):
        image = Image.open(filepath)
        info = image.getexif()
        image.close()

        gps_info = info.get_ifd(34853)

        name_unique = File(filepath, info, gps_info)
        self.filesOBJ.append(name_unique)
    
    #HELPING METHOD - RETURNS TRUE/FALSE BASED ON NAMING RULES
    def TestFileName(self, name):
        result = False

        #thing, i WANT to include
        extension = name.split(".")[-1]
        for test in self.file_extensions:
            if (test.upper() in extension.upper()):
                result = True
        #things, i DONT WANT to include (have to be after things i want to)
        for test in self.regex_omit:
            if (re.search(test, name)):
                result = False

        return result
    
    






class File:
    def __init__(self, path, exif, gps_exif):
        self.pathOBJ = path
        self.name = self.pathOBJ.name
        self.exif = exif
        self.gps_exif = gps_exif
        
        try:
            self.date = self.exif[306]
        except:
            print(f"file {self.pathOBJ} has no DATE info")
            self.date = None

        self.gpsDD = {"lat": None, "lon": None}

        #print(self.pathOBJ)
        #print(self.name)
        #print(self.exif)
        #print(self.gps_exif)
        #print(self.date)
        #print(self.gpsDD)

        self.Get_GPSdd()

    def Translate_exifs(self):
        from PIL.ExifTags import TAGS, GPSTAGS
        exif_translate = {}
        gps_translate = {}
        for tagid in self.exif:
            tagname = TAGS.get(tagid, tagid)
            value = self.exif.get(tagid)

            exif_translate[tagname] = value
        for tagid in self.gps_exif:
            tagname = GPSTAGS.get(tagid, tagid)
            value = self.gps_exif.get(tagid)

            gps_translate[tagname] = value

    #returns gps in DD (decimal degree) format
    def Get_GPSdd(self):
        #FROM DMS (degrees, minutes, seconds)
        try:
            lat = self.gps_exif[2]
            lon = self.gps_exif[4]
        except:
            #print(f"file {self.pathOBJ} has no GPS info")
            return

        self.gpsDD["lat"] = round((int(lat[0]) + int(lat[1]) / 60 + int(lat[2]) / 3600), 7)
        self.gpsDD["lon"] = round((int(lon[0]) + int(lon[1]) / 60 + int(lon[2]) / 3600), 7)
        if self.gps_exif[1] == "S": self.gpsDD[lat] = self.gpsDD[lat] * (-1)
        if self.gps_exif[3] == "W": self.gpsDD[lon] = self.gpsDD[lon] * (-1) #North (N) and East (E) are positive; South (S) and West (W) are negative.








#GOOD FOR LATER
#import sqlite3

#connection = sqlite3.connect("library.db")
#cursor = connection.cursor()
#GOOD FOR LATER






#only if .db is new (create some variable in .db, where will be written if .db is fresh)
    #put into .db date of creation of .db and date of last update

#only if .db is new
#cursor.execute("SELECT fresh from fresh")
#result = cursor.fetchall() #type(result) = list
#if (result[0]): #if fresh = true -> 





#create query for listing all files names and saave to some variable
#save path of .db file (it will be starting node). All subdirectories absolute paths will be minus this starting path
#create loop for walking in subdirectories, for every file, evaluate suffix (.jpeg, .png,...)
    #then in every loop, if filename is not already in .db -> log file into .db






if __name__ == "__main__":
    #starting_folder_path = input("Set starting position (folder)").strip()
    #starting_folder_path = "/Volumes/CaeMate/photos"
    #a = Index_photos(starting_folder_path)
    database_path = input("drag .db file to command line; THEN PRESS ANY KEY").strip()
    a = Index_photos(pathlib.Path(database_path).parent, pathlib.Path(database_path).name)

    #print(a.files_list)
    #print(f"files_list_pruned: {a.files_list_pruned}")
    #print(f"new_files: {a.new_files}")