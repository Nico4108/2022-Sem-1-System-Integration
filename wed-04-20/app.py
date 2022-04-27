import sys, csv
from textwrap import indent, wrap
from bottle import get, run, response, post, request
import json, yaml
import xml.etree.ElementTree as ET
from dict2xml import dict2xml
import pandas as pd

users = {
    '12345':{'id':'1', 'email':'@a', 'token':'12345'},
    '67890':{'id':'2', 'email':'@a', 'token':'67890'},
}

messages = {
    '1':[
        {
            'id':'aaa0381a-4a37-4caf-af5f-aae31933749c', 
            'm1':'Hi', 
            'access':'*'
        },
        {
            'id':'6a66e5e7-70c9-4957-83ad-83e75e4daba0', 
            'm2':'Hi', 
            'access':'*'
        },
        {
            'id':'5564f18d-0bed-47db-b5cf-1482c7330544', 
            'm3':'Hi', 
            'access':'*'
        },
        {
            'id':'fd8d94db-e733-42df-b87d-e77b1c43a023', 
            'm4':'Hi', 
            'access':'*'
        }
    ]  
}

############################
@get('/provider/<id>/token/<token>/format/<format>')
def _(id, token, format):
    try:
        '''if limit == 0:
            raise Exception('Limit cannot be 0')'''
        if token not in users:
            raise Exception('Token is invalid')
        
        if format == 'JSON':
            response.content_type = 'application/json'
            return json.dumps(messages[id])

        elif format == 'XML':
            response.content_type = 'application/xml'
            xml_list = []
            for msg in messages[id]:
                xml_list.append(msg)

            data = '<?xml version="1.0" encoding="UTF-8"?>'
            data += '<data>'
            data += dict2xml(xml_list, wrap='test', indent=' ')
            data += '</data>'
            return data

        elif format == 'YAML':
            response.content_type = 'application/yaml'
            data = 'messages:' + '\n'
            data += yaml.dump(messages[id])
            return data

        elif format == 'TSV':
            data = pd.DataFrame.from_records(messages[id])
            return data.to_csv(sep='\t', index=False)

    except Exception as ex:
        response.status = 400
        return str(ex)

@post('/provider/<pro_id>/token/<token>/format/<format>')
def _(pro_id, token, format):
    # provider skal være subject(student, teacher....)
    try: 
        if token not in users:
            raise Exception('Token is invalid')

        if format == 'JSON':
            response.content_type = 'application/json'
            message = request.json
            print(message)

            return message

        elif format == 'XML':
            response.content_type = 'application/xml'
            xml_list = []
            for msg in messages[id]:
                xml_list.append(msg)

            data = '<?xml version="1.0" encoding="UTF-8"?>'
            data += '<data>'
            data += dict2xml(xml_list, wrap='test', indent=' ')
            data += '</data>'
            return data

        elif format == 'YAML':
            response.content_type = 'application/yaml'
            data = 'messages:' + '\n'
            data += yaml.dump(messages[id])
            return data

        elif format == 'TSV':
            data = pd.DataFrame.from_records(messages[id])
            return data.to_csv(sep='\t', index=False)
        
    
    except Exception as ex:
        response.status = 400
        return str(ex)

############################
run(host='127.0.0.1', port=3000, debug=True, reloader=True)