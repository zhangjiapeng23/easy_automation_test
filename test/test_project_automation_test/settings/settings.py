'''
    TestProject base settings
'''

# project host
PROJECT_HOST = ''

MIDDLEWARE = {
    "mysql": {
        "host": "",
        "username": "",
        "password": "",
        "port": None
    },
    "redis": {
        "host": "",
        "password": "",
        "port": None
    }
}

APPS = [
    {
        "name": "",
        "namespace": "",
        "deployment": "",
        "path": {
            "api_name": "/xxx/xxx",
        }
    }
]


