## Steps for installation and run the program
1. **Create a virtual environment:**
`python3 -m venv venvname`
where venvname is the name of your virtual environment.

2. **Install the requirements needed:**
`pip install -r requirements.txt`

3. **Create an empty folder named 'data'** in this same directory.

4. **Run the python program:** in our case, our program is on api.py.
 `flask --app api run`

5. **Go to the IP adress 127.0.0.1:5000** (assuming that you use the default Flask settings).

6. **Upload the Input CSV file:** click on Select File button, then select the Input CSV file from
your computer and finally click on the Upload button.

7. **Copy the ID of the task.**

8. **Go to http://127.0.0.1:5000/result?id=IDTASK**, where IDTASK is the ID obtained in the previous step. If the processing has been finished, the Output CSV file will be downloaded.

---------------------------

### Notes on the CSV processing module:
The module starts by sorting the Input CSV file by two columns: song and date. In this way,
we make sure that all equal instances are consecutive throughout the file. In order to consider
files that can be larger than the available memory, we do the reading in chunks*. Then, each
instance is compared with the following one: if the song and the date coincide, the sum of the
number of plays is made; otherwise, the first instance is saved into the Output CSV file with
the computation of the total number of plays for date.

The computational complexity of this processing can be of the order of O(*n* log *n* + *n*), where *n*
is the number of rows of the Input CSV file, O(*n* log *n*) is the complexity of sorting a dataset
and O(*n*) corresponds to the complexity of iterating over all the rows.

* *As our particular input example has only 7 observations, we set the chunk size to 3. However,
for large files it would be appropriate to consider a more suitable chunksize value. This can be
easily set on the CSV processing module itself*.

---------------------------

### Notes on the API and Asynchronous Task Processing:
- The API has been created with the framework Flask. In addition, an HTML form has been
coded in order to upload the input file properly.
- The Flask API already allows to receive further requests while the previous file is still
being processed.
- The Python's Thread class has been used in order to get the task ID before the file has
been fully processed.
- In the case that we wanted to use this API without having to access to the web browser,
we could call it inside a script:
  - In a Windows Powershell v7 (similar for Linux with curl), the following instruction
uploads the Input CSV file and it shows us the ID task: 
  `Invoke-WebRequest -Uri http://127.0.0.1:5000 -Method POST -Form @{file=Get-Item input.csv}`
  - Then, we can retrieve the processed file, which will be saved in the folder where we
are running Powershell:
  `Invoke-WebRequest -Uri http://127.0.0.1:5000/result?id=IDTASK -Method GET`

