import os
import socket
import mimetypes
import json
from time import sleep
from _thread import *


class TCPServer:
    """Base server class for handling TCP connections.
    The HTTP server will inherit from this class.
    """

    def __init__(self, host: str = '127.0.0.1', port: int = 8888) -> None:
        self.host = host
        self.port = port

    def start(self, threaded: bool = False) -> None:
        """Method for starting the server"""

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)

        print("Listening at", s.getsockname())

        while True:
            conn, addr = s.accept()
            print("Connected by", addr)
            if threaded:
                print('started new thread')
                start_new_thread(self.threaded_func, (conn,))
            else:
                print('old way')
                self.handle_connection(conn)

    def threaded_func(self, c):
        while True:
            self.handle_connection(c)

    def handle_connection(self, connection):
        # For the sake of this tutorial,
        # we're reading just the first 1024 bytes sent by the client.
        data = connection.recv(1024)
        response = self.handle_request(data)
        connection.sendall(response)
        connection.close()

    def handle_request(self, data: bytes) -> bytes:
        """Handles incoming data and returns a response.
        Override this in subclass.
        """
        return data


class HTTPServer(TCPServer):
    """The actual HTTP server class."""
    blank_line: bytes = b'\r\n'
    headers: dict[str, str] = {
        'Server': 'CrudeServer',
        'Content-Type': 'text/html',
    }
    status_codes: dict[int, str] = {
        200: 'OK',
        201: 'Created',
        400: 'Bad Request',
        404: 'Not Found',
        204: 'No Content',
        501: 'Not Implemented',
    }

    def handle_request(self, data: bytes) -> bytes:
        """Handles incoming requests"""

        request = HTTPRequest(data)  # Get a parsed HTTP request
        try:
            # Call the corresponding handler method for the current
            # request's method
            handler = getattr(self, f'handle_{request.method}')
        except AttributeError:
            handler = self.HTTP_501_handler

        response = handler(request)
        print(response)
        return response

    def response_line(self, status_code: int) -> bytes:
        """Returns response line (as bytes)"""
        reason = self.status_codes[status_code]
        response_line = f'HTTP/1.1 {status_code} {reason}'

        return b''.join([response_line.encode(), self.blank_line])  # convert from str to bytes

    def response_headers(self, extra_headers: dict = None) -> bytes:
        """Returns headers (as bytes).

        The `extra_headers` can be a dict for sending
        extra headers with the current response
        """
        extra_headers = extra_headers or {}
        str_headers = ''
        for key, value in {**self.headers, **extra_headers}.items():
            str_headers += f'{key}: {value}{self.blank_line.decode()}'

        return str_headers.encode()  # convert str to bytes

    def handle_PUT(self, request: 'HTTPRequest') -> bytes:
        response_line = self.response_line(200)
        content = b'{"put_works": true}'
        return b''.join([response_line, self.blank_line], content)

    def handle_PATCH(self, request: 'HTTPRequest') -> bytes:
        response_line = self.response_line(200)
        content = b'{"patch_works": true}'
        return b''.join([response_line, self.blank_line], content)

    def handle_DELETE(self, request: 'HTTPRequest') -> bytes:
        response_line = self.response_line(200)
        content = b'{"delete_works": true}'
        return b''.join([response_line, self.blank_line], content)

    def handle_OPTIONS(self, request: 'HTTPRequest') -> bytes:
        """Handler for OPTIONS HTTP method"""

        response_line = self.response_line(200)
        extra_headers = {'Allow': 'OPTIONS, GET'}
        response_headers = self.response_headers(extra_headers)

        return b''.join([response_line, response_headers, self.blank_line])  # without body

    def handle_PATCH(self, request: 'HTTPRequest') -> bytes:
        path = request.uri.strip('/')  # remove slash from URI
        print(path)
        if '/' in path:
            sub_path = path.split('/')
            if len(sub_path) == 2:
                if sub_path[0] == 'items' and sub_path[1].isdigit():
                    requested_id = int(sub_path[1])
                    with open('database.json', 'r+') as db_file:
                        db = json.load(db_file)
                        db_copy = db.copy()
                        result = None
                        for registry in db_copy:
                            if requested_id == registry['id']:
                                result = registry
                        if result:
                            db.remove(result)
                            result.update(request.request_body)
                            db.append(result)
                            db_file.seek(0)
                            json.dump(db, db_file)
                            response_line = self.response_line(200)
                            response_headers = self.response_headers()
                            added_response = {'detail': f"Patched item with id: {requested_id}. "
                                                        f"Updated data: {request.request_body}"}
                            response_body = str(added_response).encode()
                        else:
                            response_line = self.response_line(404)
                            response_headers = self.response_headers()
                            id_bot_found_error = {"detail": f"Item with id: {requested_id} doesn't exist"}
                            response_body = str(id_bot_found_error).encode()

                        return self.format_response(response_line, response_headers, response_body)

    def handle_DELETE(self, request: 'HTTPRequest') -> bytes:
        path = request.uri.strip('/')  # remove slash from URI
        print(path)
        if '/' in path:
            sub_path = path.split('/')
            if len(sub_path) == 2:
                if sub_path[0] == 'items' and sub_path[1].isdigit():
                    requested_id = int(sub_path[1])
                    with open('database.json') as db_file:
                        db = json.load(db_file)
                        result = None
                        for registry in db:
                            if requested_id == registry['id']:
                                result = registry
                                db.remove(registry)
                        if result:
                            with open('database.json', 'w') as db_file:
                                json.dump(db, db_file)
                            response_line = self.response_line(204)
                            response_headers = self.response_headers()
                            response_body = str({}).encode()
                        else:
                            response_line = self.response_line(404)
                            response_headers = self.response_headers()
                            id_bot_found_error = {"detail": f"Item with id: {requested_id} doesn't exist"}
                            response_body = str(id_bot_found_error).encode()

                        return self.format_response(response_line, response_headers, response_body)

    def handle_GET(self, request: 'HTTPRequest') -> bytes:
        """Handler for GET HTTP method"""

        path = request.uri.strip('/')  # remove slash from URI
        print(path)
        if 'sleep/' in path:
            uri_parts = path.split('/')
            sleep_time = int(uri_parts[1])
            sleep(sleep_time)
            response_line = self.response_line(200)
            response_headers = self.response_headers()
            response_body = str({"detail": "I slept well"}).encode()
            return self.format_response(response_line, response_headers, response_body)

        elif not path:
            # If path is empty, that means user is at the homepage
            # so just serve index.html
            path = 'index.html'
        if path == 'items':
            with open('database.json', 'r+') as db_file:
                db = json.load(db_file)
                results = []
                for registry in db:
                    short_dict = {'id': registry['id'], 'name': registry['name']}
                    results.append(short_dict)
                response_line = self.response_line(200)
                response_headers = self.response_headers()
                response_body = str(results).encode()
        elif '/' in path:
            sub_path = path.split('/')
            if len(sub_path) == 2:
                if sub_path[0] == 'items' and sub_path[1].isdigit():
                    requested_id = int(sub_path[1])
                    with open('database.json', 'r+') as db_file:
                        db = json.load(db_file)
                        result = None
                        for registry in db:
                            if requested_id == registry['id']:
                                result = registry
                        if result:
                            response_line = self.response_line(200)
                            response_headers = self.response_headers()
                            response_body = str(result).encode()
                        else:
                            response_line = self.response_line(404)
                            response_headers = self.response_headers()
                            id_bot_found_error = {"detail": f"Item with id: {requested_id} doesn't exist"}
                            response_body = str(id_bot_found_error).encode()
        else:
            if os.path.exists(path) and not os.path.isdir(path):  # don't serve directories
                response_line = self.response_line(200)

                # find out a file's MIME type
                # if nothing is found, just send `text/html`
                content_type = mimetypes.guess_type(path)[0] or 'text/plain'

                extra_headers = {'Content-Type': content_type}
                response_headers = self.response_headers(extra_headers)

                with open(path, 'rb') as f:
                    response_body = f.read()
            else:
                response_line = self.response_line(404)
                response_headers = self.response_headers()
                response_body = b'<h1>404 Not Found</h1>'

        return self.format_response(response_line, response_headers, response_body)

    @staticmethod
    def validate_data(data):
        required_keys = {'name', 'supply', 'price_per_item', 'available'}
        if required_keys != set(data.keys()):
            redundant = [key for key in set(data.keys()) if key not in required_keys]
            missing = [key for key in required_keys if key not in set(data.keys())]
            if redundant and missing:
                return f"Missing fields: {missing}, supply. Redundant fields: {redundant}"
            elif redundant:
                return f"Redundant fields: {redundant}"
            else:
                return f"Missing fields: {missing}"
        else:
            invalid_types = []
            if not isinstance(data['name'], str):
                invalid_types.append("'name': type(str)")
            elif not isinstance(data['supply'], int):
                invalid_types.append("'supply': type(int)")
            elif not isinstance(data['price_per_item'], (int, float)):
                invalid_types.append("'price_per_item': type(int, float)")
            elif not isinstance(data['available'], bool):
                invalid_types.append("'available': type(bool)")
        if not invalid_types:
            return None
        else:
            return f"Some fields don't have right type. Fill according to schema: {invalid_types}"

    @staticmethod
    def highest_id(data):
        id = 0
        for part in data:
            if part["id"] > id:
                id = part["id"]
        return id

    def handle_POST(self, request: 'HTTPRequest') -> bytes:
        # request.request_body = request.request_body.replace("\'", "\"")
        print(type(request.request_body))
        print('POST REQUEST BODY')
        print(request.request_body)
        request_body_dict = json.loads(request.request_body)
        # print(type(request_body_dict))
        # print(request.uri)
        if request.uri.strip('/') == 'items':
            error_msg = self.validate_data(request_body_dict)
            if error_msg:
                response_body = json.dumps({'detail': error_msg}).encode()
                response_line = self.response_line(400)
            else:
                with open('database.json', 'r+') as db_file:
                    db = json.load(db_file)
                    if not db:
                        id = 1
                    else:
                        id = self.highest_id(db) + 1
                    request_body_dict['id'] = id
                    db.append(request_body_dict)
                    db_file.seek(0)
                    json.dump(db, db_file)
                    # mam czasami 2 znaki ] w sensie jeden dodatkowy na koncu jsona
                    response_body = str(request_body_dict).replace("\'", "\"").encode()
                    response_line = self.response_line(201)
        elif '/' in request.uri.strip('/'):
            uri_parts = request.uri.strip('/').split('/')
            if uri_parts[0] == 'items' and uri_parts[2] == 'buy' and uri_parts[1].isdigit():
                requested_id = int(uri_parts[1])
                amount = request.request_body["amount"]
                money = request.request_body["money"]
                correct_transaction = False
                with open('database.json', 'r+') as db_file:
                    db = json.load(db_file)
                    db_copy = db.copy()
                    result = None
                    for registry in db_copy:
                        if requested_id == registry['id']:
                            result = registry
                    if not result:
                        transaction_response = {"detail": f"Item with id: {requested_id} doesn't exist"}
                    elif not result["available"]:
                        transaction_response = {"detail": f"Item is not available"}
                    elif amount > result["supply"]:
                        transaction_response = {"detail": f"There's not enough supply to buy {amount} items, supply: "
                                                          f"{result['supply']}"}
                    elif result["price_per_item"] * amount > money:
                        transaction_response = {"detail": f"That's not enough money to buy this many items"}
                    else:
                        db.remove(result)
                        change = money - result["price_per_item"] * amount
                        transaction_response = {"change": change}
                        correct_transaction = True
                        result["supply"] -= amount
                        if result["supply"] == 0:
                            result["available"] = False
                        db.append(result)
                        db_file.seek(0)
                        json.dump(db, db_file)
                response_body = str(transaction_response).encode()
                if correct_transaction:
                    response_line = self.response_line(200)
                else:
                    response_line = self.response_line(404)
        else:
            # content = b'{"works": true}'
            response_line = self.response_line(200)
        extra_headers = {'content': response_body}
        response_headers = self.response_headers(extra_headers)
        print(b''.join([response_line,  response_headers]))

        return b''.join([response_line, self.blank_line, response_body])

    def HTTP_501_handler(self, request: 'HTTPRequest') -> bytes:
        """Returns 501 HTTP response if the requested method hasn't been implemented."""

        response_line = self.response_line(status_code=501)
        response_headers = self.response_headers()
        response_body = b'<h1>501 Not Implemented</h1>'

        return self.format_response(response_line, response_headers, response_body)

    def format_response(self, line: bytes, headers: bytes, body: bytes) -> bytes:
        return b"".join([line, headers, self.blank_line, body])


