from pathlib import Path
import json,html
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

root=Path(__file__).resolve().parents[1]
m=json.loads((root/'outputs/demo/analysis_metrics.json').read_text())
a=pd.read_csv(root/'outputs/demo/annotated_dataset.csv');pairs=pd.read_csv(root/'outputs/demo/paired_comparison.csv')
navy='#102C54';blue='#166AE8';green='#17846E';sky='#EDF5FF';ink='#22344D';muted='#53687E'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(8,2.7),layout='constrained')
counts=a.total_score.value_counts().reindex(range(8),fill_value=0)
bars=ax.bar(counts.index,counts.values,color=blue,width=.64);ax.bar_label(bars,padding=3)
ax.set_ylim(0,12);ax.set_xticks(range(8));ax.set_xlabel('Cumulative score (0-7)');ax.set_ylabel('Synthetic annotation rows')
ax.set_title('Demo score distribution (n=20)',loc='left',fontweight='bold',color=navy)
fig.savefig(root/'figures/demo_score_distribution.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.2),layout='constrained')
x=range(len(pairs));ax.plot(x,pairs.candidate_A,'o-',color=blue,label='Candidate A');ax.plot(x,pairs.candidate_B,'s-',color=green,label='Candidate B')
ax.set_xticks(list(x),pairs.prompt_id);ax.set_ylim(-.3,7.5);ax.set_ylabel('Reference score /7');ax.legend(loc='lower right',ncols=2)
ax.set_title('Authored paired examples, not model performance',loc='left',fontweight='bold',color=navy)
fig.savefig(root/'figures/demo_paired_scores.png',dpi=180);plt.close(fig)

pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DVB',italic='DV',boldItalic='DVB')
s=getSampleStyleSheet()
for name,size,leading,color,font in [('Body',9.3,13.5,ink,'DV'),('Title',27,33,navy,'DVB'),('Head',17,22,navy,'DVB'),('Sub',11,16,blue,'DVB'),('Small',7.8,11,muted,'DV'),('Cell',7.8,10.8,ink,'DV'),('White',8,11,'#FFFFFF','DVB')]:
 s.add(ParagraphStyle(name='H'+name,fontName=font,fontSize=size,leading=leading,textColor=colors.HexColor(color),spaceAfter=8 if name not in ['Cell','White'] else 0,spaceBefore=5 if name=='Sub' else 0))
story=[]
def p(t,style='Body'):return Paragraph(t,s['H'+style])
def add(t,style='Body'):story.append(p(t,style))
def table(headers,rows,widths):
 data=[[p(html.escape(str(v)),'White') for v in headers]]+[[p(html.escape(str(v)),'Cell') for v in row] for row in rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(navy)),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor(sky)]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),8)]))
 story.append(t);story.append(Spacer(1,10))
def new(t):story.append(PageBreak());add(t,'Head')
add('HUMAN-IN-THE-LOOP EVALUATIONS','Sub')
add('A clear rubric.<br/>A traceable human judgment.','Title')
add('Lab solution package • Walid Barakat • 10 October2026','Small')
add('<b>Implemented workflow with an executed synthetic demonstration.</b> The package covers the nine lab steps with guidelines, dataset configuration, upload/export code, analysis, notebook and submission instructions. A real Argilla Space, provider outputs, colleague review and genuine human annotations were not available in the supplied brief.')
table(['20 responses','10 paired prompts','0-7 rubric'],[['Two authored candidates per task','Energy-themed Python helpers','Code3 + docs2 + examples2'],['20 synthetic reference rows','No live provider outputs','No human-rating claim']],[170,170,170])
add('Demonstration snapshot','Sub')
table(['Measure','Demo result','Limit'],[['Record-weighted mean','4.25/7','Synthetic reference labels only'],['Median / range','5.00 / 0-7','Not observed human judgment'],['Paired comparison','A wins5; B wins5','10 matched authored prompts'],['Mean A-B difference','-0.30 points','No model-ranking inference'],['Inter-annotator agreement','Not measured (null)','No shared genuine multi-rater sample']],[145,130,235])
add('Required deliverables are included','Sub')
add('Root annotator_guidelines.md, dataset_config.md, annotated_dataset.csv/JSON, one-short-paragraph lab_summary.md and README. Optional reflection, eight-cell executed notebook, blue HTML/PDF reports and16 offline tests support reproducibility. Root exports currently contain explicitly synthetic references.')
add('The brief requires a dedicated GitHub repository URL as the actual submission. No Space, colleague review, screenshot, human label or GitHub URL is fabricated. Follow the final-page checklist to replace demonstration evidence with the real workflow.','Small')

