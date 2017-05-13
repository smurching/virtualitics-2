import json
import requests
from collections import OrderedDict
skg_url = skg_url = "http://34.210.65.117:8983/solr/knowledge-graph/update"
headers = {'Content-type': 'application/json'}

class schema_doc():    
    
    def __init__(self, resource, name=None, position=None, institutions=None, summary=None, wildcard=None):
        self.doc = OrderedDict()
        self.doc['resource'] = resource
        if name is not None:
            self.doc['name'] = name

        if position is not None:
            self.doc['position'] = position
        if institutions is not None:
            self.doc['institutions'] = institutions
        if summary is not None:
            self.doc['summary'] = summary
        if wildcard is not None:
            for k in wildcard.keys():
                self.doc[k] = wildcard[k]


def send_data(docs):
    print("Uploading %s docs"%(len(docs)))
    req = '''{update}'''.format(update=json.dumps([d.doc for d in docs]))
    print(req)
    result = requests.post(skg_url, data=req, headers=headers).text
    # return result
    # check if result was ok