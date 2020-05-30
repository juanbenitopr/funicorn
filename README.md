This project emulate the basic behaviour of any [WSGI server](https://medium.com/@juanbenito.pr/explaining-wsgi-and-python-applications-25478dc6c696). 


## Goal

It only pursues educational purposes, it is designed to be easy to understand. It is not production ready and for sure doesn't implement all use cases, also it might contains bugs. 
So don't use it for deploy your application 

## Gettint Started

In order to run your application you only need:

`pip install -r requirements.txt`

``
funicorn = Funicorn('application.path', 'application_name_obj', 'host', 'port')

# The most used application object name is app or application
# host is localhost by default
# port is 8000 by default

``

## Example

There is already an example created.

 `python main.py`
 
The example application return 'Hello World' for GET method, and it return the body of your request in the response (echo application)

``
funicorn = Funicorn('application.path', 'application_name_obj', 'host', 'port')

# The most used application object name is app or application
# host is localhost by default
# port is 8000 by default

``

## Testing

There are some tests to cover the basic use cases, you can run them using `pytest`


## Architecture

The package contains the modules:

- *http2*: it contains all the http entities.

- *wsgi*: it contains the logic to handle the WSGI application

- *main*: it contains the server and the plain request handler
