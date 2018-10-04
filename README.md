## Installation
Download this project and run
```
python setup.py install
```

## Configuration
You'll need a config file (`config.ini`, for example) with the following options.
```
[qgenda]
company_key = <GUID for your company>
username = <email address associated with your API login>
password = <password associated with your API login>
api_url = https://api.qgenda.com/
documentation = http://restapi.qgenda.com
api_version = v2
cache_backend = ;redis and memcache supported
cache_host = <IP address or host name>
cache_port = <int>
cache_lifetime = <seconds of cache lifetime>
debug = <1 or leave empty>
```
You will also need to set an environment variable (or two, depending) **BEFORE IMPORTING THE API**:
```
import os
os.environ['QGENDA_CONF_FILE'] = <full or relative path to config.ini>
# optional
os.environ['QGENDA_CONF_REGION'] = <name of qgenda settings region, defaults to qgenda>
```
The client will let you know if your config is missing any required options.

## Basic Usage
You'll want to look at the tests. There are a bunch of goodies in there
showing you how to use caching and leader/follower client implementations.

Here is the most bare working example:

```
import json

client = QGendaClient(raise_errors=True) # whether failed API calls raise an exception or fail silently.
response = client.get_staff() # you will be getting response objects directly from the requests library
response_dict = json.loads(response.text)
print(json.dumps(response_dict, indent=4)
```

## What is leader/follower?
Followers do not authenticate; they borrow authentication tokens from
the leader. This allows you to have multiple clients running around on
your machine that are looking for the leader to give out authentication
details.

**Note: waiting for authentication is a blocking process, so
followers must be implemented in separate threads or processes from the
leader.**