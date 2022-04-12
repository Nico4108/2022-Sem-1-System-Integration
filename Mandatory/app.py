from bottle import get, run, view, default_app, request, route, template, response
import jwt, time, random, requests
from get_api_key import api_key
import sqlite3
from send_email import send_email

##############################
def jwtFunc():
    cpr = "12345"
    iat = int(time.time())
    exp = iat + 600000
    encoded_jwt = jwt.encode({"cpr": cpr, "iat": iat, "exp": exp}, "secret", algorithm ="HS256")
    print(encoded_jwt)
    return encoded_jwt

#MitID
##############################

@route('/')
def _():
    #jwt = jwtFunc()
    return template('mitid')

@route('/jwt_mitid', method='POST')
def get_mitid_jwt():
    try:
        token = request.json
        print ('jwt String is:', token)
        print(token.get('jwt'))
        jwt.decode(token.get('jwt'), key='secret', algorithms='HS256')
        
        jwt = jwtFunc()
        return template('index', data=jwt)
        #return 'welcome'
    except:
        return "JWT Token is invalid!"

##############################
#@get("/")
#@view("index")
@route('/index')
def index():
    jwt = jwtFunc()
    return template('index', data=jwt)


##############################
@route('/jwt', method='POST')
def get_jwt():
    try:
        token = request.forms.get("print_JWT")
        print ('jwt String is:', token)
        jwt.decode(token, key='secret', algorithms='HS256')
    except:
        return "JWT Token is invalid!"

    four_code = random.randint(1111, 9999)
    print(four_code)

    email = request.forms.get('email')
    print(email, type(email))

    # Send code to phone
    try:
        send_email(email, four_code)
    except Exception as ex:
        return ex

    # Connect to database
    try:
        conn = sqlite3.connect('Mandatory.db')
        #conn.execute('CREATE TABLE IF NOT EXISTS codes ([email] TEXT, [fourcode] TEXT)')
        #conn.execute("CREATE TABLE codes (email char(50), fourcode char(4))")
        conn.execute(f"INSERT INTO codes (email, fourcode) VALUES ('{email}', {four_code})")
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

    return template('jwt')
    
##############################

@route('/jwt_code', method='POST')
def four_code():
    try:
        code = request.forms.get("four_code")
        
        conn = sqlite3.connect('Mandatory.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM codes WHERE fourcode={code}")
        code_result = c.fetchall()
    except:
        return template('jwt')
    # MUST CLOSE DB!!
    finally:
        conn.close()
        
    if code_result:
        print(code_result)
        #msg = 'You are logged in'
        return template('welcome')
    else:
        #msg = 'Wrong Code, please try again!'
        return template('jwt')

##############################

try:
    import production
    application = default_app()
except:
    run(host="127.0.0.1", port=3333, debug=True, reloader=True, server="paste")