new('1 / Make the judgment reproducible')
add('Evaluate a response against its own instruction, units and edge-case contract. Use three component scores rather than a vague overall impression. Keep code correctness visible: polished documentation cannot make a wrong formula usable.')
table(['Component','Score','Decision anchor'],[['Code quality','0','Unusable: central formula, function or ordinary output wrong; syntax failure.'],['Code quality','1','Partly useful; major requirement fails, such as required validation or a central boundary.'],['Code quality','2','Main behavior works but a specific minor defect remains within the stated contract.'],['Code quality','3','Correct function/formula/units with required validation and ordinary/edge behavior.'],['Documentation','0 / 1 / 2','None or misleading / partial / clear docstring plus input, unit and invalid-case explanation.'],['Examples','0 / 1 / 2','None or wrong / correct ordinary only / correct ordinary and edge examples with expected behavior.']],[110,55,345])
add('Annotation sequence','Sub')
add('Read instruction, candidate answer and validation context. Check at least one normal and one edge case. Distinguish executed observations from static reasoning in the comment. Assign each component independently, choose the primary issue and evaluation confidence, then submit the complete record in Argilla. The total is calculated after export.')
add('If you cannot verify a critical point, use low confidence and describe the missing evidence. Do not claim tests ran when they did not. Unfamiliar generated code belongs in a disposable isolated environment without secrets or network access, not on your main working system.')
add('Pilot, peer review and disagreement','Sub')
add('A colleague must review guideline clarity. Use a three-record pilot: strong, weak and ambiguous answers, independently scored before discussion. Refine wording and preserve original scores separately from adjudication. Version the guideline; use a shared sample with two real raters before reporting agreement.')
add('Example: count_above([2],2) must return0 when “strictly above” is required. A >= comparison fails that boundary even if the answer looks neat. “By inspection, equality would count” is honest static evidence; “I tested it” needs an actual test.','Small')

new('2 / Configure the real Argilla annotation dataset')
add('The proposed dataset is <b>energy-code-human-evaluation</b>, in the existing <b>argilla</b> workspace. Each record contains one candidate response; prompt_id joins two answers to the same task. Anonymous aliases and randomized record order reduce reputation/position cues, but do not eliminate all bias.')
table(['Configuration','Defined contract'],[['Fields','Required Markdown-enabled instruction, response and validation_context.'],['Ratings','code_quality:0-3; documentation:0-2; examples:0-2.'],['Other questions','Required primary_issue label, high/low evaluation_confidence, and evidence-based comment.'],['Metadata','prompt_id, candidate_alias, topic, data_origin. Preserve actual model/run provenance separately.'],['Distribution','One submitted rating/record by default. Use min_submitted2 only with two real raters.'],['Suggestions','None uploaded in first pass; synthetic fixtures are not uploaded as human answers.']],[110,400])
add('Space and connection','Sub')
add('Use the official Argilla deployment template linked from its quickstart. Sign in to Hugging Face, choose visibility and verify the running UI. Record the actual direct hf.space URL, retrieve the key from My Settings, and keep secrets in local .env. Private Spaces require HF authorization. The package does not create a remote Space automatically.')
add('The live script uses the Argilla2.8 SDK to connect, check client.me, create Settings and Dataset, log records, and verify uploaded IDs. Start with two records. An existing dataset is not deleted; repeated identical records are reused, while changed text/metadata is rejected to protect earlier judgments.')
add('Persistence needs a current account/template check','Sub')
add('The lab and older Argilla docs describe “Small” storage. Current Hugging Face docs describe attached Storage Bucket volumes. Confirm that the actual database/data paths are durable in your deployment, rather than assuming private visibility or the old tier name guarantees persistence. Keep exports before restarts/settings changes.')
add('Offline SDK settings were validated under mocked HTTP. Successful local configuration is not proof that a Space is deployed or that its UI displays the dataset.','Small')

