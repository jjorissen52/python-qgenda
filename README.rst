    ::

         /$$$$$$$              /$$     /$$
        | $$__  $$            | $$    | $$
        | $$  \ $$ /$$   /$$ /$$$$$$  | $$$$$$$   /$$$$$$  /$$$$$$$
        | $$$$$$$/| $$  | $$|_  $$_/  | $$__  $$ /$$__  $$| $$__  $$
        | $$____/ | $$  | $$  | $$    | $$  \ $$| $$  \ $$| $$  \ $$
        | $$      | $$  | $$  | $$ /$$| $$  | $$| $$  | $$| $$  | $$
        | $$      |  $$$$$$$  |  $$$$/| $$  | $$|  $$$$$$/| $$  | $$
        |__/       \____  $$   \___/  |__/  |__/ \______/ |__/  |__/
                   /$$  | $$
                  |  $$$$$$/
                   \______/
                                  /$$$$$$   /$$$$$$                            /$$
                                 /$$__  $$ /$$__  $$                          | $$
                                | $$  \ $$| $$  \__/  /$$$$$$  /$$$$$$$   /$$$$$$$  /$$$$$$
                                | $$  | $$| $$ /$$$$ /$$__  $$| $$__  $$ /$$__  $$ |____  $$
                                | $$  | $$| $$|_  $$| $$$$$$$$| $$  \ $$| $$  | $$  /$$$$$$$
                                | $$/$$ $$| $$  \ $$| $$_____/| $$  | $$| $$  | $$ /$$__  $$
                                |  $$$$$$/|  $$$$$$/|  $$$$$$$| $$  | $$|  $$$$$$$|  $$$$$$$
                                 \____ $$$ \______/  \_______/|__/  |__/ \_______/ \_______/
                                      \__/



Description
------------
A simple Python package to facilitate interactions with QGenda's REST API.


Overview
---------
Python QGenda is a client library to interact with QGenda's REST API. It provides some nice things out of the box for
you like automatic authentication and authentication storage.

Only GET methods are implemented, so if you need to update/delete, you will have to extend the API to do so.
Official QGenda API documentation can be found `here <http://restapi.qgenda.com>`__.

Setup
------
You will need to have an API account for QGenda for any of this stuff to work, of course. You will
want to have a config file that looks something like this:

    ::

        [qgenda]
        company_key = YOUR-COMPANY-KEY
        username = API-USERNAME
        password = API-PASSWORD
        api_url = https://api.qgenda.com/
        documentation = http://restapi.qgenda.com
        api_version = v2
        ; you can use redis or memcached, but you
        ; don't have to use caching at all if you don't want to.
        cache_backend =
        cache_host = 127.0.0.1
        cache_port = 6379
        cache_lifetime = 600 ; in seconds
        debug = 0

Simple Usage
------------

Logging In
++++++++++
You can login manually to test your credentials, but this library keeps the client authenticated
automatically so you don’t need to worry about it after you know your credentials work.

..  code:: python

        import os

        # tell configparser where to look for config
        os.environ['QGENDA_CONF_FILE'] = '/path/to/qgenda.conf'
        # optional
        os.environ['QGENDA_CONF_REGION'] = 'name_of_region' # defaults to qgenda

        from qgenda.api import client
        client = client.QGendaClient()
        client.authenticate()

Basics
+++++++
Every method returns a Response object from the requests library, so it's up to you to handle the json (or errors) that
come out.

.. code:: python

    import json

    odata_kwargs = {"$select": "StartDate,EndDate,StaffLName"}
    api_response = client.get_schedule(start_date='2019-01-01',
    odata_kwargs=odata_kwargs)
    # the response is now in a dictionary for easy consumption
    response_dict = json.loads(api_response.text)

    print(json.dumps(response_dict[0], indent=4))

Output
    ::

        {
            "StaffLName": "Holmes K",
            "EndDate": "2019-01-01T00:00:00",
            "StartDate": "2019-01-01T00:00:00"
        }


Get Method Examples
+++++++++++++++++++
Each of the get methods has optional OData parameters available, which allow you to sort, filter,
or limit what data you are pulling from the API. These are different for each of the get methods,
so you will want to check the official `QGenda API docs <http://restapi.qgenda.com>`__ for more details on that.

QGendaClient.get_schedule
@@@@@@@@@@@@@@@@@@@@@@@@@@

..  code:: python

        # odata is completely optional, but pretty useful.

        odata_kwargs = {
        "$select": "StartDate,EndDate,StaffLName",
        "$orderby": "StartDate",
        "$filter": "startswith(StaffLName, 'H')"
        }
        api_response = client.get_schedule(start_date='2019-01-01',
        end_date='2019-01-14',
        odata_kwargs=odata_kwargs)

        response_dict = json.loads(api_response.text)
        print(json.dumps(response_dict[:2], indent=4))

Output
    ::

        [
            {
                "StaffLName": "Holmes K",
                "EndDate": "2019-01-01T00:00:00",
                "StartDate": "2019-01-01T00:00:00"
            },
            {
                "StaffLName": "Hoover",
                "EndDate": "2019-01-01T00:00:00",
                "StartDate": "2019-01-01T00:00:00"
            }
        ]

QGendaClient.get_facility
@@@@@@@@@@@@@@@@@@@@@@@@@
As of the writing of this guide, attempting to use odata on an empty request results in a Bad
Request response. You may need to keep that in mind as you work with the API.

..  code:: python

    odata_kwargs = {
        '$select': 'Name,ID',
    }
    api_response = client.get_facility()
    response_dict = json.loads(api_response.text)
    # looks like there aren't any yet.
    print(json.dumps(response_dict[:2], indent=4))

QGendaClient.get_timeevent
@@@@@@@@@@@@@@@@@@@@@@@@@@

.. code:: python

    api_response = client.get_timeevent(start_date='2019-01-01')
    response_dict = json.loads(api_response.text)
    # looks like there aren't any yet.
    print(json.dumps(response_dict[:2], indent=4))


QGendaClient.get_dailycase
@@@@@@@@@@@@@@@@@@@@@@@@@@

.. code:: python

    api_response = client.get_dailycase(start_date='2019-01-01')
    response_dict = json.loads(api_response.text)
    # looks like there aren't any yet.
    print(json.dumps(response_dict[:2], indent=4))


Advanced
--------

Caching Authentication
+++++++++++++++++++++++
The client saves its saved authentication token in cache so you don't need to re-authenticate between instances unless your token
expires. redis and python-memcached are currently the only supported cache backends. Using the below configuration

Redis
@@@@@@

You need to install redis in your environment and run a redis server.

.. code:: bash

    pip install redis

Config
    ::

        [qgenda]
        company_key = YOUR-COMPANY-KEY
        username = API-USERNAME
        password = API-PASSWORD
        api_url = https://api.qgenda.com/
        documentation = http://restapi.qgenda.com
        api_version = v2
        cache_backend = redis
        cache_host = 127.0.0.1
        cache_port = 6379
        cache_lifetime = 600 ; in seconds
        debug = 0

Memcached
@@@@@@@@@@@

You need to install python-memecached in your environment and run a memcached server.

.. code:: bash

    pip install python-memcached

Config
    ::

        [qgenda]
        company_key = YOUR-COMPANY-KEY
        username = API-USERNAME
        password = API-PASSWORD
        api_url = https://api.qgenda.com/
        documentation = http://restapi.qgenda.com
        api_version = v2
        cache_backend = memcached
        cache_host = 127.0.0.1
        cache_port = 11211
        cache_lifetime = 600 ; in seconds
        debug = 0

