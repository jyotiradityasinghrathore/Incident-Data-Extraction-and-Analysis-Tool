# CIS6930SP24-ASSIGNMENT0

## Author: Jyotiraditya

## Assignment Description:
This assignment involves developing a Python program to extract incident data from a PDF document, populate a SQLite database with the extracted data, and display the status of incidents.

## How to Install:
1. Clone the repository on your system:
    ```sh
    $ git clone https://github.com/jyotiradityasinghrathore/cis6930sp24-assignment0.git
    $ cd cis6930sp24-assignment0
    ```

2. Utilizing Pipenv, install prerequisites:
    ```sh
    $  pipenv install
    ```
3. Verify Installation:
    After the installation is complete, you can verify that
    pipenv is installed correctly by running:
    ```sh
    $  pipenv --version
    ```
4. Install PyPDF2: 
    PyPDF2 is a dependency for the project. You can install it using pipenv.
    ```sh
    $ pipenv install PyPDF2
    ```    
## How to run
1. To run the program, use the following command:
    ```sh
    $ pipenv run python assignment0/main.py --incidents <url>
    ```
2. below are the screenshots from the VScode output.
    [Screenshot 1](https://drive.google.com/file/d/1S0-N8wr_3sZlaTmLc44uXQa1dErenqit/view?usp=sharing)
    [Screenshot 2](https://drive.google.com/file/d/1kVxciUtwtkKuhPZ49_xf_IdwbwDTlyv-/view?usp=sharing)

## Files

- `main.py`: Contains the main function to execute the program. It fetches incident data, creates a database, extracts data from the PDF, populates the database, and prints a summary of incidents.

- `assignment0.py`: Contains helper functions to fetch incidents from a URL, create a SQLite database, extract data from the PDF, populate the database, and print the status of incidents.

## Function Descriptions

### `fetchincidents(url)`

This function takes a URL pointing to a PDF file containing incident data as input. It fetches the PDF content from the URL, reads it using PyPDF, and returns the PdfReader object.

### `create_database()`

This function creates a new SQLite database named `normanpd.db` if it doesn't exist already. It defines a table named `incidents` with columns for date, incident number, location, nature, and incident ORI. If the table already exists, it drops the existing table and recreates it.

### `extractdata_populatedb(conn, inc_data)`

This function extracts data from the provided PdfReader object `inc_data` and populates the SQLite database `conn` with the extracted data. It iterates over each page of the PDF, extracts text, parses it to identify incident details, and inserts them into the database.

### `status(conn)`

This function retrieves data from the SQLite database `conn` and prints a summary of incidents. It counts the occurrences of each incident type and prints them in descending order of frequency.


## Bugs/Assumptions
-  The program operates under the assumption that there may be instances where the "location" and "nature" columns could be empty for one or more rows of data.
- Additionally, it is assumed that the first two columns, "Date / Time" and "Incident Number," will consistently appear in the data.