new('3 / Preserve the annotations before analyzing')
add('The export keeps original instruction/response, reference context, record ID, annotator ID, metadata, question values, comment and submission status. The raw JSON is an audit backup. The normalized CSV contains one row per record and annotator, not one row per question or per entire prompt pair.')
table(['Check','Analysis behavior'],[['Status','Only fully submitted response groups enter the scored dataset. Drafts and incomplete groups are excluded and recorded.'],['Validation','Reject duplicate question/user entries, invalid score ranges, empty required comments or missing metadata.'],['Attribution','Join questions by record ID and annotator ID; never rely on response order.'],['Suggestions','Retain separately; never count them as independent human labels.'],['Coverage','Annotated record count / all exported source records; partial annotation remains visible.'],['Weighting','Average ratings within each record first, then weight records equally for overall/candidate statistics.']],[105,405])
add('Why export response objects explicitly?','Sub')
add('In the tested Argilla2.8 SDK, the basic dictionary representation omits per-response submitted/draft status. The package snapshots individual response objects to retain it. This protects the analysis from silently treating a saved draft as a finished judgment.')
add('Matched comparisons and agreement','Sub')
add('A/B comparison joins record means on the same prompt and excludes incomplete pairs. It reports matched-prompt counts, wins, ties and score differences. With multiple raters, identical totals can conceal different component judgments. The optional exact-total agreement statistic is descriptive, not a chance-corrected reliability measure.')
add('The demonstration has one synthetic reference identity per response. There is no independent human overlap, so agreement is null. A model suggestion, demo fixture or extra copied row cannot provide human reliability evidence.','Small')

new('4 / Read the demo results with their limits')
add('Twenty authored candidates cover conversion, mean/peak load, capacity factor, battery runtime, tariffs, thresholds, PUE, percentage change and load factor. Reference scores were assigned for illustration; no human annotation session or candidate-code execution is claimed.')
story.append(Image(str(root/'figures/demo_score_distribution.png'),width=490,height=165))
story.append(Image(str(root/'figures/demo_paired_scores.png'),width=490,height=196))
add('Patterns in the synthetic comments','Sub')
add('Five references flag central correctness errors, four flag missing validation, and one flags mixed presentation gaps; ten have no issue. Reversed conversion and ratio formulas, equality counted as “above,” and empty/zero input handling are useful pilot cases. The rubric also separates correct functionality from missing documentation/examples.')
add('The mean is4.25/7; the two candidate groups win five prompts each. A small average difference (-0.30 A-B) does not show a generally superior model, especially with authored answers, purposive prompts and no genuine raters. The data supports a pipeline demonstration, not a production quality claim.')
add('For the real run, inspect actual comments and component scores, adjudicate unclear contracts, document sampling, and add an independent rater on shared examples. An automated arithmetic test can check specific outputs; human reviewers still assess explanation, relevance and the limits of the evidence.','Small')

new('5 / Run and complete the course submission')
table(['Phase','Action'],[['Offline start','Install requirements; run python -m src.workflow demo, then python -m unittest discover -s tests -v.'],['Genuine responses','Use previous actual provider outputs or opt into src.generate_responses. It makes20 logical API requests and creates no annotations.'],['Guideline review','Get real colleague feedback and pilot scores; complete docs/guideline_review.md.'],['Space/config/upload','Deploy official template, configure .env, connect/create, upload2 pilot records, verify UI, then upload full inputs.'],['Human rating/export','People annotate and submit in Argilla. Run python -m src.workflow export; inspect exclusions, coverage and attributed comments.'],['Required handoff','Use genuine root annotated_dataset.csv/JSON, guidelines, config description and one-paragraph summary. Record actual Space URL/evidence.'],['GitHub only','Publish a dedicated lab-only repository yourself and submit its real URL. No credentials or unrelated files.']],[115,395])
add('What was actually verified','Sub')
add('Sixteen offline tests pass, including SDK field/question construction under mocked HTTP, score validation, drafts, missing answers, multiple-user joins, record weighting, matched pairs, suggestion separation and repeat-upload protection. All eight notebook code cells ran sequentially in a shared Python process; native Jupyter startup was blocked by environment socket restrictions.')
add('The package is self-contained. README maps every file and provides live commands. The root short summary accurately describes the demo. PDF/HTML reports stay as demo reports after a live run; the live CSVs/metrics/summary and screenshots become the actual completion evidence.')
add('Sources and references','Sub')
for title,url in [
('Argilla quickstart','https://docs.argilla.io/latest/getting_started/quickstart/'),
('Argilla settings and questions','https://docs.argilla.io/latest/reference/argilla/settings/settings/'),
('Argilla human annotation UI','https://docs.argilla.io/latest/how_to_guides/annotate/'),
('Argilla record export','https://docs.argilla.io/latest/how_to_guides/import_export/'),
('Hugging Face Space storage','https://huggingface.co/docs/hub/spaces-storage')]:
 add(f'<link href="{url}" color="{blue}">{title}</link>','Small')
