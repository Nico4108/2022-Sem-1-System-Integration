from bottle import error, get, run, response, post, request, hook, delete, put
import json
import uuid

items = [
    {'id': 'eeb02eb1-5ebf-47d0-9f64-754bd2dad3d7', 
     'name': 'a',
     'last_name': 'somthing'}
]

# Hook, can add an action before or after a requests
@hook('after_request')
def _():
    response.content_type = 'application/json'


####################################
@get('/')
def _():
    return 'home'

####################################
@get('/items')
def _():
    #response.content_type = 'application/json'
    return json.dumps(items)

@get('/items/<id>')
def _(id):
    #response.content_type = 'application/json'
    # loop
    '''for item in items:
        if item['id'] == id:
            return json.dumps(item)
    return'''

    # list comprehension
    # result = [return value    loop    condition]
    list_of_matches = [ item for item in items if item['id'] == id ]
    if not list_of_matches:
        response.status = 204
        return

    return list_of_matches[0]

@post('/items')
def _():
    item_id = str(uuid.uuid4())
    item_name = request.json.get('name')
    item = {'id': item_id, 'name': item_name}
    items.append(item)
    print(type(item_id))
    response.status = 201
    return {'id': item_id}

####################################
@delete('/items/<item_id>')
def _(item_id):
    # enumerate is creating an "id" of the item in the list to look up for deleting
    for index, item in enumerate(items):
        if item['id'] == item_id:
            items.pop(index)
            return {'info': 'item deleted'}

    response.status = 204
    return
    # This is not displayed since a 204 dosen't return json or anything
    #return json.dumps({'info': f'item with id {item_id} was not found'})

####################################
@put('/items/<id>') #(Patch)
def _(id):
    try:
        # item is changed since it is using refference (pointer to list object)
        item = [item for item in items if item['id'] == id][0]
        
        # Små Kus løsning
        '''if not request.json.get('name'):
            pass
        else:
            item['name'] = request.json.get('name')

        if not request.json.get('last_name'): 
            pass
        else:
            item['last_name'] = request.json.get('last_name')'''

        #Santiagos løsning
        '''if request.json.get('name'): item['name'] = request.json.get('name')
        if request.json.get('last_name'): item['last_name'] = request.json.get('last_name')'''

        #Catalinas løsning, extended
        for key in item.keys():
            if key in request.json.keys():
                item[key] = request.json.get(key)

        return item

    except Exception as ex:
        print(ex)
        response.status = 204
        return

####################################
@error(404)
def _(err):
    #response.content_type = 'application/json'
    return json.dumps({'info': 'page not found'})

####################################
# max port available 65535
# not available 0 - 1024
run(host='127.0.0.1', port=8888, debug=True, reloader=True, server='paste')