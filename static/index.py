from app import app as flask_app
import sys
from io import BytesIO

def handler(event, context):
    headers = event.get('headers', {})
    proto = headers.get('X-Forwarded-Proto', 'https')
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    query = event.get('queryStringParameters', '') or ''
    body = event.get('body', '')
    if body is None:
        body = ''
    if isinstance(body, str):
        body = body.encode('utf-8')

    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query,
        'CONTENT_TYPE': headers.get('Content-Type', ''),
        'CONTENT_LENGTH': str(len(body)),
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': proto,
        'wsgi.input': BytesIO(body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': True,
        'REMOTE_ADDR': headers.get('X-Real-IP', ''),
        'HTTP_HOST': headers.get('Host', ''),
    }
    for key, value in headers.items():
        environ['HTTP_' + key.upper().replace('-', '_')] = value

    response_status = None
    response_headers = []

    def start_response(status, headers, exc_info=None):
        nonlocal response_status, response_headers
        response_status = status
        response_headers = headers
        return lambda data: None

    response_body = flask_app(environ, start_response)
    body_output = b''.join(response_body).decode('utf-8')
    status_code = int(response_status.split()[0])

    return {
        'statusCode': status_code,
        'headers': dict(response_headers),
        'body': body_output
    }