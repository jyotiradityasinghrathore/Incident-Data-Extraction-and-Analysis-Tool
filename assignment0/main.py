import argparse
from assignment0 import fetchincidents, create_database, extractdata_populatedb, status

def main(url):
    # Get incident data
    inc_data = fetchincidents(url)

    # Create new database
    db = create_database()

    # Extract data and populate db
    extractdata_populatedb(db, inc_data)
    
    # Print incident count
    status(db)


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--incidents", type=str, help="Incident summary url")
    args = parser.parse_args()
    if args.incidents:
        url = args.incidents
        main(url)

