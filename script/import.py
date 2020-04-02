'''
Import excel data to sqlite:
    python script/import.py '<file-location-path>' '<db-name>'
    ex:
    python script/import.py '/Users/immap/Documents/Project/GIZDashboard/exceldata/city_of_village.xlsx' 'reference_cityvillage'
'''

import sys
import sqlite3
import pandas as pd
from pandas.io import sql

def ImportExcel():
    # print(sys.argv[:3][1])
    Filepath = sys.argv[:3][1]
    DBname = sys.argv[:3][2]
    connection = sqlite3.connect('/Users/immap/Documents/Project/GIZDashboard/backend/db.sqlite3')
    excelfile = pd.read_excel(Filepath)
    data = pd.DataFrame(excelfile)

    cursor=connection.cursor()

    cols = "`,`".join([str(i) for i in data.columns.tolist()])
    for i,row in data.iterrows():
        # sql = "INSERT INTO `"+DBname+"` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)" #for sql
        sql = "INSERT INTO `"+DBname+"` (`" +cols + "`) VALUES (" + "?,"*(len(row)-1) + "?)" #for sqlite
        cursor.execute(sql, tuple(row))
        connection.commit()

if __name__ == "__main__":
    ImportExcel()