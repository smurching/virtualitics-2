from parse_authors import *
import httplib, urllib, base64
import json
import schema_doc
import subprocess

author_patent_list = parse_authors()


headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': '51b1c195f5ee4afe84214fd60fb6a150',
    'Content-Type': 'application/json'
}

params = urllib.urlencode({
    # Request parameters
    'mode': 'json'
})

academic_journals = [
  "ACS Applied Materials & Interfaces",
  "Acta Crystallographica",
  "Acta Materialia",
  "Acta Metallurgica",
  "Scripta Materialia",
  "Advanced Composite Materials",
  "Advanced Materials",
  "Advanced Energy Materials",
  "Advanced Engineering Materials",
  "Advanced Functional Materials",
  "Advanced Optical Materials",
  "Bulletin of Materials Science",
  "Chemistry of Materials",
  "Computational Materials Science",
  "Crystal Growth & Design",
  "Journal of the American Ceramic Society",
  "Journal of Applied Crystallography",
  "Journal of Colloid and Interface Science",
  "Journal of Materials Chemistry A",
  "Journal of Materials Chemistry B",
  "Journal of Materials Chemistry C",
  "Journal of Modern Materials",
  "Journal of Materials Research and Technology",
  "Journal of Materials Science",
  "Journal of Materials Science Letters",
  "Journal of Materials Science: Materials in Electronics",
  "Journal of Materials Science: Materials in Medicine",
  "Journal of Physical Chemistry B",
  "Materials",
  "Materials and Structures",
  "Materials Chemistry and Physics",
  "Materials Research Letters",
  "Materials Science and Engineering A",
  "Materials Science and Engineering B",
  "Materials Science and Engineering C",
  "Materials Science and Engineering R",
  "Materials Today",
  "Metallurgical and Materials Transactions",
  "Modelling and Simulation in Materials Science and Engineering",
  "Nature Materials",
  "Physical Review B",
  "Progress in Materials Science",
  "Science and Technology of Advanced Materials",
  "Structural and Multidisciplinary Optimization",
  "Annual Review of Fluid Mechanics",
  "Experiments in Fluids",
  "Fluid Dynamics Research",
  "Flow, Turbulence and Combustion",
  "International Journal for Numerical Methods in Fluids",
  "International Journal of Multiphase Flow",
  "Journal of Computational Physics",
  "Journal of Experiments in Fluid Mechanics",
  "Journal of Fluid Mechanics",
  "Journal of Fluids and Structures",
  "Journal of Physics A",
  "Magnetohydrodynamics",
  "Physica A",
  "Physical Review E",
  "Physical Review Fluids",
  "Physics of Fluids",
  "Structural and Multidisciplinary Optimization",
  "Annual Review of Physical Chemistry",
  "ChemPhysChem",
  "Combustion, Explosion, and Shock Waves",
  "Current Opinion in Colloid and Interface Science",
  "Journal of Non-Equilibrium Thermodynamics",
  "Journal of Physical Chemistry A",
  "Journal of Physical Chemistry B",
  "Journal of Physical Chemistry C",
  "Journal of Physical Chemistry Letters",
  "Journal of Physical Organic Chemistry",
  "Journal of the Chemical Society, Faraday Transactions",
  "Macromolecular Chemistry and Physics",
  "Molecular Physics",
  "Physical Chemistry Chemical Physics",
  "Russian Journal of Physical Chemistry A",
  "Russian Journal of Physical Chemistry B"
]

paper_query = """
{
  "path": "/paper/AuthorIDs/author",
  "paper": {
    "type": "Paper",
    "match": {
        "NormalizedTitle": "material science",
    },
    "select": [
      "OriginalTitle",
      "NormalizedTitle",
      "PublishYear"
    ],
    "return":{
        "CitationCount": {"gt": 100}
    },
  },
  "author": {
      "type": "Author",
      "select": [
          "Name"
       ]
  },
}
"""

author_query = """
{
  "path": "/author/PaperIDs/paper/JournalID/journal",

  "paper": {
    "type": "Paper",
    "select": [
      "OriginalTitle",
      "NormalizedTitle",
      "PublishYear",
      "CitationCount",
      "PublishDate",
      "Keywords",
      "NormalizedAffiliations",
      "DOI"
    ]
  },
  "author": {
      "type": "Author",
      "select": [
          "Name"
       ],
       "match": {
           "Name": "%s"
       }
  },
  "journal": {
    "type": "Journal",
    "select": [
      "Name"
    ],
  },
}
"""

def get_abstract(title):
  title_quote = urllib.quote_plus(title)
  conn = httplib.HTTPSConnection('scholar.google.com/scholar?hl=en&q=%s'%title_quote)



def exec_graph_search_query(body):
  docs = []
  try:
      conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
      conn.request("POST", "/academic/v1.0/graph/search?%s" % params, body, headers)
      response = conn.getresponse()
      data = response.read()

      author_json_result = json.loads(data)
      #print(json.dumps(json.loads(data), indent=4, separators=(',', ': ')))
      for paper_data in author_json_result["Results"]:
        assert(len(paper_data) == 3)
        author = paper_data[0]
        author_name = author["Name"]
        author_name = author_name.split()[0] + " " + author_name.split()[2]
        paper = paper_data[1]
        paper_title = paper["NormalizedTitle"]
        paper_affiliations = list(set(json.loads(paper["NormalizedAffiliations"])))
        paper_keywords = list(set(json.loads(paper["Keywords"])))
        paper_citations = int(paper["CitationCount"])
        journal = paper_data[2]
        journal_name = journal["Name"]
        f = open('out.txt', 'w')
        subprocess.call(["ruby", "linkedin/get_paper_abstract.rb", paper_title], stdout = f)
        f = open('out.txt', 'r')
        abstract = f.read().strip()
        doc = schema_doc.schema_doc('pub', name=author_name, institutions = paper_affiliations, wildcard = {'sigwords': paper_keywords, 'journal_name': journal_name, 'citations': paper_citations, 'title': paper_title, 'summary': abstract})
        docs.append(doc)
        if len(docs) >= 7:
          break

      conn.close()
      schema_doc.send_data(docs)
  except Exception as e:
      print(e)

docs = []
for (author, patent_count) in author_patent_list:
  exec_graph_search_query(author_query % author)
