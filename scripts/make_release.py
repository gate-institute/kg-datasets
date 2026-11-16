"""Assemble the public repository folder 06_publication/kgdse/ (github.com/gate-institute/kg-datasets).
Copies only: RDF graph, vocabulary, shapes, competency questions and queries, scripts, the two JSON build
inputs, CSV exports; writes datasets.csv (registry with descriptors and samples), README.md, CITATION.cff,
LICENSE (CC BY 4.0, data) and LICENSE-CODE (MIT). No PDFs, full texts, drafts or ResearchRabbit export."""
import os, shutil, json, csv, urllib.request, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(HERE); ROOT = os.path.dirname(RES)
OUT = os.path.join(RES, '06_publication', 'kgdse')
for d in ('data/json', 'data/csv', 'model', 'queries', 'scripts'): os.makedirs(os.path.join(OUT, d), exist_ok=True)
CP = [('02_data/kgdse.ttl', 'data/kgdse.ttl'), ('02_data/kgdse.nt', 'data/kgdse.nt'), ('02_data/validation_report.txt', 'data/validation_report.txt'),
      ('01_model/kgdse-vocab.ttl', 'model/kgdse-vocab.ttl'), ('01_model/kgdse-shapes.ttl', 'model/kgdse-shapes.ttl'),
      ('01_model/competency_questions.txt', 'model/competency_questions.txt'), ('03_sparql/results_summary.txt', 'queries/results_summary.txt')]
CP += [(f'03_sparql/cq{i}.rq', f'queries/cq{i}.rq') for i in range(1, 9)]
CP += [(f'05_scripts/{s}', f'scripts/{s}') for s in ('paths.py', 'build_rdf.py', 'validate.py', 'competency_queries.py')]
CP += [(f'05_scripts/{s}', f'scripts/{s}') for s in ('build_site.py', 'make_release.py')]
for a, b in CP: shutil.copy2(os.path.join(RES, a), os.path.join(OUT, b))
# website (GitHub Pages from /docs)
SITE = os.path.join(RES, '04_website', 'site'); DOCS = os.path.join(OUT, 'docs')
if os.path.isdir(DOCS): shutil.rmtree(DOCS)
shutil.copytree(SITE, DOCS); open(os.path.join(DOCS, '.nojekyll'), 'w').close()
# RDF served from Pages too (w3id content negotiation targets these)
os.makedirs(os.path.join(DOCS, 'rdf'), exist_ok=True)
for a, b in (('02_data/kgdse.ttl', 'kgdse.ttl'), ('02_data/kgdse.nt', 'kgdse.nt'), ('01_model/kgdse-vocab.ttl', 'kgdse-vocab.ttl'), ('01_model/kgdse-shapes.ttl', 'kgdse-shapes.ttl')):
    shutil.copy2(os.path.join(RES, a), os.path.join(DOCS, 'rdf', b))
shutil.copy2(os.path.join(ROOT, 'Master Table', 'master.json'), os.path.join(OUT, 'data/json/master.json'))
shutil.copy2(os.path.join(ROOT, 'Dataset Registry', 'registry.json'), os.path.join(OUT, 'data/json/registry.json'))
for a, b in (('master_evidence.csv', 'evidence.csv'), ('master_reports.csv', 'reports.csv'), ('master_peripheral.csv', 'peripheral.csv')):
    shutil.copy2(os.path.join(ROOT, 'Master Table', a), os.path.join(OUT, 'data/csv', b))
reg = json.load(open(os.path.join(ROOT, 'Dataset Registry', 'registry.json'), encoding='utf-8'))
F = ['resource_kind', 'introducing_source', 'derived_from', 'input_unit', 'input_type', 'output_unit', 'output_type', 'input_source', 'target_source',
     'creation_method', 'human_verification', 'size', 'access_status', 'licence']
