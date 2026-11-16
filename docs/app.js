/* KG-DSE static site. Routes mirror the resource URIs (https://w3id.org/kgdse/<kind>/<id>):
   #dataset/KGD-0001  #record/B01-R001  #subtask/CMP-01  #category/<slug>  #report/<key>  #datasets  #taxonomy  #data */
'use strict';
const GH = 'https://github.com/gate-institute/kg-datasets';
const RAW = 'https://raw.githubusercontent.com/gate-institute/kg-datasets/main/';
const LABEL = { resource_kind: 'Resource kind', introducing_source: 'Introducing source', derived_from: 'Derived from', input_unit: 'Input unit',
  input_type: 'Input type', output_unit: 'Output unit', output_type: 'Output type', input_source: 'Input source', target_source: 'Target source',
  creation_method: 'Creation method', human_verification: 'Human verification', size: 'Size', access_status: 'Access status', licence: 'Licence' };
let S = null, DS = {}, CAT = {}, SUB = {}, BYDS = {}, BYSUB = {}, BYCAT = {}, REC = {};
const view = document.getElementById('view');
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmt = n => Number(n).toLocaleString('en-US');
const link = (h, t) => `<a href="#${esc(h)}">${esc(t)}</a>`;
const url = u => /^https?:\/\//.test(u) ? `<a href="${esc(u)}" rel="noopener">${esc(u)}</a>` : esc(u);

fetch('data/site.json').then(r => r.json()).then(d => {
  S = d;
  d.datasets.forEach(x => DS[x.id] = x);
  d.categories.forEach(c => { CAT[c.id] = c; c.subtasks.forEach(s => SUB[s.id] = Object.assign({ cat: c }, s)); });
  d.records.forEach(r => { REC[r.k] = r; (BYSUB[r.sub] = BYSUB[r.sub] || []).push(r); (BYCAT[r.cat] = BYCAT[r.cat] || []).push(r);
    r.ds.forEach(id => (BYDS[id] = BYDS[id] || []).push(r)); });
  route();
}).catch(e => { view.innerHTML = `<p>Could not load the data (${esc(e)}).</p>`; });
window.addEventListener('hashchange', route);

