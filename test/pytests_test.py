# import pytest
from unittest.mock import MagicMock, patch
from assignment0 import assignment0

url2 = ("https://www.normanok.gov/sites/default/files/documents/2024-01/2024-01-07_daily_incident_summary.pdf")

def test_list_sanity():
    x = assignment0.fetchincidents(url2)
    assert x is not None

def test_create_db():
    with patch('sqlite3.connect') as mock_connect:
        conn = assignment0.create_database()
        mock_connect.assert_called_with('resources/normanpd.db')

def test_extractdata_populatedb():
    mock_conn = MagicMock()
    mock_pdf_reader = MagicMock()  
    result = assignment0.extractdata_populatedb(mock_conn, mock_pdf_reader)
    assert result == True
