from bottle import get, run, response, post, request
import json, yaml
from dict2xml import dict2xml
import pandas as pd
import sqlite3

users = {
    '12345':{'id':'1', 'email':'@a', 'token':'12345'},
    '67890':{'id':'2', 'email':'@a', 'token':'67890'},
}

messages = {
    'patient':[
        {
            'id':'aaa0381a-4a37-4caf-af5f-aae31933749c',
            'name': 'Karen Hansen', 
            'cpr':'112233-4454',
            'adress': 'Vejen 5, Vejen 6666',
            'access':'*'
        },
        {
            'id':'aaa0381a-4a37-4caf-af5f-hjkjkksksks',
            'name': 'Leif Badingado', 
            'cpr':'556644-1091',
            'adress': 'Roaden 10, Road 8888',
            'access':'*'
        }
    ]  
}
recept = {
                'recept': [
                {
                    'doc': 'Donald Doc',
                    'medicine': 'Morphine',
                    'amount': '200mg'
                }
            ]
}

def row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
            data = {}
            for idx, col in enumerate(cursor.description):
                data[col[0]] = row[idx]
            return data

############################
@get('/provider/<prov_id>/cpr/<cpr>/token/<token>/format/<format>')
def _(prov_id, token, format, cpr):
    try:
        conn = sqlite3.connect('Mandatory.db')
        '''if limit == 0:
            raise Exception('Limit cannot be 0')'''
        if token not in users:
            raise Exception('Token is invalid')
        
        if format == 'JSON':
            response.content_type = 'application/json'
            c = conn.cursor()
            c.row_factory = row_to_dict
            c.execute(f"SELECT * FROM patient WHERE cpr='{cpr}'")
            result = c.fetchall()
            return json.dumps(result)

        elif format == 'XML':
            response.content_type = 'application/xml'
            xml_list = []
            for msg in messages[prov_id]:
                xml_list.append(msg)

            data = '<?xml version="1.0" encoding="UTF-8"?>'
            data += '<data>'
            data += dict2xml(xml_list, wrap='msg', indent=' ')
            data += '</data>'
            return data

        elif format == 'YAML':
            response.content_type = 'application/yaml'
            data = 'messages:' + '\n'
            data += yaml.dump(messages[prov_id])
            return data

        elif format == 'TSV':
            data = pd.DataFrame.from_records(messages[prov_id])
            return data.to_csv(sep='\t', index=False)


    except Exception as ex:
        response.status = 400
        return str(ex)

#TODO: Split request ud så ikke IF ELSE men egne requests!! <-----
#TODO: Post/GET recept og patien data til databasen for alle filtyper!

@post('/provider/<pro_id>/token/<token>/format/<format>')
def _(pro_id, token, format):
    # provider skal være subject(student, teacher....)
    try: 
        conn = sqlite3.connect('Mandatory.db')
        #conn.execute("CREATE TABLE recept (doc char(50), medicine char(50), amount char(8), recept_cpr char(11), FOREIGN KEY(recept_cpr) REFERENCES patient(cpr))")

        if token not in users:
            raise Exception('Token is invalid')

        if format == 'JSON':
            response.content_type = 'application/json'
            message = request.json
            #conn.execute(f"INSERT INTO patient (id, name, cpr, adress, access) VALUES ('{message['id']}', '{message['name']}', '{message['cpr']}', '{message['adress']}', '{message['access']}')")
            #conn.commit()
            print(message)

            return message

        elif format == 'XML':
            response.content_type = 'application/xml'
            message = request.body.getvalue()
            print(message)
            return message

        elif format == 'YAML':
            response.content_type = 'application/yaml'
            message = request.body.getvalue()
            return message

        elif format == 'TSV':
            data = request.body.getvalue()
            print(data)
            return data
        
    
    except Exception as ex:
        response.status = 400
        return str(ex)

############################
run(host='127.0.0.1', port=3000, debug=True, reloader=True)