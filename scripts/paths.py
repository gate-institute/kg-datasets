"""Paths for the KG-DSE scripts. Works in two layouts:
- project layout: scripts in 'Resource Website and KG/05_scripts', sources in 'Master Table/master.json'
  and 'Dataset Registry/registry.json', outputs in 01_model, 02_data, 03_sparql;
- repository layout (github.com/gate-institute/kg-datasets): scripts in 'scripts', sources in 'data/json',
  outputs in model, data, queries."""
import os
HERE = os.path.dirname(os.path.abspath(__file__)); TOP = os.path.dirname(HERE)
REPO = os.path.isdir(os.path.join(TOP, 'data', 'json'))
if REPO:
    MASTER = os.path.join(TOP, 'data', 'json', 'master.json'); REGISTRY = os.path.join(TOP, 'data', 'json', 'registry.json')
    MODEL = os.path.join(TOP, 'model'); DATA = os.path.join(TOP, 'data'); QUERIES = os.path.join(TOP, 'queries')
else:
    ROOT = os.path.dirname(TOP)
    MASTER = os.path.join(ROOT, 'Master Table', 'master.json'); REGISTRY = os.path.join(ROOT, 'Dataset Registry', 'registry.json')
    MODEL = os.path.join(TOP, '01_model'); DATA = os.path.join(TOP, '02_data'); QUERIES = os.path.join(TOP, '03_sparql')
