def importCSV():
    """Import data using a csv-file"""
    print(">>>>> importCSV <<<<<")

    if request.method == "POST":
        # Read CSV file
        print('>>>>> POST CSV <<<<<')
        if not request.files["fileX"]:
            flash('Missing import file, please select a CSV-file from your computer', 'danger')
            return render_template("import.html") 
        try:
            data = pd.read_csv(request.files["fileX"], sep=";")
            print('>>>>> STORE ROWS IN DB<<<<<')
            processImport(data)
            print('>>>>> DONE STORING ROWS IN DB<<<<<')
            flash('Transactions are stored, you can now process them', 'success')
        except Exception as e:
            print(">>>>> exception <<<<<", e)
            flash('Invalid file or a database error, send an email to slackbyte8@gmail.com', 'danger')
        return redirect("/")
    else:
        print(">>> /GET <<<")
        flash('Select your csv-file to import the suspense-accounts to be matched', 'info') 
        return render_template("import.html")   