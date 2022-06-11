from bottle import get, run, response, post, request, delete, put
import json, yaml
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dict2xml import dict2xml
import pandas as pd
import sqlite3
import xml.etree.ElementTree as ET

def row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
            data = {}
            for idx, col in enumerate(cursor.description):
                data[col[0]] = row[idx]
            return data

def get_doc_token():
    conn = sqlite3.connect('Mandatory.db')
    c = conn.cursor()
    c.row_factory = row_to_dict
    c.execute(f"SELECT token FROM doctor")
    doctor_token = c.fetchall()
    #doc_token = doctor_token[0]['token']
    doc_token = list(doctor_token[0].values())
    return doc_token

def get_pharma_token():
    conn = sqlite3.connect('Mandatory.db')
    c = conn.cursor()
    c.row_factory = row_to_dict
    c.execute(f"SELECT token FROM pharma")
    pharma_token = c.fetchall()
    pharmacy_token = list(pharma_token[0].values())
    return pharmacy_token

################################################################################################################
                                                # Format JSON
################################################################################################################
@get('/provider/patient/cpr/<cpr>/limit/<limit>/token/<token>/JSON')
def _(token, cpr, limit):

    try:
        conn = sqlite3.connect('Mandatory.db')
        '''if limit == 0:
            raise Exception('Limit cannot be 0')'''
        #print(doctor_token[0]['token'])
        print(type(limit))
        if limit == '0':
            raise Exception('Limit must be greater than 0')

        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')
        
        
        response.content_type = 'application/json'
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM patient JOIN journal ON patient.cpr = journal.patient_cpr WHERE patient.cpr='{cpr}' LIMIT {limit}")
        #c.execute(f"SELECT * FROM patient WHERE cpr in (SELECT date_ FROM journal WHERE patient_cpr='{cpr}')")
        result = c.fetchall()
        return json.dumps(result)

    except Exception as ex:
        response.status = 400
        return str(ex)

@get('/provider/prescription/cpr/<cpr>/limit/<limit>/token/<token>/JSON')
def _(token, cpr, limit):
    try:
        conn = sqlite3.connect('Mandatory.db')
        if limit == '0':
            raise Exception('Limit must be greater than 0')
        pharma_token = get_pharma_token()
        if token not in pharma_token:
            raise Exception('Token is invalid')
        
        response.content_type = 'application/json'
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM prescription WHERE prescription_cpr='{cpr}' ORDER BY prescription_id DESC LIMIT {limit}")
        result = c.fetchall()
        return json.dumps(result)
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/patient/token/<token>/JSON')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
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

        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')

        response.content_type = 'application/json'
        message = request.json
        conn.execute(f"INSERT INTO prescription (doc, medicine, amount, prescription_cpr, expiration_date) VALUES ('{message['doc']}', '{message['medicine']}', '{message['amount']}', {message['prescription_cpr']}, '{message['expiration_date']}')")
        conn.commit()
        print(message)

        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@put('/provider/patient/cpr/<cpr>/token/<token>/JSON')
def _(token, cpr):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
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

@post('/provider/journal/token/<token>/JSON')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')

        response.content_type = 'application/json'
        message = request.json
        conn.execute(f"INSERT INTO journal (description, date_, given_medicine, patient_cpr) VALUES ('{message['description']}', '{message['date_']}', '{message['given_medicine']}', '{message['patient_cpr']}')")
        conn.commit()
        print(message)

        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)
################################################################################################################
                                                # Format XML
################################################################################################################
@get('/provider/patient/cpr/<cpr>/limit/<limit>/token/<token>/XML')
def _(token, cpr, limit):
    try:
        conn = sqlite3.connect('Mandatory.db')
        if limit == '0':
            raise Exception('Limit must be greater than 0')
        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')
        
        response.content_type = 'application/xml'
        xml_list = []
        c = conn.cursor()
        c.row_factory = row_to_dict
        #c.execute(f"SELECT * FROM patient WHERE cpr='{cpr}'")
        c.execute(f"SELECT * FROM patient JOIN journal ON patient.cpr = journal.patient_cpr WHERE patient.cpr='{cpr}' LIMIT {limit}")
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

@get('/provider/prescription/cpr/<cpr>/limit/<limit>/token/<token>/XML')
def _(token, cpr, limit):
    try:
        conn = sqlite3.connect('Mandatory.db')
        if limit == '0':
            raise Exception('Limit must be greater than 0')
        pharma_token = get_pharma_token()
        if token not in pharma_token:
            raise Exception('Token is invalid')
        
        response.content_type = 'application/xml'
        xml_list = []
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM prescription WHERE prescription_cpr='{cpr}' ORDER BY prescription_id DESC LIMIT {limit}")
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

