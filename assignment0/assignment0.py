from pypdf import PdfReader
import urllib.request
import io
import sqlite3
from sqlite3 import Error
import re


def create_database():
    try:
        conn = sqlite3.connect('resources/normanpd.db')
    except Error as e:
        print(e)
    
    cursor = conn.cursor()
    cursor.execute('''DROP TABLE IF EXISTS incidents''')
    command1 = """CREATE TABLE IF NOT EXISTS incidents (
        date DATE,
        incident_number TEXT,
        location TEXT,
        nature TEXT,
        incident_ori TEXT
        )"""  
    cursor.execute(command1)
    conn.commit()
    return conn

def fetchincidents(url):
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"                          
    data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()
    remote_file_bytes = io.BytesIO(data)
    reader = PdfReader(remote_file_bytes)
    return reader



def extractdata_populatedb(conn, inc_data):
    cursor = conn.cursor()
    num_pages = len(inc_data.pages)
    for i in range(0, num_pages):
        page = inc_data.pages[i]
        text = page.extract_text()
        if i == 0:
            text = text.replace('Date / Time Incident Number Location Nature Incident ORI', '') 
            text = text.replace('NORMAN POLICE DEPARTMENT', '') 
            text = text.replace('Daily Incident Summary (Public)', '')     
        text = text.replace('\n', '')
        pattern = r'(\d{1,2}/\d{1,2}/\d{4}.*?)(?=\d{1,2}/\d{1,2}/\d{4}|$)'
        table_text=re.findall(pattern, text)

        if i == num_pages - 1:
            table_text.pop(len(table_text) - 1)

        for k in range(0, len(table_text)):
            table_text[k] = table_text[k].replace('\n', '')
            ln_text = table_text[k].split(' ')
            string = ''
            end_dict = {'Date / Time': ln_text[0]+' '+ln_text[1]}
            end_dict['Incident Number'] = ln_text[2]
            end_dict['Incident ORI'] = ln_text[-1]
            ln_text.remove(ln_text[0])
            ln_text.remove(ln_text[0])
            ln_text.remove(ln_text[0])
            ln_text.remove(ln_text[-1])

            for j in range(0, len(ln_text)):
                if any(c.islower() for c in ln_text[j]) :
                    l = len(ln_text[j-1])
                    if ln_text[j-1][l-3:] == 'MVA':
                        string = 'MVA ' + string
                    for a in range (j, len(ln_text)):
                        if ln_text[a-1] == '911':
                            string += ln_text[a-1] + ' '
                        string += ln_text[a] + ' ' 
                    break 
                elif ln_text[j] == 'COP':
                    string += ln_text[j] + ' '

                elif ln_text[j] == 'EMS':
                    string += ln_text[j] + ' '

                elif ln_text[j] == 'DDACTS':
                    string += ln_text[j] + ' '

            if string.strip() == 'Breathing Problems 1400':
                string = 'Breathing Problems'

            elif string.strip() == 'Assault EMS Needed 1400':
                string = 'Assault EMS Needed'

            elif string.strip() == 'RAMPMotorist Assist':  
                string = 'Motorist Assist'

            elif string.strip() == 'Sick Person 1400':  
                string = 'Sick Person'

            end_dict['Incident Type'] = string.strip()
            end_dict['Location'] = ' '.join(ln_text).replace(string.strip(), '').strip()
            try:
                cursor.execute("INSERT INTO incidents VALUES (?, ?, ?, ?, ?)", (end_dict['Date / Time'], end_dict['Incident Number'], end_dict['Location'], end_dict['Incident Type'], end_dict['Incident ORI']))
                conn.commit()
            except Error as e:
                print("Data not fetched!! ", e)
                print(end_dict)

    return True

def status(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('''select nature, count(distinct incident_number) from incidents 
                            group by nature 
                            order by count(incident_number) desc, nature asc
                            ''')
        
    except Error as e:
        print('Data not fetched!!: ', e)
    
    for row in cursor.fetchall():
        print (*row, sep = '|')
    