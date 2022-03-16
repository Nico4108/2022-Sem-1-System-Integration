from bottle import get, run, view, default_app, request, route, template, response
import jwt, time, random, requests
from get_api_key import api_key
import sqlite3

##############################
def jwtFunc():
    cpr = "12345"
    iat = int(time.time())
    exp = iat + 600000
    encoded_jwt = jwt.encode({"cpr": cpr, "iat": iat, "exp": exp}, "secret", algorithm ="HS256")
    print(encoded_jwt)
    return encoded_jwt


##############################
#@get("/")
#@view("index")
@route('/')
def _():
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

    phone = request.forms.get('phone')
    print(phone)

    # Send code to phone
    try:
        payload = {"to_phone": phone, "message": four_code, "api_key":api_key}
        r = requests.post("https://fatsms.com/send-sms", data=payload)
        print(r.status_code)
    except:
        return r.status_code    

    # Connect to database
    try:
        conn = sqlite3.connect('Mandatory1.db')
        conn.execute(f"INSERT INTO codes (phone, fourcode) VALUES ({phone}, {four_code})")
        conn.commit()

        # Show data
        c = conn.cursor()
        c.execute("SELECT * FROM codes")
        result = c.fetchall()
        print(result)
    except Exception as ex:
        print(ex)
    # MUST CLOSE DB!!
    finally:
        conn.close()

    return template('jwt')
    
##############################

@route('/jwt_code', method='POST')
def four_code():
    try:
        code = request.forms.get("four_code")
        
        conn = sqlite3.connect('Mandatory1.db')
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