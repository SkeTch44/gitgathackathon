from flask import Flask, render_template,\
     request, session, redirect, url_for
from werkzeug.utils import secure_filename
import check_originality
import blockchain
import sqlite3
import dag_db
import shutil
import json
import os
import web3

DAG_DB = "nft_art_gallery.db"
dag_db.prepare_database(DAG_DB)

app = Flask(__name__)
app.secret_key = '1xh5qpfmsos850fl'

cwd = os.getcwd()
nft_save_path = cwd + '/static/nft_gallery'

def register_user(form_obj):
    name = form_obj['name']
    username = form_obj['username']
    password = form_obj['password']
    dob = form_obj['dob']
    
    conn = sqlite3.connect(DAG_DB)

    cur = conn.cursor()
    cur.execute('SELECT * FROM USER_INFO')
    total_registers = len(cur.fetchall())
    
    register_cmd = '''
INSERT INTO USER_INFO VALUES(
'{}', '{}', '{}', '{}', {})
'''.format(username, name, password, dob, total_registers)

    try:
        conn.execute(register_cmd)
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def login_user(form_obj):
    username = form_obj['username']
    password = form_obj['password']

    conn = sqlite3.connect(DAG_DB)
    cur = conn.cursor()
    get_creds_cmd = '''
SELECT PASSWORD, WALLET_INDEX  FROM USER_INFO WHERE USERNAME='{}'
'''.format(username)

    cur.execute(get_creds_cmd)
    try:
        creds = cur.fetchall()[0]
        if creds[0] == password:
            session['username'] = username
            session['index'] = creds[1]
            return True
        else:
            conn.close()
            return False
    except IndexError:
        conn.close()
        return False

def add_nft_db(form_obj, nft_art):
    files_in_gallery = len(os.listdir(nft_save_path))
    art_name = 'art_{}.png'.format(files_in_gallery)
    nft_art.save(secure_filename(art_name))
    if check_originality.is_original(art_name):
        art_path = nft_save_path + "/" + art_name
        shutil.move(art_name, art_path)

        conn = sqlite3.connect(DAG_DB)
        cur = conn.cursor()
        cur.execute('SELECT * FROM NFT_INFO')
        total_nfts = len(cur.fetchall())

        name = form_obj['name']
        desc = form_obj['description']
        price = form_obj['price']
        add_art_cmd = '''
    INSERT INTO NFT_INFO VALUES({}, '{}', '{}', {}, {}, '{}', {})
    '''.format(total_nfts, name, desc, price, session['index'], art_name, 0)

        conn.execute(add_art_cmd)
        conn.commit()
        conn.close()

        user_account = w3.eth.accounts[session['index']]
        blockchain.add_nft(w3, marketplace_contract, name, desc, price, user_account)
        
        return True
    else:
        os.remove(art_name)
        return False

@app.route('/onboard/login', methods=["POST"])
def login_backend():
    if request.method == "POST":
        form_obj = request.form

        logged_in = login_user(form_obj)

        if logged_in:
            return redirect(url_for('homepage'))
        else:
            return render_template('msg.html', msg='Invalid credentials. Please retry')

@app.route('/onboard/register', methods=["POST"])
def register_backend():
    if request.method == "POST":
        form_obj = request.form
        
        register_success = register_user(form_obj)

        if register_success:
            return render_template('msg.html', msg='Registered Successfully. Please Login')
        else:
            return render_template('msg.html', msg='Please try using a new username. This username already exists on our system')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/')
def homepage():
    if 'username' in session:
        usr_account_address = w3.eth.accounts[session['index']]
        title = "Welcome {}".format(session['username'])
        info1 = "Your wallet address: {}".format(usr_account_address)
        usr_balance = blockchain.get_balance(w3, usr_account_address)
        info2 = "Your account balance: {} ETH".format(usr_balance)
        return render_template('index.html', logged=True, title=title, info1=info1, info2=info2)
    else:
        
        return render_template('index.html', logged=False)

@app.route('/user/upload')
def upload_page():
    if "username" in session:
        return render_template("create.html")
    else:
        return render_template('msg.html', msg='Please login before performing this action')

@app.route('/buy/nft/<int:nft_index>')
def buy_nft_page(nft_index):
    if 'username' in session:
        get_info_cmd = '''
SELECT TITLE, PRICE, DESCRIPTION, ART_PATH FROM NFT_INFO WHERE S_NO={}
'''.format(nft_index)
        conn = sqlite3.connect(DAG_DB)
        cur = conn.cursor()
        cur.execute(get_info_cmd)
        nft_info = cur.fetchall()
        nft_info = nft_info[0]
        return render_template('buy.html', name=nft_info[0], price=nft_info[1], description=nft_info[2], art_path=nft_info[3], nft_index=nft_index)
    else:
        return render_template('msg.html', msg='Please login before performing this action')