class HTTPRequest:
    """Parser for HTTP requests.

    It takes raw data and extracts meaningful information about the incoming request.

    Instances of this class have the following attributes:
        self.method: The current HTTP request method sent by client (string)
        self.uri: URI for the current request (string)
        self.http_version = HTTP version used by  the client (string)
    """

    def __init__(self, data: bytes) -> None:
        self.method = None
        self.uri = None
        self.http_version = '1.1'  # default to HTTP/1.1 if request doesn't provide a version
        self.request_body = None

        # call self.parse method to parse the request data
        self.parse(data)

    def parse(self, data: bytes) -> None:
        print(data.decode())
        """
        Example data:
        GET /index.html HTTP/1.1
        Host: example.com
        Connection: keep-alive
        User-Agent: Mozilla/5.0
        """
        if b'\r\n\r\n' in data:
            head, body = data.split(b'\r\n\r\n')
            self.request_body = body.decode()
        else:
            head = data
        parts = head.split(b'\r\n')
        request_line = parts[0]  # request line is the first line of the data
        words = request_line.split(b' ')  # split request line into separate words
        self.method = words[0].decode()  # call decode to convert bytes to string
        request_headers = {}
        for idx, line in enumerate(parts):
            if idx > 1:
                key, value = line.decode().split(':')
                request_headers[key] = value.strip()

        if len(words) > 1:
            # we put this in if block because sometimes browsers
            # don't send URI with the request for homepage
            self.uri = words[1][1:].decode()  # call decode to convert bytes to string
        if len(words) > 2:
            # we put this in if block because sometimes browsers
            # don't send HTTP version
            self.http_version = words[2]


if __name__ == '__main__':
    server = HTTPServer()
    server.start()
