import os
import sys
import io

import SQLAlchemy
import csv


def main():
    print("Hello World!")

def importCSV():
    """Import data using a csv-file"""
    print(">>>>> importCSV <<<<<")

    
    try:
        data = pd.read_csv(books.csv)
        print('>>>>> STORE ROWS IN DB<<<<<')
        processImport(data)
        print('>>>>> DONE STORING ROWS IN DB<<<<<')
        flash('Transactions are stored, you can now process them', 'success')
    except Exception as e:
        print(">>>>> exception <<<<<", e)

def processImport(data):
    # for each record store an entry in database (id+key shoul be unique)
    # isbn,title,author,year
    
    # iterate over rows with iterrows()
    for index, row in data.iterrows():
         # access data using column names
         # Skip headers / title

            
        # Process data
        csvISBN = row[0]
        csvTitle = row[1]
        csvAuthor = row[2]
        csvYear = row[3]
        

        #for row in data:
        params = (csvISBN, csvTitle, csvAuthor, csvYear)

        cursor = db.cursor()
        cursor.execute('''INSERT INTO books(isbn, title, author, year) VALUES(?, ?, ?, ?)''', params)
        db.commit()

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)        


if __name__ == "__main__":
    main()    