add('Requirements: supplied Human-in-the-loop Evaluations Extra lab brief. Full URLs, optional OpenAI generator reference and documentation dates are in docs/sources.md.','Small')

def footer(canvas,doc):
 canvas.setFillColor(colors.HexColor(navy));canvas.rect(0,A4[1]-12,A4[0],12,fill=1,stroke=0)
 canvas.setStrokeColor(colors.HexColor('#CADAEE'));canvas.line(42,38,A4[0]-42,38)
 canvas.setFont('DV',7);canvas.setFillColor(colors.HexColor(muted));canvas.drawString(42,25,'HUMAN-IN-THE-LOOP LAB  |  SYNTHETIC DEMO, HUMAN WORK PENDING')
 canvas.drawRightString(A4[0]-42,25,str(doc.page))
SimpleDocTemplate(str(root/'human_in_loop_solution_report.pdf'),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=37,bottomMargin=49,title='Human-in-the-loop Evaluations - Solution',author='Walid Barakat').build(story,onFirstPage=footer,onLaterPages=footer)

# Portable interactive results report, without implying it is an Argilla UI.
records=a[['record_id','prompt_id','candidate_alias','topic','instruction','response','validation_context','code_quality','documentation','examples','total_score','primary_issue','comment']].to_dict('records')
data=json.dumps(records,ensure_ascii=False).replace('<','\\u003c')
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Human-in-the-loop lab | synthetic demo</title><style>
:root{font-family:system-ui,Arial,sans-serif;color:#173252;background:#eff5fd}*{box-sizing:border-box}body{margin:0}header{background:#102c54;color:white;padding:34px 24px}header div,main{max-width:1160px;margin:auto}main{padding:28px 24px}.eyebrow{color:#89beff;font-size:12px;font-weight:700;letter-spacing:2px}h1{font-size:36px;margin:8px 0}h2{font-size:22px}.notice{background:#fff8df;border-left:5px solid #b8811b;padding:18px;line-height:1.6}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}.card,.panel{background:white;border:1px solid #d4e2f4;border-radius:12px;padding:20px}.panel{margin:20px 0}.number{font-size:32px;font-weight:750;color:#166ae8}.muted{font-size:14px;line-height:1.6;color:#53687e}.filters{display:flex;gap:12px;flex-wrap:wrap}input,select{font:inherit;padding:10px;border:1px solid #bad0e8;border-radius:7px;background:white}input{flex:1;min-width:190px}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:12px;vertical-align:top;border-bottom:1px solid #e0eaf6}th{background:#edf5ff;text-align:left}.tag{display:inline-block;border-radius:6px;background:#edf5ff;padding:5px 8px;white-space:nowrap}.strong{background:#def5e9;color:#17624e}summary{cursor:pointer;color:#166ae8}details{margin:8px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:15px;background:#f5f8fd;border-radius:6px;font-size:12px;line-height:1.6}a{color:#166ae8}li{margin:8px 0}@media(max-width:720px){.cards{grid-template-columns:repeat(2,1fr)}h1{font-size:28px}main{padding:20px 12px}}@media print{.filters{display:none}header{color:#102c54;background:white}}
</style></head><body><header><div><div class="eyebrow">HUMAN-IN-THE-LOOP EVALUATIONS EXTRA</div><h1>Evidence before the score</h1><p>Walid Barakat • 10 October2026 • offline lab solution</p></div></header><main>
<div class="notice"><b>Synthetic demonstration only.</b>20 candidate answers and reference labels were authored for this package. They are not actual LLM outputs, human annotations or a deployed Argilla export. This report is a demo results viewer; use Argilla for the required genuine annotation workflow.</div>
<div class="cards"><div class="card"><div class="number">20</div><p>Reference-labelled response records</p></div><div class="card"><div class="number">10</div><p>Paired energy coding tasks</p></div><div class="card"><div class="number">4.25/7</div><p>Record-weighted demo mean</p></div><div class="card"><div class="number">5 : 5</div><p>A/B matched-prompt wins</p></div></div>
<section class="panel"><h2>The cumulative rubric</h2><div class="scroll"><table><thead><tr><th>Component</th><th>Points</th><th>Decision</th></tr></thead><tbody><tr><td>Code quality</td><td>0-3</td><td>Unusable, major issue, minor issue, correct and robust</td></tr><tr><td>Documentation</td><td>0-2</td><td>None/misleading, partial, clear and useful</td></tr><tr><td>Examples</td><td>0-2</td><td>None/wrong, ordinary only, ordinary plus edge</td></tr></tbody></table></div><p class="muted">Total is computed after export. Keep component scores, an issue label, confidence and a concrete comment. Drafts and incomplete response groups are excluded. Agreement is not measured here: no genuine shared multi-rater sample exists.</p></section>
<section class="panel"><h2>Inspect demo reference scores and rationale</h2><div class="filters"><input id="search" aria-label="Search demo responses" placeholder="Search ID, instruction or rationale"><select id="candidate" aria-label="Candidate"><option value="all">All candidates</option><option value="candidate_A">Candidate A</option><option value="candidate_B">Candidate B</option></select><select id="score" aria-label="Score filter"><option value="all">All scores</option><option value="strong">Score7</option><option value="weak">Score0-3</option></select></div><p id="shown" class="muted" aria-live="polite"></p><div class="scroll"><table><thead><tr><th>Record</th><th>Code / docs / examples</th><th>Total</th><th>Issue and rationale</th><th>Candidate answer</th></tr></thead><tbody id="rows"></tbody></table></div></section>
<section class="panel"><h2>Complete the actual lab</h2><ol><li>Deploy the official Argilla Space template and record the real URL/persistence settings.</li><li>Collect genuine model responses; have a colleague review guidelines and run an independent pilot.</li><li>Create the configured dataset, test2 uploads, then upload the full inputs.</li><li>People rate independently in Argilla and submit complete annotations.</li><li>Export attributed responses, audit exclusions, inspect scores and comments, and write the root paragraph.</li><li>Publish a dedicated lab-only GitHub repository yourself and submit its actual URL.</li></ol><p class="muted">README and docs/requirements_checklist.md contain commands and evidence requirements. The packaged HTML/PDF remain synthetic demo reports after a live CLI export; use fresh live results for completion claims.</p></section>
<p class="muted">Sources: supplied lab brief; <a href="https://docs.argilla.io/latest/getting_started/quickstart/">Argilla quickstart</a> • <a href="https://docs.argilla.io/latest/how_to_guides/annotate/">Annotation UI</a> • <a href="https://docs.argilla.io/latest/how_to_guides/import_export/">Export</a></p></main>
<script>const records=__DATA__;const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));function render(){const term=document.getElementById('search').value.toLowerCase(),candidate=document.getElementById('candidate').value,score=document.getElementById('score').value;const filtered=records.filter(r=>(candidate==='all'||r.candidate_alias===candidate)&&(score==='all'||(score==='strong'?r.total_score===7:r.total_score<=3))&&[r.record_id,r.instruction,r.comment,r.response].join(' ').toLowerCase().includes(term));document.getElementById('shown').textContent=`Showing ${filtered.length} of ${records.length} synthetic reference records`;document.getElementById('rows').innerHTML=filtered.map(r=>`<tr><td>${esc(r.record_id)}<br><small>${esc(r.topic)}</small></td><td>${r.code_quality} / ${r.documentation} / ${r.examples}</td><td><span class="tag ${r.total_score===7?'strong':''}">${r.total_score}/7</span></td><td><b>${esc(r.primary_issue)}</b><p>${esc(r.comment)}</p></td><td><details><summary>Instruction, answer and context</summary><p>${esc(r.instruction)}</p><pre>${esc(r.response)}</pre><p>${esc(r.validation_context)}</p></details></td></tr>`).join('');}['search','candidate','score'].forEach(id=>document.getElementById(id).addEventListener('input',render));render();</script></body></html>'''.replace('__DATA__',data)
(root/'human_in_loop_demo_report.html').write_text(page,encoding='utf-8')
print('Created PDF and self-contained HTML demo report.')
