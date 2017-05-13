import schema_doc
import json

with open('data/wiki_dump.json', 'r') as f:
	lines = f.readlines()
docs = []
for l in lines:
	# print json.loads(l.strip())
	json_doc = json.loads(l.strip())
	additional = {'sigwords' : [json_doc['id']], 'resource': 'wikipedia'}
	# print json_doc['id']
	# print json_doc['tweet']
	# print json_doc['tweet']
	docs.append(schema_doc.schema_doc(summary=json_doc['tweet'], wildcard=additional))
	if len(docs) >= 100:
		result = schema_doc.send_data(docs)
		print result
		docs = []