@post('/provider/patient/token/<token>/XML')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')

        response.content_type = 'application/xml'
        message = request.body.getvalue()
        data = ET.fromstring(message)
        conn.execute(f"INSERT INTO patient (id, name, cpr, adress, access) VALUES ('{data[0][0].text}', '{data[0][1].text}', '{data[0][2].text}', '{data[0][3].text}', '{data[0][4].text}')")
        conn.commit()
        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/prescription/token/<token>/XML')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')

        response.content_type = 'application/xml'
        message = request.body.getvalue()
        data = ET.fromstring(message)
        conn.execute(f"INSERT INTO prescription (doc, medicine, amount, prescription_cpr, expiration_date) VALUES('{data[0][0].text}', '{data[0][1].text}', '{data[0][2].text}', {data[0][3].text}, '{data[0][4].text}')")
        conn.commit()
        print(message)
        
        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@put('/provider/patient/cpr/<cpr>/token/<token>/XML')
def _(token, cpr):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
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

@post('/provider/journal/token/<token>/XML')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')

        response.content_type = 'application/xml'
        message = request.body.getvalue()
        data = ET.fromstring(message)
        conn.execute(f"INSERT INTO journal (description, date_, given_medicine, patient_cpr) VALUES('{data[0][1].text}', '{data[0][0].text}', '{data[0][2].text}', '{data[0][3].text}')")
        conn.commit()
        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)

################################################################################################################
                                                # Format YAML
################################################################################################################
@get('/provider/patient/cpr/<cpr>/limit/<limit>/token/<token>/YAML')
def _(token, cpr, limit):
    try:
        conn = sqlite3.connect('Mandatory.db')
        if limit == '0':
            raise Exception('Limit must be greater than 0')
        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')
        
        response.content_type = 'application/yaml'
        c = conn.cursor()
        c.row_factory = row_to_dict
        #c.execute(f"SELECT * FROM patient WHERE cpr='{cpr}'")
        c.execute(f"SELECT * FROM patient JOIN journal ON patient.cpr = journal.patient_cpr WHERE patient.cpr='{cpr}' LIMIT {limit}")
        result = c.fetchall()

        data = 'messages:' + '\n'
        data += yaml.dump(result)
        return data
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@get('/provider/prescription/cpr/<cpr>/limit/<limit>/token/<token>/YAML')
def _(token, cpr, limit):
    try:
        conn = sqlite3.connect('Mandatory.db')
        if limit == '0':
            raise Exception('Limit must be greater than 0')
        pharma_token = get_pharma_token()
        if token not in pharma_token:
            raise Exception('Token is invalid')
        
        response.content_type = 'application/yaml'
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM prescription WHERE prescription_cpr='{cpr}' ORDER BY prescription_id DESC LIMIT {limit}")
        result = c.fetchall()

        data = 'messages:' + '\n'
        data += yaml.dump(result)
        return data
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/patient/token/<token>/YAML')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
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

        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')

        response.content_type = 'application/yaml'
        message = request.body.getvalue()
        data = yaml.safe_load(message)
        conn.execute(f"INSERT INTO prescription (doc, medicine, amount, prescription_cpr, expiration_date) VALUES ('{data['messages'][0]['doc']}', '{data['messages'][0]['medicine']}', '{data['messages'][0]['amount']}', {data['messages'][0]['prescription_cpr']}, '{data['messages'][0]['expiration_date']}')")
        conn.commit()
        print(message)
        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)
########
# Put Patient
########
@put('/provider/patient/cpr/<cpr>/token/<token>/YAML')
def _(token, cpr):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
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

###################
# YAML POST JOURNAL
###################
@post('/provider/journal/token/<token>/YAML')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')

        response.content_type = 'application/yaml'
        message = request.body.getvalue()
        data = yaml.safe_load(message)
        conn.execute(f"INSERT INTO journal (description, date_, given_medicine, patient_cpr) VALUES ('{data['messages'][0]['description']}', '{data['messages'][0]['date_']}', '{data['messages'][0]['given_medicine']}', {data['messages'][0]['patient_cpr']})")
        conn.commit()
        print(message)
        return message
    
    except Exception as ex:
        response.status = 400
        return str(ex)

################################################################################################################
                                                # Format TSV https://jsonformatter.org/json-to-tsv
