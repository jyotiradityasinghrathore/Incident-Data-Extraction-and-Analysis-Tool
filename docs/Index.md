# Documentation
This file includes explanation about the extraction algorithm and how the algorithm is implemented in python. A sample minimum viable product (MVP) implementation of this algorithm is located [here](../notebooks/MVP.ipynb).

## Overview
> See [Run on local system](../README.md) to run this project locally.

This utility takes the Incident PDF file URL as the input and returns the summary of Incident Natures found and their counts from the given PDF. The extraction process is as follows.
![Process-Flow.png](./resources/Process-Flow.png)

Explanation about each module can be found later down the document (or follow the below quick links).
- [Parser](#parser)
- [Storer](#storer)
- [main.py](#mainpy)



### fetch_incidents(url) -> list
This function used built-in `urllib` to reach out to the given resource URL and tries to get the resource as bytes. Then we store the bytes in a temporary file created using built-in `tempfile` package.

There is a possibility of supplying invalid URL to the utility. In doing so `urllib` raises an exception from [utllib.error](https://docs.python.org/3/library/urllib.error.html#module-urllib.error) or [ValueError](https://docs.python.org/3/library/exceptions.html#ValueError) exception if the URL has invalid schema (http protocol).

### extract_incidents(temp_file) -> list
The above function `fetch_incidents` depends on `extract_incidents` to create an unparsed 2-dimentional list containing incidents from each page using python's built-in `re` package and third-party `PyPDF2` package. This function performs the following tasks.

1. Read all pages content using `PyPDF2` and create an unparsed, unformatted string.

    ![Unparsed-Page-Data](./resources/Downloader-P1.png)
2. There is some unnecessary content which is not incident data (like table headers, PDF titles). The function uses `re` to remove those unwanted content using `re.sub`.

    ![Unwanted-Content-Removal](./resources/Downloader-P2.png)
3. Later, using `re.sub` the utility add a row sperator `\n;;` between each row.

    ![Added-Row-Seperator](./resources/Downloader-P3.png)
4. Finally, the utility uses `re.findall` to extract all rows from the file using two seperate regular expressions which uses the special row seperator `\n;;`.
    * Extracts rows with either all 5 columns present or 4 columns present using `(\d+/\d+/\d{4}.\d+:\d\d)\n(\d{4}-\d{8})\n([\w,\.;#\'<>&\(\) /-]*)\n([\w /]*)\n([\w /]*)\n;;`
    * Extracts rows with location and nature column data missing using `(\d+/\d+/\d{4}.\d+:\d\d)\n(\d{4}-\d{8})()()\n([\w /]*)\n;;`

#### Regular expressions explanation
Each row of incidents file contains Date Time, Incident Number, Location, Incident Nature and Incident ORI. Each column of the row has unique characteristics based on which the above regular expression was derived. Those characteristics are as follows.

| Column Name  | Regular Expression  | Example Values | Comment |
|-----------|----------|-------------|-------------|
|Date Time|`\d+/\d+/\d{4}.\d+:\d\d`|2/1/2022 0:04|Fixed datetime format|
|Incident Number|`\d{4}-\d{8}`|2022-00001588|Fixed format|
|Location|`[\w,\.;#\'<>&\(\) /-]*`|2113 GODDARD AVE, W MAIN ST / 24TH AVE SW, 35.2046561833333;-97.4720664|Contains numbers, alphabets (uppercase), spaces and special characters (including `,.;#<>'&()-`). This [Sample File](../tests/resources/sample.pdf) contains some such possible special characters|
|Nature|`[\w /]*`|Traffic Stop, Disturbance/Domestic |Contains alphabets (lowercase and uppercase) along with space and slash (`/`) special character|
|Incident ORI|`[\w /]*`|OK0140200, EMSSTAT, 14005|Contains alphabets (uppercase) and numbers|

## Parser
[`parser.py`](../project0/parser.py) converts the 2-dimentional list of incidents data into `Incident` python class objects, which is used later down the extraction process.

This file contains the following class and funtion.
- [Incident](#class-incident)
- [extract_incidents](#extract_incidentsraw_incidents---listincident)

### class Incident
This class models each incident row. This class contains `__eq__` which is used by python when equality `==` operator is applied between two different Incident objects.

### extract_incidents(raw_incidents) -> list[Incident]
This function goes through each raw incident in the `raw_incidents` and create an `Incident` object. Which is stored in a list to be returned along with other parsed incidents

## Storer
[`storer.py`](../project0/storer.py) contains the code to perform the following functionalities.
1. Abstracts the database functionality of creating, adding and retrieving incident data and
2. Create the database abstraction

This file contains the following class and funtions.
- [create_db](#create_db---normanpddb)
- [NormanPdDb](#class-normanpddb-database-abstraction)

### create_db() -> NormanPdDb
create_db creates a new sqlite3 database file in the current working directory if it does not exist and returns the `NormanPdDb` object, which is used to perform database operations later.

The default name for the sqlite3 file used is `normanpd.db`, unless specified during `create_db()` call

### class NormanPdDb (Database Abstraction)
This class acts as the database layer for this utility. This abstraction uses built-in `sqlite3` package to interact with the file-based sqlite database. This class contains the following methods.
- [check_con](#check_conself---bool)
- [add_incidents](#add_incidentsself-incidents---int)
- [get_stats](#get_statsself---str)

### check_con(self) -> bool
check_con checks if the database file was connected successfully and returns `True`. If the database connecting attempt raised any exception, this function just returns `False` indicating failure of connecting to the database

### add_incidents(self, incidents) -> int
add_incidents opens the connection to sqlite3 database using `with` resource manager. Later, creates a `sqlite3.Cursor` object from the connection using the `with` resource manager and performs the following operations.
1. Drop the table `incidents` if it already exists
2. Create the table `incidents` and
3. Lastly, insert the incidents into the newly created table
4. Finally the function returns the number of changes done to the database, indicating the number of insert operations performed.

In case any exception was raised while deleting old table, creating new table or inserting new incidents into the table, the function returns -1 indicating something went wrong.

### get_stats(self) -> str
get_stats creates `sqlite3.Connection` and `sqlite3.Cursor` objects using `with` resource manager and fetch's the natures and their count from the incidents table. The sql command used to fetch the statistics is `SELECT nature, count(*) FROM incidents WHERE IFNULL(nature, '') != '' GROUP BY nature ORDER BY count(*) DESC, nature ASC`

> Note: The above command does not include empty incident count. This is done using `WHERE IFNULL(nature, '') != ''`.

## main.py
[`main.py`](../main.py) combines all the three modules (downloader, parser and storer) and performs the following functionalities.
1. Used the built-in `argparse` package to accept the PDF URL from the command line as an argument.
2. Then firstly, sends that URL to `downloader.fetch_incidents` to get the incidents as an unparsed 2-dimentional list.
3. Secondly, sends the unparsed list to `parser.extract_incidents` to convert the unparsed incidents to `Incident` type objects.
4. Later, create a database and resets the incidents table if the database was created earlier and inserts the extracted rows into the database using `storer.create_db` and `db.add_incidents`.
5. Lastly if the rows were successfully inserted, the file calls `db.get_stats` to retrieve the final summary of Incident Natures and Counts.