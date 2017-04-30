import cherrypy
import requests
import pprint

class HelloWorld(object):
    def index(self):
        return "Hello World!"
    index.exposed = True

def start():
    cherrypy.quickstart(HelloWorld())

def main():
    json_body = {
        'query': [ 'go to the kitchen' ],
        'lang': 'en',
        'sessionId': '1234567890'
    }
    headers = {
        'Authorization': 'Bearer 2b03fc197cbf4387ad9c8c0e7c3cb0c2'
    }
    r = requests.post("https://api.api.ai/v1/query", 
            headers=headers, json=json_body)
    # try:
    #     print(r.json())
    # except Exception as e:
    #     print("Exception: {}".format(e))
    pprint.pprint(r.json())


if __name__ == "__main__":
    main()
