"""Write the eight competency queries (01_model/competency_questions.txt) as SPARQL files in 03_sparql/
and run them on 02_data/kgdse.ttl. Writes 03_sparql/cqN.rq and 03_sparql/results_summary.txt
(row count and the first rows of each result). Usage: py -3.13 competency_queries.py"""
import os
from rdflib import Graph
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths as PT
OUT = PT.QUERIES
PFX = '''PREFIX kd: <https://w3id.org/kgdse/vocab#>
PREFIX kgdse: <https://w3id.org/kgdse/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
'''
CQ = {
 'cq1': ('Which datasets have been used for subtask X (here CMP-01 link prediction), by which studies, and where is the evidence?', '''
SELECT ?dataset (COUNT(DISTINCT ?study) AS ?studies) (COUNT(?r) AS ?records) (SAMPLE(?loc) AS ?exampleEvidence) (SAMPLE(?rep) AS ?exampleReport)
WHERE { ?r kd:recordStatus "active" ; kd:subtask <https://w3id.org/kgdse/subtask/CMP-01> ; kd:usesDataset ?d ; kd:study ?study ;
          kd:evidenceLocation ?loc ; kd:fromReport ?rep . ?d rdfs:label ?dataset }
GROUP BY ?dataset ORDER BY DESC(?studies) LIMIT 15'''),
 'cq2': ('For dataset D (here FB15k-237): in which categories and roles has it been used, by how many studies, and which variants exist?', '''
SELECT ?category ?role (COUNT(DISTINCT ?study) AS ?studies) (GROUP_CONCAT(DISTINCT ?variantLabel; separator="; ") AS ?variants)
WHERE { ?r kd:recordStatus "active" ; kd:usesDataset <https://w3id.org/kgdse/dataset/KGD-0001> ; kd:researchCategory ?c ; kd:role ?ro ; kd:study ?study .
        ?c skos:prefLabel ?category . ?ro skos:prefLabel ?role .
        OPTIONAL { ?v kd:variantOf <https://w3id.org/kgdse/dataset/KGD-0001> ; rdfs:label ?variantLabel } }
GROUP BY ?category ?role ORDER BY DESC(?studies)'''),
 'cq3': ('Which datasets have author-reported dataset limitations (DL), and how many records report one? (DL is recorded per record: it is attributable to the dataset only when the record names that dataset alone; in grouped records it may concern another dataset of the record.)', '''
SELECT ?dataset (SUM(IF(?n = 1, 1, 0)) AS ?attributableRecords) (SUM(IF(?n > 1, 1, 0)) AS ?groupedRecords)
       (MAX(IF(?n = 1, ?dl, "")) AS ?exampleAttributable)
WHERE { ?r kd:recordStatus "active" ; kd:limitationDataset ?dl ; kd:usesDataset ?d . ?d rdfs:label ?dataset .
        { SELECT ?r (COUNT(DISTINCT ?x) AS ?n) WHERE { ?r kd:usesDataset ?x } GROUP BY ?r } }
GROUP BY ?dataset ORDER BY DESC(?attributableRecords) DESC(?groupedRecords) LIMIT 15'''),
 'cq4': ('Which dataset uses do not report a version, per research category?', '''
SELECT ?category (SUM(IF(?vs = "version not stated", 1, 0)) AS ?notStated) (COUNT(?r) AS ?records)
WHERE { ?r kd:recordStatus "active" ; kd:versionStatus ?vs ; kd:researchCategory ?c . ?c skos:prefLabel ?category }
GROUP BY ?category ORDER BY DESC(?records)'''),
 'cq5': ('Which datasets were introduced in the corpus and later reused by other studies in it?', '''
SELECT ?dataset (COUNT(DISTINCT ?intro) AS ?introducingStudies) (COUNT(DISTINCT ?user) AS ?reusingStudies)
WHERE { ?d kd:introducedIn ?intro ; rdfs:label ?dataset .
        ?r kd:recordStatus "active" ; kd:usesDataset ?d ; kd:study ?user .
        FILTER NOT EXISTS { ?d kd:introducedIn ?user } }
GROUP BY ?dataset HAVING (COUNT(DISTINCT ?user) > 0) ORDER BY DESC(?reusingStudies) LIMIT 15'''),
 'cq6': ('Which research categories rely on fewer than k (here 20) distinct datasets?', '''
SELECT ?category (COUNT(DISTINCT ?d) AS ?datasets) (COUNT(DISTINCT ?r) AS ?records)
WHERE { ?r kd:recordStatus "active" ; kd:researchCategory ?c ; kd:usesDataset ?d . ?c skos:prefLabel ?category }
GROUP BY ?category HAVING (COUNT(DISTINCT ?d) < 20) ORDER BY ?datasets'''),
 'cq7': ('Which described datasets are restricted, not publicly released, or have no located release?', '''
SELECT ?dataset ?access ?licence
WHERE { ?d kd:accessStatus ?access ; rdfs:label ?dataset . OPTIONAL { ?d kd:licenceText ?licence }
        FILTER(!STRSTARTS(?access, "Public")) }
ORDER BY ?access ?dataset'''),
 'cq8': ('Where can dataset D (here WebNLG, KGD-0055) be obtained, under which licence, and what does an item look like?', '''
SELECT ?dataset ?access ?licence ?accessSource ?sampleInput ?sampleOutput ?sampleSource
WHERE { BIND(<https://w3id.org/kgdse/dataset/KGD-0055> AS ?d) ?d rdfs:label ?dataset .
        OPTIONAL { ?d kd:accessStatus ?access } OPTIONAL { ?d kd:licenceText ?licence }
        OPTIONAL { ?d kd:descriptorEvidence ?e . ?e kd:field "access_status" ; dcterms:source ?accessSource }
        OPTIONAL { ?d kd:sample ?s . ?s kd:sampleInput ?sampleInput ; dcterms:source ?sampleSource . OPTIONAL { ?s kd:sampleOutput ?sampleOutput } } }'''),
}
g = Graph().parse(os.path.join(PT.DATA, 'kgdse.ttl'), format='turtle')
lines = []
for k, (question, body) in CQ.items():
    text = f'# {k.upper()}: {question}\n' + PFX + body.strip() + '\n'
    open(os.path.join(OUT, f'{k}.rq'), 'w', encoding='utf-8').write(text)
    res = list(g.query(PFX + body))
    lines.append(f'== {k.upper()}: {question}\n   rows: {len(res)}')
    for r in res[:6]:
        lines.append('   ' + ' | '.join((str(v)[:70] if v is not None else '-') for v in r))
rep = '\n'.join(lines); print(rep)
open(os.path.join(OUT, 'results_summary.txt'), 'w', encoding='utf-8').write(rep + '\n')
