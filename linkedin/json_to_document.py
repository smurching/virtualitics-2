import json
import sys
sys.path.append("..")
import schema_doc
RESOURCE_NAME = "linkedin"
MAX_DOCS_PER_POST = 100

def upload(linkedin_datafile):
    docs = []
    with open(linkedin_datafile) as handle:
        i = 0
        for line in handle:
            dictionary = json.loads(line.strip())
            wildcard = {"resource" : RESOURCE_NAME}
            document = schema_doc.schema_doc(name=dictionary["name"],
                position=dictionary["title"],
                institutions=dictionary["companies"],
                summary=dictionary["summary"], wildcard=wildcard)
            docs.append(document)
            i += 1
            if i % MAX_DOCS_PER_POST == 0:
                schema_doc.send_data(docs)
                docs = []

    if len(docs) > 0:
        schema_doc.send_data(docs)

if __name__ == "__main__":
    linkedin_datafile = sys.argv[1]
    upload(linkedin_datafile)
