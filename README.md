# KG-DSE: dataset use in knowledge graph research

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
