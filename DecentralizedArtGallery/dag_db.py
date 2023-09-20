'''
this script, dag_db.py (abbreviated for 'digital art gallery database') setups the database that is required to hold all the information at backend
'''

# importing module to work with sqlite3
# sqlite is a crossplatform database engine that can work without setup
import sqlite3

# sqlite command to create table to hold user information
user_info_cmd = '''
CREATE TABLE IF NOT EXISTS USER_INFO(
USERNAME VARCHAR(255) PRIMARY KEY,
NAME VARCHAR(255) NOT NULL,
PASSWORD VARCHAR(255) NOT NULL,
DOB DATE NOT NULL,
wALLET_INDEX TINYINT UNIQUE NOT NULL);'''

# sqlite command to create table to hold nft information
nft_info_cmd = '''
CREATE TABLE IF NOT EXISTS NFT_INFO(
S_NO TINYINT PRIMARY KEY NOT NULL,
TITLE VARCHAR(255) NOT NULL,
DESCRIPTION TEXT NOT NULL,
PRICE FLOAT NOT NULL,
OWNER_INDEX TINYINT NOT NULL,
ART_PATH TEXT NOT NULL,
ISSOLD TINYINT NOT NULL);'''

def prepare_database(db_name = "nft_art_gallery.db"):
    '''function that accepts the name of a database and setup the database'''
    
    print("Preparing database")

    conn = sqlite3.connect(db_name) # connect to database
    
    conn.execute(user_info_cmd) # prepare user information table
    conn.execute(nft_info_cmd) # prepare nft information table
    conn.close() # close the database cconnection
    print("Database is now ready")

if __name__ == "__main__":
    prepare_database("nft_art_gallery.db") # call the function 'prepare_database' with argument 'nft_art_gallery' to create a database with this name