################################################################################################################
@get('/provider/patient/cpr/<cpr>/limit/<limit>/token/<token>/TSV')
def _(token, cpr, limit):
    try:
        conn = sqlite3.connect('Mandatory.db')
        if limit == '0':
            raise Exception('Limit must be greater than 0')
        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')
        
        c = conn.cursor()
        c.row_factory = row_to_dict
        #c.execute(f"SELECT * FROM patient WHERE cpr='{cpr}'")
        c.execute(f"SELECT * FROM patient JOIN journal ON patient.cpr = journal.patient_cpr WHERE patient.cpr='{cpr}' LIMIT {limit}")
        result = c.fetchall()
        data = pd.DataFrame.from_records(result)
        return data.to_csv(sep='\t', index=False)
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@get('/provider/prescription/cpr/<cpr>/limit/<limit>/token/<token>/TSV')
def _(token, cpr, limit):
    try:
        conn = sqlite3.connect('Mandatory.db')
        if limit == '0':
            raise Exception('Limit must be greater than 0')
            ### CHANGE TO CHECK IS IN DATABASE FOR A SPECIFIC USER
        pharma_token = get_pharma_token()
        if token not in pharma_token:
            raise Exception('Token is invalid')
        
        c = conn.cursor()
        c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM prescription WHERE prescription_cpr='{cpr}' ORDER BY prescription_id DESC LIMIT {limit}")
        result = c.fetchall()
        data = pd.DataFrame.from_records(result)
        return data.to_csv(sep='\t', index=False)
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/patient/token/<token>/TSV')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
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

        doc_token = get_doc_token()
        if token not in doc_token:
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
        prescription_cpr = file['prescription_cpr'].to_list()
        expiration_date = file['expiration_date'].to_list()
        conn.execute(f"INSERT INTO prescription (doc, medicine, amount,prescription_cpr, expiration_date) VALUES ('{doc[0]}', '{medicine[0]}', '{amount[0]}', '{prescription_cpr[0]}', '{expiration_date[0]}')")
        conn.commit()
        return data
    
    except Exception as ex:
        response.status = 400
        return str(ex)

@put('/provider/patient/cpr/<cpr>/token/<token>/TSV')
def _(token, cpr):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
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

###################
# TSV POST JOURNAl
###################
@post('/provider/journal/token/<token>/TSV')
def _(token):
    try: 
        conn = sqlite3.connect('Mandatory.db')

        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')

        data = request.body.getvalue()
        data = data.decode("utf-8")
        print(data)
        with open('./output.tsv', 'wt') as out_file:
            out_file.write(data)

        file = pd.read_csv('output.tsv', sep='\t')

        description = file['description'].to_list()
        date_ = file['date_'].to_list()
        given_medicine = file['given_medicine'].to_list()
        amount = file['amount'].to_list()
        patient_cpr = file['patient_cpr'].to_list()
        print(str(description), str(date_), str(given_medicine), str(amount), patient_cpr)
        conn.execute(f"INSERT INTO journal (description, date_, given_medicine, patient_cpr, amount) VALUES ('{description[0]}', '{date_[0]}', '{given_medicine[0]}', '{patient_cpr[0]}', '{amount[0]}')")
        conn.commit()
        return data
    
    except Exception as ex:
        response.status = 400
        return str(ex)

################################################################################################################
                                                # Delete Patient
################################################################################################################
@delete('/provider/patient/cpr/<cpr>/token/<token>/d')
def _(token, cpr):
    try:
        conn = sqlite3.connect('Mandatory.db')
        
        doc_token = get_doc_token()
        if token not in doc_token:
            raise Exception('Token is invalid')
        
        c = conn.cursor()
        c.execute(f"DELETE FROM patient WHERE cpr='{cpr}'")
        conn.commit()
        return f'Patient {cpr} deleted!'
    
    except Exception as ex:
        response.status = 400
        return str(ex)

################################################################################################################
                                                # Delete Prescription
################################################################################################################
scheduler = BackgroundScheduler()

@scheduler.scheduled_job(IntervalTrigger(days=1))
def delete_prescriptions():
    try:
        today = date.today()
        d = today.strftime("%Y-%m-%d")
        print(d)
        conn = sqlite3.connect('Mandatory.db')
        c = conn.cursor()
        #c.row_factory = row_to_dict
        c.execute(f"SELECT * FROM prescription WHERE expiration_date='{d}'")
        result = c.fetchall()
        print(result)

        if result:
            c.execute(f"DELETE FROM prescription WHERE expiration_date='{d}'")
            conn.commit()
            return 'Prescritons deleted'
        else:
            return 'No prescritions deleted'
        
    except Exception as ex:
        return ex

scheduler.start()

################################################################################################################
                                                #Run Server
################################################################################################################
run(host='127.0.0.1', port=3000, debug=True, reloader=True)