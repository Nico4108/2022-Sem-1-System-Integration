from bottle import run, default_app, request, route, template, redirect
import jwt, time, random
#from get_api_key import api_key
import sqlite3
from send_email import send_email
from private_info import sender_email, phonenumber, api_key
import requests

cpr_ref = ''
#MitID
##############################

@route('/')
def _():
    return template('mitid')

@route('/jwt_mitid', method='POST')
def get_mitid_jwt():
    try:
        token = request.json
        print ('jwt String is:', token)
        print(token.get('jwt')) 
        try:
            global ref_code
            ref_code = jwt.decode(token.get('jwt'), key='secret', algorithms='HS256')
            print(jwt.decode(token.get('jwt'), key='secret', algorithms='HS256'), "_________INFO FROM SANTIAGO")
            #print(ref_code['cpr'])
            #cpr_ref = ref_code['cpr']
        except:
            return "Wrong JWT"
        four_code = random.randint(1111, 9999)
        try:
            payload = {"to_phone": phonenumber, "message": four_code, "api_key":api_key}
            r = requests.post("https://fatsms.com/send-sms", data=payload)
            print(r.status_code)
        except:
            print("No SMS for You") 
        try:
            conn = sqlite3.connect('Mandatory.db')
            #conn.execute('CREATE TABLE IF NOT EXISTS codes ([email] TEXT, [fourcode] TEXT)')
            #conn.execute("CREATE TABLE doctor (cpr char(50), name char(40), token char(255))")
            #conn.execute("CREATE TABLE pharma (cpr char(50), name char(40), token char(255))")
            #conn.execute(f"INSERT INTO doctor (cpr, name, token) VALUES ('221085-4079', 'Carl', '288185799053')")
            #conn.execute(f"INSERT INTO pharma (cpr, name, token) VALUES ('010792-2078', 'Jens', '844534679260')")
            conn.execute(f"INSERT INTO codes (email, fourcode) VALUES ('{phonenumber}', {four_code})")
            conn.commit()
            # Show data
            c = conn.cursor()
            c.execute("SELECT * FROM codes")
            result = c.fetchall()
            print(result, '<----1')
        except Exception as ex:
            print(ex, '<----2')
        # MUST CLOSE DB!!
        finally:
            conn.close()
        return 
    except:
        return "JWT Token is invalid!"

@route('/jwt')
def index():
    return template('jwt')

@route('/jwt_code', method='POST')
def four_code():
    try:
        code = request.forms.get("four_code")
        conn = sqlite3.connect('Mandatory.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM codes WHERE fourcode={code}")
        code_result = c.fetchall()
        print(ref_code['cpr'], '________ CPR_REF')
    except:
        return template('jwt')
    # MUST CLOSE DB!!
    
        
    if code_result:
        print(code_result)
        token_doctor = c.execute(f"SELECT token FROM doctor WHERE cpr='{ref_code['cpr']}'")
        t_doctor= token_doctor.fetchall()
        if t_doctor:
            return f"Token: {t_doctor[0]}"

        token_pharma = c.execute(f"SELECT token FROM pharma WHERE cpr='{ref_code['cpr']}'")
        t_pharma= token_pharma.fetchall()
        if t_pharma:
            return f"Token: {t_pharma[0]}"
        conn.close()
        #msg = 'You are logged in'
        #return template('welcome')
    else:
        #msg = 'Wrong Code, please try again!'
        return template('jwt')

##############################

try:
    import production
    application = default_app()
except:
    run(host="127.0.0.1", port=3333, debug=True, reloader=True, server="paste")