function route() {
  const h = decodeURIComponent(location.hash.replace(/^#\/?/, ''));
  const [kind, id] = h.split('/');
  const pages = { '': overview, datasets: datasetList, taxonomy: taxonomy, data: dataPage, dataset: () => dataset(id), record: () => record(id),
    subtask: () => subtask(id), category: () => category(id), report: () => report(id),
    study: () => report(id),   // a study's identifier is its canonical report key
    variant: () => { const p = S.datasets.find(x => x.variants.some(v => v[0] === id)); return p ? dataset(p.id) : notFound('variant', id); } };
  (pages[kind] || overview)();
  view.focus({ preventScroll: true }); window.scrollTo(0, 0);
}

function overview() {
  const m = S.meta;
  const top = S.datasets.filter(d => d.records > 0).sort((a, b) => b.records - a.records).slice(0, 10);
  view.innerHTML = `
  <h1>Which datasets are used for which knowledge graph tasks?</h1>
  <p class="lead">KG-DSE links knowledge graph research categories, tasks and subtasks to the datasets used for them, and every link to the
  exact place in the published literature where the use is documented. It was built through a systematic mapping study.</p>
  <div class="stats">
    ${[[m.records, 'dataset-use records'], [m.studies, 'included studies'], [m.datasets, 'datasets'], [m.described, 'datasets described in depth'],
       [m.categories, 'research categories'], [m.subtasks, 'subtasks'], [m.reports_assessed, 'reports assessed'], [m.decisions, 'logged decisions']]
      .map(([n, l]) => `<div class="stat"><b>${fmt(n)}</b><span>${l}</span></div>`).join('')}
  </div>
  <h2>Most used datasets</h2>
  <div class="tablewrap"><table><thead><tr><th>Dataset</th><th class="num">Records</th><th class="num">Studies</th><th>Main categories</th></tr></thead><tbody>
  ${top.map(d => `<tr><td>${link('dataset/' + d.id, d.name)}</td><td class="num">${fmt(d.records)}</td><td class="num">${fmt(d.studies)}</td>
    <td>${esc(d.categories.split('; ').slice(0, 2).join('; '))}</td></tr>`).join('')}
  </tbody></table></div>
  <p>Browse all ${link('datasets', 'datasets')}, the ${link('taxonomy', 'taxonomy')}, or download the ${link('data', 'data and queries')}.</p>
  <h2>How the evidence was collected</h2>
  <p>${fmt(m.reports_assessed)} reports were assessed in full text (${fmt(m.included)} included, ${fmt(m.excluded)} excluded with a reason).
  Each record gives the section, table and page of the evidence, the role of the dataset, and any limitation the authors reported, kept apart from
  the reviewer's own observations. Version ${esc(m.version)}, built ${esc(m.built)}.</p>`;
}

function datasetList() {
  const cats = S.categories.map(c => `<option value="${esc(c.label)}">${esc(c.label)}</option>`).join('');
  view.innerHTML = `<h1>Datasets</h1>
  <p class="muted">${fmt(S.meta.datasets)} datasets with documented use. The ${S.meta.described} most used (5 or more records) are described in depth.</p>
  <div class="controls">
    <input type="search" id="q" placeholder="Search names and aliases" aria-label="Search datasets">
    <select id="cat" aria-label="Filter by category"><option value="">All categories</option>${cats}</select>
    <select id="desc" aria-label="Filter by description"><option value="">All datasets</option><option value="1">Described in depth</option></select>
  </div>
  <p class="muted" id="count"></p>
  <div class="tablewrap"><table><thead><tr><th>Dataset</th><th class="num">Records</th><th class="num">Studies</th><th>Kind</th><th>Access</th></tr></thead>
  <tbody id="rows"></tbody></table></div>`;
  const q = document.getElementById('q'), cat = document.getElementById('cat'), desc = document.getElementById('desc');
  const draw = () => {
    const t = q.value.trim().toLowerCase();
    const list = S.datasets.filter(d => d.records > 0 && (!t || (d.name + ' ' + d.aliases + ' ' + d.id).toLowerCase().includes(t))
      && (!cat.value || d.categories.includes(cat.value)) && (!desc.value || d.desc)).sort((a, b) => b.records - a.records || a.name.localeCompare(b.name));
    document.getElementById('count').textContent = `${fmt(list.length)} datasets`;
    document.getElementById('rows').innerHTML = list.slice(0, 400).map(d => `<tr><td>${link('dataset/' + d.id, d.name)}</td><td class="num">${fmt(d.records)}</td>
      <td class="num">${fmt(d.studies)}</td><td>${esc(d.desc ? d.desc.resource_kind : '')}</td><td>${esc(d.desc ? d.desc.access_status : '')}</td></tr>`).join('')
      + (list.length > 400 ? `<tr><td colspan="5" class="muted">Showing the first 400. Narrow the search to see more.</td></tr>` : '');
  };
  [q, cat, desc].forEach(e => e.addEventListener('input', draw)); draw();
}

function recordRows(rs) {
  return `<div class="tablewrap"><table><thead><tr><th>Record</th><th>Study</th><th>Subtask</th><th>Roles</th><th>Evidence location</th></tr></thead><tbody>
  ${rs.map(r => `<tr><td>${link('record/' + r.k, r.k)}</td><td>${link('report/' + r.rep, (S.reports[r.rep] || {}).a || r.rep)}</td>
    <td>${SUB[r.sub] ? link('subtask/' + r.sub, SUB[r.sub].label) : esc(r.sub)}</td><td>${esc(r.roles)}</td><td>${esc(r.loc)}</td></tr>`).join('')}
  </tbody></table></div>`;
}

function dataset(id) {
  const d = DS[id];
  if (!d) return notFound('dataset', id);
  const rs = (BYDS[id] || []);
  let h = `<p class="muted">${link('datasets', 'Datasets')} / ${esc(d.id)}</p><h1>${esc(d.name)}</h1>
  <p><code>https://w3id.org/kgdse/dataset/${esc(d.id)}</code></p>
  ${d.aliases ? `<p>Also recorded as: ${esc(d.aliases)}</p>` : ''}
  <div class="stats"><div class="stat"><b>${fmt(d.records)}</b><span>records</span></div><div class="stat"><b>${fmt(d.studies)}</b><span>studies</span></div></div>
  <dl class="kv"><dt>Categories</dt><dd>${esc(d.categories)}</dd><dt>Roles</dt><dd>${esc(d.roles)}</dd>
  ${d.variants.length ? `<dt>Variants</dt><dd>${d.variants.map(v => `<span class="pill">${esc(v[1])} (${esc(v[2])})</span>`).join('')}</dd>` : ''}
  ${d.notes ? `<dt>Notes</dt><dd>${esc(d.notes)}</dd>` : ''}</dl>`;
  if (d.desc) {
    h += `<h2>Description</h2><dl class="kv">${Object.keys(LABEL).filter(f => d.desc[f] != null).map(f => `<dt>${LABEL[f]}</dt><dd>${esc(d.desc[f])}
      ${d.ev && d.ev[f] ? `<div class="quote">${d.ev[f][1] ? '"' + esc(d.ev[f][1]) + '" ' : ''}(${url(d.ev[f][0])})</div>` : ''}</dd>`).join('')}</dl>`;
    const s = d.sample;
    if (s) {
      h += `<h2>Sample</h2><div class="card">` + (s.sample_input ? `<p><b>Input</b></p><pre>${esc(s.sample_input)}</pre>
        ${s.sample_output && s.sample_output !== 'not applicable' ? `<p><b>Output</b></p><pre>${esc(s.sample_output)}</pre>` : ''}`
        : `<p>No sample reproduced (${esc(s.status)}).${s.official_example_url ? ' Official example: ' + url(s.official_example_url) : ''}</p>`) +
        `<p class="quote">${esc(s.selection)}. Source: ${esc(s.source_label)}${s.source_url ? ', ' + url(s.source_url) : ''}. Licence: ${esc(s.licence)}.</p></div>`;
    }
  } else {
    h += `<p class="muted">Descriptors: ${esc(d.status)}.</p>`;
  }
  h += `<h2>Documented uses (${rs.length})</h2>` + (rs.length ? recordRows(rs) : '<p class="muted">None.</p>');
  view.innerHTML = h;
}

function record(id) {
  const r = REC[id];
  if (!r) return notFound('record', id);
  const rep = S.reports[r.rep] || {};
  const c = CAT[r.cat];
  view.innerHTML = `<p class="muted">Record ${esc(r.k)}</p><h1>${esc(r.task)}</h1>
  <p><code>https://w3id.org/kgdse/record/${esc(r.k)}</code></p>
  <dl class="kv">
    <dt>Report</dt><dd>${link('report/' + r.rep, rep.c || r.rep)}</dd>
    <dt>Category</dt><dd>${c ? link('category/' + c.id, c.label) : ''}</dd>
    <dt>Subtask</dt><dd>${SUB[r.sub] ? link('subtask/' + r.sub, r.sub + ' ' + SUB[r.sub].label) : esc(r.sub)}</dd>
    <dt>Datasets</dt><dd>${r.ds.map(x => DS[x] ? link('dataset/' + x, DS[x].name) : esc(x)).join(', ')}</dd>
    <dt>Dataset as stated</dt><dd>${esc(r.dv)}</dd>
    <dt>Documented use</dt><dd>${esc(r.use)}</dd>
    <dt>Roles</dt><dd>${esc(r.roles)}</dd>
    ${r.met ? `<dt>Metrics named</dt><dd>${esc(r.met)}</dd>` : ''}
    <dt>Evidence location</dt><dd>${esc(r.loc)} (${esc(r.pc)}s)</dd>
    <dt>Version</dt><dd>${esc(r.vs)}</dd>
    <dt>Domains</dt><dd>${esc(r.dom)}</dd>${r.fac ? `<dt>Facets</dt><dd>${esc(r.fac)}</dd>` : ''}
    ${r.dl ? `<dt>Dataset limitation (authors)</dt><dd>${esc(r.dl)}</dd>` : ''}
    ${r.ss ? `<dt>Study scope</dt><dd>${esc(r.ss)}</dd>` : ''}
    ${r.ri ? `<dt>Reviewer interpretation</dt><dd>${esc(r.ri)}</dd>` : ''}
  </dl>`;
}

function report(key) {
  const rep = S.reports[key];
  if (!rep) return notFound('report', key);
  const rs = S.records.filter(r => r.rep === key);
  view.innerHTML = `<p class="muted">Report ${esc(key)}</p><h1>${esc(rep.c)}</h1>
  <dl class="kv"><dt>Authors</dt><dd>${esc(rep.a)}</dd>${rep.ps ? `<dt>Publication status</dt><dd>${esc(rep.ps)}</dd>` : ''}
  ${rep.acc ? `<dt>Code and data</dt><dd>${esc(rep.acc)}</dd>` : ''}</dl>
  <h2>Records (${rs.length})</h2>${recordRows(rs)}`;
}

function taxonomy() {
  view.innerHTML = `<h1>Taxonomy</h1><p class="muted">${S.categories.length} research categories and ${S.meta.subtasks} subtasks in use, with active records per node.</p>
  <div class="cats">${S.categories.slice().sort((a, b) => b.records - a.records).map(c => `<div class="card">
    <h3>${link('category/' + c.id, c.label)}</h3><p class="muted">${fmt(c.records)} records, ${fmt(c.studies)} studies, ${fmt(c.datasets)} datasets</p>
    <ul>${c.subtasks.filter(s => s.records > 0).sort((a, b) => b.records - a.records).map(s => `<li>${link('subtask/' + s.id, s.label)} <span class="muted">(${s.records})</span></li>`).join('')}</ul>
  </div>`).join('')}</div>
  <h2>Facets</h2><p>${S.facets.map(f => `<span class="pill">${esc(f[0])} ${esc(f[1])}</span>`).join('')}</p>
  <h2>Roles</h2><dl class="kv">${S.roles.map(r => `<dt>${esc(r[0])}</dt><dd>${esc(r[1])}</dd>`).join('')}</dl>`;
}

function topDatasets(rs, n) {
  const c = {};
  rs.forEach(r => r.ds.forEach(id => c[id] = (c[id] || new Set()).add(r.study)));
  return Object.entries(c).map(([id, s]) => [id, s.size]).sort((a, b) => b[1] - a[1]).slice(0, n);
}
function category(id) {
  const c = CAT[id];
  if (!c) return notFound('category', id);
  const rs = BYCAT[id] || [];
  view.innerHTML = `<p class="muted">${link('taxonomy', 'Taxonomy')}</p><h1>${esc(c.label)}</h1>
  <p class="muted">${fmt(c.records)} records, ${fmt(c.studies)} studies, ${fmt(c.datasets)} datasets</p>
  <h2>Subtasks</h2><ul>${c.subtasks.filter(s => s.records > 0).map(s => `<li>${link('subtask/' + s.id, s.label)} (${s.records}): <span class="muted">${esc(s.def)}</span></li>`).join('')}</ul>
  <h2>Most used datasets (by studies)</h2><ul>${topDatasets(rs, 15).map(([d, n]) => `<li>${link('dataset/' + d, DS[d] ? DS[d].name : d)} (${n})</li>`).join('')}</ul>`;
}
function subtask(id) {
  const s = SUB[id];
  if (!s) return notFound('subtask', id);
  const rs = BYSUB[id] || [];
  view.innerHTML = `<p class="muted">${link('taxonomy', 'Taxonomy')} / ${link('category/' + s.cat.id, s.cat.label)}</p><h1>${esc(id)} ${esc(s.label)}</h1>
  <p>${esc(s.def)}</p><p><code>https://w3id.org/kgdse/subtask/${esc(id)}</code></p>
  <h2>Most used datasets (by studies)</h2><ul>${topDatasets(rs, 15).map(([d, n]) => `<li>${link('dataset/' + d, DS[d] ? DS[d].name : d)} (${n})</li>`).join('')}</ul>
  <h2>Records (${rs.length})</h2>${recordRows(rs)}`;
}

function dataPage() {
  view.innerHTML = `<h1>Data and queries</h1>
  <p>The full graph and every input are in the <a href="${GH}">GitHub repository</a> (data CC BY 4.0, code MIT).</p>
  <ul>
    <li><a href="${RAW}data/kgdse.ttl">kgdse.ttl</a> (Turtle) and <a href="${RAW}data/kgdse.nt">kgdse.nt</a> (N-Triples)</li>
    <li><a href="${RAW}model/kgdse-vocab.ttl">Vocabulary</a> (<code>https://w3id.org/kgdse/vocab#</code>) and <a href="${RAW}model/kgdse-shapes.ttl">SHACL shapes</a></li>
    <li>CSV: <a href="${RAW}data/csv/evidence.csv">records</a>, <a href="${RAW}data/csv/reports.csv">reports</a>, <a href="${RAW}data/csv/datasets.csv">datasets</a>,
      <a href="${RAW}data/csv/dataset_links.csv">dataset links</a></li>
    <li>Competency queries: <a href="${GH}/tree/main/queries">queries/</a></li>
  </ul>
  <h2>Example query</h2><p>Datasets used for link prediction (subtask CMP-01), by number of studies:</p>
  <pre>PREFIX kd: &lt;https://w3id.org/kgdse/vocab#&gt;
PREFIX rdfs: &lt;http://www.w3.org/2000/01/rdf-schema#&gt;
SELECT ?dataset (COUNT(DISTINCT ?study) AS ?studies) WHERE {
  ?r kd:recordStatus "active" ;
     kd:subtask &lt;https://w3id.org/kgdse/subtask/CMP-01&gt; ;
     kd:usesDataset ?d ; kd:study ?study .
  ?d rdfs:label ?dataset .
} GROUP BY ?dataset ORDER BY DESC(?studies)</pre>
  <h2>Cite</h2><p>See <a href="${GH}/blob/main/CITATION.cff">CITATION.cff</a>.</p>`;
}

function notFound(kind, id) { view.innerHTML = `<h1>Not found</h1><p>No ${esc(kind)} with identifier ${esc(id)}.</p><p>${link('', 'Back to the overview')}</p>`; }
