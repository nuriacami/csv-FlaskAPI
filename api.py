import os
from threading import Thread
import uuid
from flask import Flask, flash, request, redirect, send_from_directory, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from csvsort import csvsort

# global variables
UPLOAD_FOLDER = ".\\data" 
ALLOWED_EXTENSIONS = {'csv'}

# init Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# allowed extensions checker
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#--------------------------------#
# 1. Large CSV Processing module #
#--------------------------------#
def csv_processing(filename):

    CSV_PATH = ".\\data\\"+filename
    CHUNK_SIZE = 3

    # sort 
    csvsort(CSV_PATH+".csv", [0,1], has_header=True, output_filename = CSV_PATH+"_sorted.csv")
    
    # get chunks
    chunks = pd.read_csv(CSV_PATH+"_sorted.csv", chunksize=CHUNK_SIZE)

    # processing
    i = 0
    for chunk in chunks:
        for row in chunk.values:
            if (i == 0):
                song = row[0]
                date = row[1]
                plays = row[2]
                i = 1
            else:
                if row[0] == song and row[1] == date:
                    plays = plays + row[2]
                
                else:
                    with open (CSV_PATH+"_processed.csv", 'a') as f:
                        f.write(str(song) + "," + str(date) + "," + str(plays) + '\n' )
                    song = row[0]
                    date = row[1]
                    plays = row[2]

    with open (CSV_PATH+"_processed.csv", 'a') as f:
        f.write(str(song) + "," + str(date) + "," + str(plays) + '\n' )

    # remove initial and sorted csv since we only keep the processed csv
    if os.path.exists(CSV_PATH+"_sorted.csv"):
        os.remove(CSV_PATH+"_sorted.csv")
    else:
        print("The file does not exist") 
    
    if os.path.exists(CSV_PATH+".csv"):
        os.remove(CSV_PATH+".csv")
    else:
        print("The file does not exist") 
    

#--------------------------------------------------#
# 2.1. API Endpoint 1: Schedule file to processing #
#--------------------------------------------------#
@app.route('/', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        # Error Handling
        # 1 - check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # 2 - if the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # name the file as the ID of the processing task 
            filename =  str(uuid.uuid4()) 
            # save file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename+".csv")) 

            # asynchronous task processing
            thread = Thread(target=csv_processing, args=[filename]) 
            thread.start()
            
            return {"id": filename}
    
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

#-------------------------------------------#
# 2.2. API Endpoint 2: Download the result. #
#-------------------------------------------#
@app.route('/result')
def download_result():
    filename = request.args.get('id')+'_processed.csv'
    # if the file has been processed, it is downloaded. else, show message.
    if (os.path.isfile(".\\data\\"+filename)):
        return send_from_directory(UPLOAD_FOLDER,filename) 
    else:
        return "Your file is still being processed"