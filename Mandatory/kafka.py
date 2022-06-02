from bottle import get, run, response, post, request, delete, put
import json, yaml
from dict2xml import dict2xml
import pandas as pd
import sqlite3
import xml.etree.ElementTree as ET

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
# Add CPR and create db table!
prescription = {
                'prescription': [
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

################################################################################################################
# Format JSON
################################################################################################################
@get('/provider/pharmacy/cpr/<cpr>/token/<token>/JSON')
def _(token, cpr):
    try:
        conn = sqlite3.connect('Mandatory.db')
        '''if limit == 0:
            raise Exception('Limit cannot be 0')'''
        if token not in users:
            raise Exception('Token is invalid')
        
        response.content_type = 'application/json'
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM patient JOIN journal ON patient.cpr = journal.patient_cpr WHERE patient.cpr='{cpr}'")
        #c.execute(f"SELECT * FROM patient WHERE cpr in (SELECT date_ FROM journal WHERE patient_cpr='{cpr}')")
        result = c.fetchall()
        return json.dumps(result)

    except Exception as ex:
        response.status = 400
        return str(ex)

@get('/provider/prescription/cpr/<cpr>/token/<token>/JSON')
def _(token, cpr):
    try:
        conn = sqlite3.connect('Mandatory.db')
        '''if limit == 0:
            raise Exception('Limit cannot be 0')'''
        if token not in users:
            raise Exception('Token is invalid')
        
        response.content_type = 'application/json'
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM prescription WHERE cpr='{cpr}'")
        result = c.fetchall()
        return json.dumps(result)
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/pharmacy/token/<token>/JSON')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        response.content_type = 'application/json'
        message = request.json
        conn.execute(f"INSERT INTO patient (id, name, cpr, adress, access) VALUES ('{message['id']}', '{message['name']}', '{message['cpr']}', '{message['adress']}', '{message['access']}')")
        conn.commit()
        print(message)

        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/prescription/token/<token>/JSON')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        response.content_type = 'application/json'
        message = request.json
        conn.execute(f"INSERT INTO prescription (doc, medicin, amount) VALUES ('{message['doc']}', '{message['medicine']}', '{message['amount']}')")
        conn.commit()
        print(message)

        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@put('/provider/pharmacy/cpr/<cpr>/token/<token>/JSON')
def _(token, cpr):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        response.content_type = 'application/json'
        message = request.json

        if message.get('name') is not None:
            print('in name')
            conn.execute(f"UPDATE patient SET name='{message['name']}' WHERE cpr={cpr}")
        if message.get('adress') is not None:
            print('in adress')
            conn.execute(f"UPDATE patient SET adress='{message['adress']}' WHERE cpr={cpr}")
        if message.get('access') is not None:
            conn.execute(f"UPDATE patient SET access='{message['access']}' WHERE cpr={cpr}")
        
        conn.commit()
        return message
    
    except Exception as ex:
        response.status = 400
        print('exeption called!')
        return str(ex)
################################################################################################################
# Format XML
################################################################################################################
@get('/provider/pharmacy/cpr/<cpr>/token/<token>/XML')
def _(token, cpr):
    try:
        conn = sqlite3.connect('Mandatory.db')
        '''if limit == 0:
            raise Exception('Limit cannot be 0')'''
        if token not in users:
            raise Exception('Token is invalid')
        
        response.content_type = 'application/xml'
        xml_list = []
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM patient WHERE cpr='{cpr}'")
        result = c.fetchall()

        for msg in result:
            xml_list.append(msg)
            
        data = '<?xml version="1.0" encoding="UTF-8"?>'
        data += '<data>'
        data += dict2xml(xml_list, wrap='msg', indent=' ')
        data += '</data>'
        return data
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@get('/provider/prescription/cpr/<cpr>/token/<token>/XML')
def _(token, cpr):
    try:
        conn = sqlite3.connect('Mandatory.db')
        '''if limit == 0:
            raise Exception('Limit cannot be 0')'''
        if token not in users:
            raise Exception('Token is invalid')
        
        response.content_type = 'application/xml'
        xml_list = []
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM prescription WHERE cpr='{cpr}'")
        result = c.fetchall()

        for msg in result:
            xml_list.append(msg)
            
        data = '<?xml version="1.0" encoding="UTF-8"?>'
        data += '<data>'
        data += dict2xml(xml_list, wrap='msg', indent=' ')
        data += '</data>'
        return data
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/pharmacy/token/<token>/XML')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        response.content_type = 'application/xml'
        message = request.body.getvalue()
        data = ET.fromstring(message)
        conn.execute(f"INSERT INTO patient (id, name, cpr, adress, access) VALUES ('{data[0][1].text}', '{data[0][2].text}', '{data[0][3].text}', '{data[0][4].text}', '{data[0][0].text}')")
        conn.commit()
        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/prescription/token/<token>/XML')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        response.content_type = 'application/xml'
        message = request.body.getvalue()
        data = ET.fromstring(message)
        conn.execute(f"INSERT INTO prescription (doc, medicine, amount) VALUES ('{data['doc']}', '{data['medicine']}', '{data['amount']}')")
        conn.commit()
        print(message)
        
        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@put('/provider/pharmacy/cpr/<cpr>/token/<token>/XML')
def _(token, cpr):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        response.content_type = 'application/xml'
        message = request.body.getvalue()
        data = ET.fromstring(message)

        for d in data.iter():          
            if d.tag == 'name':
                conn.execute(f"UPDATE patient SET name='{d.text}' WHERE cpr={cpr}")
            if d.tag == 'adress':
                conn.execute(f"UPDATE patient SET adress='{d.text}' WHERE cpr={cpr}")
            if d.tag == 'access':
                conn.execute(f"UPDATE patient SET access='{d.text}' WHERE cpr={cpr}")
        
        conn.commit()
        return message
    
    except Exception as ex:
        response.status = 400
        print('exeption called!')
        return str(ex)

################################################################################################################
# Format YAML
################################################################################################################
@get('/provider/pharmacy/cpr/<cpr>/token/<token>/YAML')
def _(token, cpr):
    try:
        conn = sqlite3.connect('Mandatory.db')
        '''if limit == 0:
            raise Exception('Limit cannot be 0')'''
        if token not in users:
            raise Exception('Token is invalid')
        
        response.content_type = 'application/yaml'
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM patient WHERE cpr='{cpr}'")
        result = c.fetchall()

        data = 'messages:' + '\n'
        data += yaml.dump(result)
        return data
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@get('/provider/prescription/cpr/<cpr>/token/<token>/YAML')
def _(token, cpr):
    try:
        conn = sqlite3.connect('Mandatory.db')
        '''if limit == 0:
            raise Exception('Limit cannot be 0')'''
        if token not in users:
            raise Exception('Token is invalid')
        
        response.content_type = 'application/yaml'
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM prescription WHERE cpr='{cpr}'")
        result = c.fetchall()

        data = 'messages:' + '\n'
        data += yaml.dump(result)
        return data
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/pharmacy/token/<token>/YAML')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        response.content_type = 'application/yaml'
        message = request.body.getvalue()
        data = yaml.safe_load(message)
        conn.execute(f"INSERT INTO patient (id, name, cpr, adress, access) VALUES ('{data['messages'][0]['id']}', '{data['messages'][0]['name']}', '{data['messages'][0]['cpr']}', '{data['messages'][0]['adress']}', '{data['messages'][0]['access']}')")
        conn.commit()
        print(message)
        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/prescription/token/<token>/YAML')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        response.content_type = 'application/yaml'
        message = request.body.getvalue()
        data = yaml.safe_load(message)
        conn.execute(f"INSERT INTO prescription (doc, medicine, amount) VALUES ('{data['doc']}', '{data['medicine']}', '{data['amount']}')")
        conn.commit()
        print(message)
        return message

        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@put('/provider/pharmacy/cpr/<cpr>/token/<token>/YAML')
def _(token, cpr):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        response.content_type = 'application/yaml'
        message = request.body.getvalue()
        data = yaml.safe_load(message)
        print(data)

        for k in data['messages']:
            for i in k.keys():
                if i == 'name':
                    print(k['name'])
                    conn.execute(f"UPDATE patient SET name='{k['name']}' WHERE cpr={cpr}")
                if i == 'adress':
                    print(k['adress'])
                    conn.execute(f"UPDATE patient SET adress='{k['adress']}' WHERE cpr={cpr}")
                if i == 'access':
                    conn.execute(f"UPDATE patient SET access='{k['access']}' WHERE cpr={cpr}")
        
        conn.commit()
        return message

    except Exception as ex:
        response.status = 400
        print('exeption called!')
        return str(ex)
################################################################################################################
# Format TSV
################################################################################################################
@get('/provider/pharmacy/cpr/<cpr>/token/<token>/TSV')
def _(token, cpr):
    try:
        conn = sqlite3.connect('Mandatory.db')
        '''if limit == 0:
            raise Exception('Limit cannot be 0')'''
        if token not in users:
            raise Exception('Token is invalid')
        
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM patient WHERE cpr='{cpr}'")
        result = c.fetchall()
        data = pd.DataFrame.from_records(result)
        return data.to_csv(sep='\t', index=False)
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@get('/provider/prescription/cpr/<cpr>/token/<token>/TSV')
def _(token, cpr):
    try:
        conn = sqlite3.connect('Mandatory.db')
        '''if limit == 0:
            raise Exception('Limit cannot be 0')'''
        if token not in users:
            raise Exception('Token is invalid')
        
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM prescription WHERE cpr='{cpr}'")
        result = c.fetchall()
        data = pd.DataFrame.from_records(result)
        return data.to_csv(sep='\t', index=False)
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/pharmacy/token/<token>/TSV')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        data = request.body.getvalue()
        data = data.decode("utf-8")
        print(data)
        with open('./output.tsv', 'wt') as out_file:
            out_file.write(data)

        file = pd.read_csv('output.tsv', sep='\t')

        id = file['id'].to_list()
        name = file['name'].to_list()
        cpr = file['cpr'].to_list()
        adress = file['adress'].to_list()
        access = file['access'].to_list()
        print(str(id), str(name), str(cpr), str(adress), str(access))
        conn.execute(f"INSERT INTO patient (id, name, cpr, adress, access) VALUES ('{id[0]}', '{name[0]}', '{cpr[0]}', '{adress[0]}', '{access[0]}')")
        conn.commit()
        return data
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/prescription/token/<token>/TSV')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        data = request.body.getvalue()
        data = data.decode("utf-8")
        print(data)
        with open('./output.tsv', 'wt') as out_file:
            out_file.write(data)

        file = pd.read_csv('output.tsv', sep='\t')

        doc = file['doc'].to_list()
        medicine = file['medicine'].to_list()
        amount = file['amount'].to_list()
        conn.execute(f"INSERT INTO prescription (doc, medicine, amount) VALUES ('{doc[0]}', '{medicine[0]}', '{amount[0]}')")
        conn.commit()
        return data
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@put('/provider/pharmacy/cpr/<cpr>/token/<token>/TSV')
def _(token, cpr):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        if token not in users:
            raise Exception('Token is invalid')

        data = request.body.getvalue()
        data = data.decode("utf-8")
        with open('./output.tsv', 'wt') as out_file:
            out_file.write(data)

        file = pd.read_csv('output.tsv', sep='\t')

        name = file.get('name')
        adress = file.get('adress')
        access = file.get('access')

        if name is not None:
            conn.execute(f"UPDATE patient SET name='{name.to_list()[0]}' WHERE cpr={cpr}")
        if adress is not None:
            conn.execute(f"UPDATE patient SET name='{adress.to_list()[0]}' WHERE cpr={cpr}")
        if access is not None:
            conn.execute(f"UPDATE patient SET name='{access.to_list()[0]}' WHERE cpr={cpr}")

        conn.commit()
        return data

    except Exception as ex:
        response.status = 400
        print('exeption called!')
        return str(ex)
################################################################################################################
# Delete Pharmacy
@delete('/provider/pharmacy/cpr/<cpr>/token/<token>/d')
def _(token, cpr):
    try:
        conn = sqlite3.connect('Mandatory.db')
        
        if token not in users:
            raise Exception('Token is invalid')
        
        c = conn.cursor()
        c.execute(f"DELETE FROM patient WHERE cpr={cpr}")
        return f'Patient {cpr} deleted!'
    
    except Exception as ex:
        response.status = 400
        return str(ex)


################################################################################################################
run(host='127.0.0.1', port=3000, debug=True, reloader=True)