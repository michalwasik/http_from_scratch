""" Task 1
Similarly to GET implement POST, PUT and PATCH methods. (they will look exactly the same at first)
1. (in pycharm Scratches and Consoles) create simple script that you'll use to send POST requests to your server:
import requests

response = requests.post(
    'http://127.0.0.1:8888/lesson.md',
    json={'key': 'value', '1': 2, 2: ['1', 2, '3']},
)
print(f'{response.status_code = }, {response.content = }')
2. Modify HTTPRequest so that it will have new attribute `data` which will be equal to data attached to request, loaded
   into dict with json.loads(...) for POST, PUT and PATCH methods, and will be None for rest. I recommend attaching
   debugger in HTTPRequest.parse() function to see what data you're getting then sending request with above script.
3. implement handle_POST and make sure you can access request.data
4. in response add extra_headers {'Content-Type': 'application/json'}, and try to attach some json to the response,
   so that the above script will print something like
   response.status_code = 200, response.content = b'{"works": true}'
5. copy and paste the same logic to create rest of HTTP methods required to make your server a REST server:
    list of methods with their meaning, don't worry about it yet, make them all do nothing
    POST - create object
    PUT - create or override all data of existing object (deleting non-edited fields)
    PATCH - override some data of existing object (leaving non-edited fields unchanged)
    GET - get some object
    DELETE - delete some object
    read: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
"""


""" Task 2
Let's make our server somewhat useful, we'll create simplified version of what you'll actually be doing at work.
First let's create file database.json, which will store information about iterm in some grocery store.
For now it should be empty, meaning containing only [].
Each item will be in following format
{
    "id": 1,
    "name": "banana",
    "supply": 45,
    "price_per_item": 7.30,
    "available": True
}

In order to create item you will need to send POST request to http://127.0.0.1:8888/items/ with following data exactly 
as above (without the id), server should check:
    1. if all fields are present (excluding id which should be created by server)
    2. if field are of proper type
if at least one condition is invalid server should return invalid response with status 400 and message like
     {"detail": "Missing fields: name, supply"}
     {"detail": "Too many fields: id, test"}
     {"detail": "Field price_per_item does not have proper type(float)}
otherwise, pick new id (that will be equal to 1 or will be one higher than id of previously added item), insert new
item in database.json and return proper response with status 201 and json of created item in message
    {"id": 1, "name": "banana", "supply": 45, "price_per_item": 7.30, "available": True}

To receive information about existing item in our database, client will need to send GET request to
http://127.0.0.1:8888/items/<int:item_id>/ if the item with given id doesn't exist return status 404 with message
    {"detail": "Item with id <given_id> doesn't exist"}
otherwise return item just like with POST example before

To get info abut all existing items, client will need to send GET request to http://127.0.0.1:8888/items/
return status 200 with list of ids and names of existing items.
    [
        {"id": 1, "name": "banana"}
    ]

To update existing item send PATCH method to http://127.0.0.1:8888/items/<int:item_id>/ if item doesn't exist act as 
with GET, if exists check supplied fields like with POST, and update them accordingly, 
return obj as previously with status 200

To delete object send DELETE method to http://127.0.0.1:8888/items/<int:item_id>/ if item doesn't exist act as 
with GET, if exists remove it from database, return status 204 (meaning no content) with no data, just {}

To buy items send POST request to http://127.0.0.1:8888/items/<int:item_id>/buy/ with data in format
    {"amount": 5, "money": 50.0}
If item does not exist, there's no enough supply or item is not available return status 400 with error message like
    {"detail": "Item with id <given_id> doesn't exist"}
    {"detail": "There's not enough supply to buy <amount> items, supply: <supply>"}
    {"detail": "Item is not available"}
    {"detail": "That's not enough money to buy this many items"}
Otherwise update the supply of requested item and return change amount:
    {"change": 3.5}
"""


""" Task 3
Make your server multithreaded, add another endpoint http://127.0.0.1:8888/sleep/<int:seconds>/ that will
simply sleep for x seconds and then return status 200 with message {"detail": "I slept well"}

using
from threading import Thread
try to modify TCPServer so that depending on its new initial argument `threaded`
def start(self, threaded: bool = False) -> None: 
it will run each new connection in separate Thread or not
"""