@app.route('/action/buy/<int:nft_index>')
def buy_nft(nft_index):
    if 'username' in session:
        user_indx = session['index']
        get_price_cmd = '''
    SELECT PRICE FROM NFT_INFO WHERE S_NO={}
    '''.format(nft_index)
        conn = sqlite3.connect(DAG_DB)
        cur = conn.cursor()
        cur.execute(get_price_cmd)
        nft_price= cur.fetchall()
        nft_price = nft_price[0]

        try:
            blockchain.buy_nft(w3, marketplace_contract, nft_index, w3.eth.accounts[user_indx], nft_price[0])
            buy_nft_cmd = '''
        UPDATE NFT_INFO SET OWNER_INDEX={}, ISSOLD=1 WHERE S_NO={}
        '''.format(user_indx, nft_index)
            conn = sqlite3.connect(DAG_DB)
            conn.execute(buy_nft_cmd)
            conn.commit()
            conn.close()

            return render_template('msg.html', msg='You have successfully purchased the NFT!')
        except web3.exceptions.ContractLogicError as error:
            msg = str(error)
            if 'product sold' in msg:
                return render_template('msg.html', msg="This NFT has already been sold")
            elif 'insufficient funds' in msg:
                return render_template('msg.html', msg="Sorry! Your account has insufficient funds to process this request")
            else:
                return render_template('msg.html', msg=msg)
        
    else:
        return render_template('msg.html', msg='Please login before performing this action')

@app.route('/upload/nft', methods=["POST"])
def add_nft():
    if request.method == "POST" and 'username' in session:
        form_obj = request.form
        file_uploaded = add_nft_db(form_obj, request.files['file'])
        if file_uploaded:
            return render_template('msg.html', msg='Your NFT was uploaded to marketplace successfully')
        else:
            return render_template('msg.html', msg='Please upload an original NFT. This one was copied')
    else:
        return render_template('msg.html', msg='Please login before performing this action')

@app.route('/logout')
def logout_user():
    if 'username' in session:
        session.pop('username', None)
        session.pop('index', None)
        return redirect(url_for('login_page'))
    else:
        return render_template('msg.html', msg='You are not logged in yet')

@app.route('/mycollection')
def user_collection():
    if 'username' in session:
        user_index = session['index']
        get_nfts_cmd = '''
    SELECT ART_PATH, PRICE FROM NFT_INFO WHERE OWNER_INDEX={}
    '''.format(user_index)
        conn = sqlite3.connect(DAG_DB)
        cur = conn.cursor()
        cur.execute(get_nfts_cmd)
        info_list = cur.fetchall()
        info_dict = {}
        for i in range(len(info_list)):
            info_dict[i] = (info_list[i][0], "ETH {}".format(info_list[i][1]))
        usr_account_address = w3.eth.accounts[user_index]
        title = "Welcome {}".format(session['username'])
        info1 = "Your wallet address: {}".format(usr_account_address)
        usr_balance = blockchain.get_balance(w3, usr_account_address)
        info2 = "Your account balance: {} ETH".format(usr_balance)
        return render_template('collection.html', title=title, info1=info1, info2=info2, info_dict=info_dict, clickable=False)
    else:
        return render_template('msg.html', msg='Please login before performing this action')


@app.route('/marketplace')
def marketplace():
    if 'username' in session:
        get_nfts_cmd = '''
    SELECT ART_PATH, PRICE, ISSOLD FROM NFT_INFO
    '''
        conn = sqlite3.connect(DAG_DB)
        cur = conn.cursor()
        cur.execute(get_nfts_cmd)
        info_list = cur.fetchall()
        info_dict = {}
        for i in range(len(info_list)):
            if info_list[i][2] == 1:
                info_list_i = (info_list[i][0], "SOLD", 1)
                info_dict[i] = info_list_i
            else:
                info_dict[i] = (info_list[i][0], "ETH {}".format(info_list[i][1]), info_list[i][2])
        usr_account_address = w3.eth.accounts[session['index']]
        usr_balance = blockchain.get_balance(w3, usr_account_address)
        info1 = "Your account balance: {} ETH".format(usr_balance)
        return render_template('collection.html', title='Marketplace', info1=info1, info_dict=info_dict, clickable=True)
    else:
        return render_template('msg.html', msg='Please login before performing this action')

@app.errorhandler(404)
def not_found(e):
    return render_template('msg.html', msg='The page you are looking for was not found')

with open("smart-contracts/abi.json") as abi_file:
    abi = json.load(abi_file)
with open("marketplace_contract.txt") as contract_file:
    contract = contract_file.read().strip()
    contract_address = contract

if __name__ == "__main__":
    w3 = blockchain.connect_to_server("http://127.0.0.1:7545")
    if w3.is_connected():
        print("Connected to ethereum blockchain. Network ID: {}".format(w3.net.version))
        marketplace_contract = blockchain.get_contract(w3, contract_address, abi)
        app.run(debug=True)
    else:
        print("Could not connect to server. Make sure to host the server on 'http://127.0.0.1:7545' and restart Ganache and try again.")
        input("Press enter to close the program")
