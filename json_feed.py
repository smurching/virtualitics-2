import pandas
import sys
sys.path.append("../")

from schema_doc import schema_doc, send_data
from nameparser import HumanName


def get_doc(row):
    name = HumanName(row[0])
    name = name.first + " " + name.last
    position = row[7]
    institutions = [row[5]]
    summary = ""
    grade = row[1]
    pay_plan = row[2]
    salary = row[3]
    bonus = row[4]
    location = row[6]
    dic = {'grade': row[1], 'pay_plan': row[2], 'salary':row[3], 'bonus':row[4], 'location':row[6], 'resource':'gov_salary'}
    doc = schema_doc(name, position, institutions, wildcard=dic)
    return doc
    
    

df = pandas.read_csv('data.csv', header=None)
df = df[df[0] != 'NAME WITHHELD BY AGENCY'].values
start = 100001
count = 0
docs = []
for row in df:
    count += 1
    if count < start:
        continue
    docs.append(get_doc(row))
    if len(docs) % 100000 == 0:
        print "Sending"
        print send_data(docs)
        docs = []
        print count
print send_data(docs)