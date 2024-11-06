#ask, what path to create html in. If no parametr, take current path in which .py file is
#dont forget to show in html date of creation and last update
#would be great, if in html would be button, for date to choose from
    #will be created more .html files, then they would show only certain files on map API
import pathlib
import sqlite3
from datetime import datetime

def Create_HTML(database_path, html_filename, base_path = None):
    database_name = pathlib.Path(database_path).name
    if base_path == None: base_path = database_path
    
    #STARTING TESTS
    if not (pathlib.Path(database_path).is_file()):
        input(f"{database_name} was not found in {database_path}. Please fix problem and run script again. The script is now closing. Press any key to continue...")
        return
    
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM photos")
    result = cursor.fetchall()
    cursor.close()
    connection.close()

    result_list = []
    for row in result:
        if not (dict(row)["gpslat"] == "None" and dict(row)["gpslon"] == "None"):
            result_list.append(dict(row))

    with open(pathlib.Path(pathlib.Path(base_path) / "index_TEMPLATE.html"), "r") as file:
        template = file.read()
        print("file TEMPLATE read succesfully")
    template = template.split("/*PLACEHOLDER_FOR_DATA_INSERTION*/")

    file_str = template[0]
    file_str += (str(result_list))
    file_str += f";\n my_global_variable_F['created'] = '{datetime.today().strftime('%Y-%m-%d')}';"
    file_str += template[1]

    #print(template)
    #print(file_str)


    with open(pathlib.Path(database_path).parent / html_filename, "w") as file:
        file.write(file_str)
        
        #file.write(template[0])

        #file.write("[")
        #for x in result_list:
        #    file.write(x)
        #file.write("]")
        #file.write(str(result_list))

        #file.write(template[1])
    print("file written")


if __name__ == "__main__":
    database_path = input("drag .db file to command line; THEN PRESS ANY KEY").strip()
    Create_HTML(database_path, "index.html")
    print("file index.html succesfully created - END OF SCRIPT")