with open(os.path.join(OUT, 'data/csv', 'datasets.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['dataset_id', 'canonical_name', 'records', 'studies', 'aliases', 'variants', 'categories', 'roles', 'introduced_in', 'notes', 'descriptor_status'] + F +
               ['sample_input', 'sample_output', 'sample_source', 'sample_licence', 'sample_reproduce'])
    for d in reg['registry']:
        ds = d.get('descriptors') or {}; s = ds.get('sample') or {}
        w.writerow([d['dataset_id'], d['canonical_name'], d['records'], d['studies'], d['aliases'], d['variants'], d['categories'], d['roles'], d['introduced_in'],
                    d.get('notes', ''), d.get('descriptor_status', '')] + [(ds.get(x) or {}).get('value', '') for x in F] +
                   [s.get('sample_input', ''), s.get('sample_output', ''), s.get('source_url', ''), s.get('licence', ''), s.get('reproduce', '')])
with open(os.path.join(OUT, 'data/csv', 'dataset_links.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['row_key', 'study_id', 'research_category', 'recorded_name', 'dataset_id', 'dataset', 'variant_id', 'variant'])
    for l in reg['links']:
        if l['first_for_dataset']: w.writerow([l['row_key'], l['study_id'], l['category'], l['name'], l['canonical_id'], l['canonical'], l['variant_id'], l['variant']])
with open(os.path.join(OUT, 'data/csv', 'variants.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['variant_id', 'variant_name', 'variant_of_id', 'variant_of', 'variant_type', 'records'])
    for v in reg['variants']: w.writerow([v[k] for k in ('variant_id', 'variant_name', 'variant_of_id', 'variant_of', 'variant_type', 'records')])
lic = urllib.request.urlopen(urllib.request.Request('https://creativecommons.org/licenses/by/4.0/legalcode.txt', headers={'User-Agent': 'kgdse-release/1.0'}), timeout=30).read().decode('utf-8')
open(os.path.join(OUT, 'LICENSE'), 'w', encoding='utf-8').write(lic)   # pure legal code so GitHub detects CC-BY-4.0; scope stated in README
open(os.path.join(OUT, 'LICENSE-CODE'), 'w', encoding='utf-8').write(f'''MIT License

Copyright (c) {datetime.date.today().year} Boniface Chukwuemeka Godwin and Petar Tomov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''')
open(os.path.join(OUT, 'CITATION.cff'), 'w', encoding='utf-8').write(f'''cff-version: 1.2.0
message: "If you use this resource, please cite it as below."
title: "KG-DSE: a traceable evidence graph of dataset use in knowledge graph research"
version: 0.1.0
date-released: {datetime.date.today().isoformat()}
license: CC-BY-4.0
repository-code: "https://github.com/gate-institute/kg-datasets"
url: "https://w3id.org/kgdse"
authors:
  - family-names: Godwin
    given-names: Boniface Chukwuemeka
    affiliation: "Carnegie Mellon University"
  - family-names: Tomov
    given-names: Petar
    affiliation: "GATE Institute, Sofia University"
''')
open(os.path.join(OUT, 'README.md'), 'w', encoding='utf-8').write('''# KG-DSE: dataset use in knowledge graph research

A traceable evidence graph that links knowledge graph (KG) research categories, tasks and subtasks to the
datasets used for them, and every link to its location in the published literature. It was built through a
systematic mapping study (Kitchenham and Charters guidelines; PRISMA 2020 reporting).

**Browse:** https://gate-institute.github.io/kg-datasets/ (datasets, taxonomy, every record with its evidence location).

**Status:** version 0.1.0 (pre-release, 14 Nov 2026). Persistent identifier https://w3id.org/kgdse (being registered); DOI to follow (Zenodo).

## What is in it
| | |
|---|---|
| Reports assessed in full text | 1,085 (869 included, 216 excluded with reason) |
| Unique included studies | 867 |
| Dataset-use records (active) | 1,690, each with section/table/page of the evidence |
| Datasets | 1,203 canonical datasets + 50 variants |
| Taxonomy | 15 research categories, 70 subtasks in use, 12 facets, 11 domains |
| Dataset descriptors | 72 most-used datasets (5+ records): kind, source, input/output, creation, verification, size, access, licence, one real sample; every value with source and quote |
| Graph | 73,056 triples (SKOS, DCAT, PROV-O, Dublin Core); SHACL-validated |

All screening, extraction and coding decisions were made by a single reviewer (B. C. Godwin), with AI-assisted
extraction; every decision is logged in the graph (`kd:Decision`) and in `data/json/master.json`.

## Files
- `data/kgdse.ttl`, `data/kgdse.nt`: the graph (Turtle, N-Triples).
- `model/kgdse-vocab.ttl`: the `kd:` vocabulary (https://w3id.org/kgdse/vocab#); `model/kgdse-shapes.ttl`: SHACL shapes.
- `queries/cq1.rq` ... `cq8.rq`: competency queries (questions in `model/competency_questions.txt`), first results in `queries/results_summary.txt`.
- `data/csv/`: evidence records, reports, peripheral records, datasets (with descriptors and samples), dataset links, variants.
- `data/json/`: the build inputs (`master.json`, `registry.json`).
- `scripts/`: `build_rdf.py` (JSON -> RDF), `validate.py` (SHACL + count checks), `competency_queries.py`, `build_site.py` (website data).
- `docs/`: the website (GitHub Pages; plain HTML, CSS and JavaScript, no external libraries or tracking).

## Quick start
```bash
pip install rdflib pyshacl
python scripts/build_rdf.py          # rebuild data/kgdse.ttl from data/json
python scripts/validate.py           # SHACL and count checks
python scripts/competency_queries.py # run CQ1-CQ8
```
Or load `data/kgdse.ttl` into any SPARQL store and run the queries in `queries/`.

## Identifiers
`https://w3id.org/kgdse/record/B01-R001` (records), `.../dataset/KGD-0001` (datasets), `.../variant/KGV-001`,
`.../report/B01-S04`, `.../study/B01-S04`, `.../subtask/CMP-01`, `.../category/<slug>`, `.../decision/<n>`.

## Licence
Data (graph, vocabulary, shapes, queries, CSV, JSON): CC BY 4.0. Code (`scripts/`): MIT. Dataset samples quote
one item per dataset under that dataset's own licence, recorded with each sample; where the terms forbid copying,
no sample is given.

## Citation
See `CITATION.cff`. Paper: Godwin and Tomov, ESWC 2027 Resources Track (submitted).
''')
total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
for dp, _, fs in os.walk(OUT):
    for f in sorted(fs): print(os.path.relpath(os.path.join(dp, f), OUT), os.path.getsize(os.path.join(dp, f)))
print('total MB', round(total / 1e6, 1))
