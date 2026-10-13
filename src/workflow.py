from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil

import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
SCORES = {'code_quality': 3, 'documentation': 2, 'examples': 2}
ISSUES = ['none', 'correctness', 'missing_validation', 'missing_documentation',
          'missing_examples', 'mixed', 'uncertain']
REQUIRED = list(SCORES) + ['primary_issue', 'evaluation_confidence', 'comment']
FIELDS = ['instruction', 'response', 'validation_context']
METADATA = ['prompt_id', 'candidate_alias', 'topic', 'data_origin']


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')


def validate_records(records):
    if len(records) < 5: raise ValueError('Use at least five response records, preferably ten or more.')
    ids = set(); pairs = defaultdict(set)
    for item in records:
        rid = item.get('record_id')
        if not isinstance(rid, str) or not rid.strip() or rid in ids: raise ValueError('Unique nonempty record_id required.')
        ids.add(rid)
        for f in FIELDS:
            if not isinstance(item.get(f), str) or not item[f].strip(): raise ValueError(f'Missing text field {f}')
        for f in METADATA:
            if not isinstance(item.get(f), str) or not item[f].strip(): raise ValueError(f'Missing metadata {f}')
        pair = (item['prompt_id'], item['candidate_alias'])
        if item['candidate_alias'] in pairs[item['prompt_id']]: raise ValueError('Duplicate prompt/candidate pair.')
        pairs[item['prompt_id']].add(item['candidate_alias'])
    return records


def config_description(min_submitted=1):
    if not isinstance(min_submitted, int) or min_submitted < 1: raise ValueError('min_submitted must be positive.')
    return {
        'dataset_name': os.getenv('ARGILLA_DATASET', 'energy-code-human-evaluation'),
        'workspace': os.getenv('ARGILLA_WORKSPACE', 'argilla'),
        'fields': [{'name': f, 'type': 'TextField', 'required': True, 'use_markdown': True} for f in FIELDS],
        'questions': [
            {'name': k, 'type': 'RatingQuestion', 'values': list(range(v+1)), 'required': True}
            for k,v in SCORES.items()
        ] + [{'name': 'primary_issue', 'type': 'LabelQuestion', 'labels': ISSUES, 'required': True},
             {'name': 'evaluation_confidence', 'type': 'LabelQuestion', 'labels': ['high','low'], 'required': True},
             {'name': 'comment', 'type': 'TextQuestion', 'required': True}],
        'metadata': [{'name': k, 'type': 'TermsMetadataProperty'} for k in METADATA],
        'min_submitted': min_submitted,
        'score_computation': 'code_quality + documentation + examples (0-7), computed after export',
        'suggestions': 'none; first-pass human ratings should not be anchored to automated suggestions',
        'deployment_status': 'configuration prepared, remote deployment not verified',
    }


def make_settings(min_submitted=1):
    """Call after establishing a real Argilla client; SDK resources use its default."""
    import argilla as rg
    config_description(min_submitted)
    return rg.Settings(
        guidelines=(ROOT/'annotator_guidelines.md').read_text(encoding='utf-8'),
        fields=[rg.TextField(name=f, required=True, use_markdown=True) for f in FIELDS],
        questions=[
            rg.RatingQuestion(name='code_quality', values=[0,1,2,3], title='Code correctness and robustness (0-3)',
                description='0 unusable; 1 major functional errors; 2 minor limitations; 3 correct and robust on specified checks.'),
            rg.RatingQuestion(name='documentation', values=[0,1,2], title='Documentation (0-2)',
                description='0 none; 1 partial; 2 clear docstring and useful explanation of inputs, units and invalid cases.'),
            rg.RatingQuestion(name='examples', values=[0,1,2], title='Examples (0-2)',
                description='0 none/incorrect; 1 correct ordinary example only; 2 correct ordinary and edge example with expected behavior.'),
            rg.LabelQuestion(name='primary_issue', labels=ISSUES, title='Primary issue',
                description='Choose the most consequential issue; use uncertain if evidence is insufficient.'),
            rg.LabelQuestion(name='evaluation_confidence', labels=['high','low'], title='Evaluation confidence',
                description='Low if testing/evidence is incomplete or interpretation is unresolved.'),
            rg.TextQuestion(name='comment', required=True, title='Evidence and rationale',
                description='Record a concrete check/result and explain the score. Do not paste credentials or personal details.'),
        ],
        metadata=[rg.TermsMetadataProperty(name=f) for f in METADATA],
        distribution=rg.TaskDistribution(min_submitted=min_submitted),
        allow_extra_metadata=False,
    )


def connect():
    import argilla as rg
    load_dotenv()
    url, key = os.getenv('ARGILLA_API_URL'), os.getenv('ARGILLA_API_KEY')
    if not url or not key: raise ValueError('Set ARGILLA_API_URL and ARGILLA_API_KEY locally in .env.')
    headers = {'Authorization': f'Bearer {os.environ["HF_TOKEN"]}'} if os.getenv('HF_TOKEN') else {}
    client = rg.Argilla(api_url=url, api_key=key, headers=headers, timeout=30, retries=2)
    _ = client.me
    print('Argilla connection verified; credentials are not printed.')
    return client


def get_dataset(client):
    dataset = client.datasets(name=os.getenv('ARGILLA_DATASET','energy-code-human-evaluation'),
                              workspace=os.getenv('ARGILLA_WORKSPACE','argilla'))
    if dataset is None: raise ValueError('Dataset not found. Run create, then upload.')
    return dataset


def create_dataset(client, min_submitted=1):
    import argilla as rg
    name = os.getenv('ARGILLA_DATASET','energy-code-human-evaluation')
    workspace = os.getenv('ARGILLA_WORKSPACE','argilla')
    if client.workspaces(workspace) is None: raise ValueError('Workspace absent; create/select it in the Argilla UI.')
    if client.datasets(name=name, workspace=workspace) is not None:
        raise ValueError('Dataset already exists. Reuse it for upload/export or choose a new name; nothing is deleted.')
    dataset = rg.Dataset(name=name, workspace=workspace, settings=make_settings(min_submitted), client=client).create()
    write_json(ROOT/'outputs/live/dataset_configuration.json',config_description(min_submitted))
    print('Created dataset:',name)
    return dataset


def upload_records(dataset, records, limit=None):
    """Stable external IDs; no response/suggestion fixture is uploaded."""
    import argilla as rg
    validate_records(records)
    if limit is not None and (not isinstance(limit,int) or limit < 1):
        raise ValueError('limit must be a positive integer.')
    existing = {str(r.id): r for r in dataset.records(with_responses=True)}
    selected = records[:limit] if limit else records
    new=[]; reused=0
    for item in selected:
        fields = {f:item[f] for f in FIELDS}
        if item['record_id'] in existing:
            old = existing[item['record_id']]
            if dict(old.fields) != fields or dict(old.metadata) != {f:item[f] for f in METADATA}:
                raise ValueError('Existing record content/metadata changed; use a new dataset/version rather than overwrite annotations.')
            reused+=1;continue
        new.append(rg.Record(id=item['record_id'], fields=fields, metadata={f:item[f] for f in METADATA}))
    if new: dataset.records.log(new)
    actual = {str(r.id) for r in dataset.records()}
    if not {x['record_id'] for x in selected}.issubset(actual):
        raise ValueError('Upload verification failed: one or more record IDs missing. Inspect server before retry.')
    print(f'Uploaded {len(new)} new records; reused {reused} identical records.')
    return len(new),reused


def snapshot_records(dataset):
    """Preserve per-user response status; to_list() alone omits it in SDK2.8."""
    result=[]
    for record in dataset.records(with_responses=True, with_suggestions=True):
        responses=[]
        for response in record.responses:
            responses.append({'question_name':response.question_name, 'value':response.value,
                              'user_id':str(response.user_id),
                              'status':getattr(response.status,'value',response.status)})
        result.append({'record_id':str(record.id),'server_record_id':str(record._server_id or ''),
            'fields':dict(record.fields),'metadata':dict(record.metadata),
            'responses':responses, 'suggestions':[s.serialize() for s in record.suggestions],
            'annotation_source':'argilla_user_response', 'exported_at':datetime.now(timezone.utc).isoformat()})
    return result


def flatten_annotations(payload):
    """One row per record/annotator; only a complete submitted response qualifies."""
    rows=[]; rejected=[]; seen_records=set()
    for item in payload:
        rid=item['record_id']
        if rid in seen_records: raise ValueError('Duplicate record in export.')
        seen_records.add(rid)
        grouped=defaultdict(dict); status=defaultdict(list)
        for response in item.get('responses',[]):
            user=response.get('user_id')
            if not user: raise ValueError('Response has no annotator ID; cannot attribute or pair scores.')
            q=response['question_name']
            if q in grouped[user]: raise ValueError('Duplicate question/annotator response.')
            grouped[user][q]=response['value'];status[user].append(response.get('status'))
        for user, answers in grouped.items():
            reason=''
            if not all(s=='submitted' for s in status[user]): reason='not_fully_submitted'
            elif not set(REQUIRED).issubset(answers): reason='missing_required_answers'
            else:
                for name,max_value in SCORES.items():
                    v=answers[name]
                    if isinstance(v,bool) or not isinstance(v,int) or not 0<=v<=max_value:
                        reason='invalid_score';break
                if answers.get('primary_issue') not in ISSUES: reason='invalid_issue'
                if answers.get('evaluation_confidence') not in ['high','low']: reason='invalid_confidence'
                if not isinstance(answers.get('comment'),str) or not answers['comment'].strip(): reason='empty_comment'
            if reason:
                rejected.append({'record_id':rid,'annotator_id':user,'reason':reason});continue
            meta=item['metadata']; fields=item['fields']
            if any(not meta.get(f) for f in METADATA): raise ValueError('Export missing required metadata.')
            rows.append({'record_id':rid,'annotator_id':user,
                **{f:meta[f] for f in METADATA},**{f:fields[f] for f in FIELDS},
                **{q:answers[q] for q in REQUIRED},'total_score':sum(answers[q] for q in SCORES),
                'annotation_source':item.get('annotation_source','unknown'),
                'response_status':'submitted','exported_at':item.get('exported_at','')})
    columns=['record_id','annotator_id',*METADATA,*FIELDS,*REQUIRED,'total_score','annotation_source','response_status','exported_at']
    return pd.DataFrame(rows,columns=columns),pd.DataFrame(rejected,columns=['record_id','annotator_id','reason'])


def analyze(annotations, total_records):
    if annotations.empty: raise ValueError('No complete submitted annotations. Annotate in the UI before analysis.')
    if annotations.duplicated(['record_id','annotator_id']).any(): raise ValueError('Duplicate record/annotator rows.')
    if annotations.groupby('record_id')[['prompt_id','candidate_alias']].nunique().gt(1).any().any():
        raise ValueError('A record has inconsistent prompt/candidate metadata.')
    for name,max_value in SCORES.items():
        numeric=pd.to_numeric(annotations[name],errors='raise')
        if numeric.isna().any() or not numeric.between(0,max_value).all() or not numeric.mod(1).eq(0).all():
            raise ValueError('Invalid score range/type.')
    if not annotations.total_score.eq(annotations[list(SCORES)].sum(axis=1)).all():
        raise ValueError('Total score does not equal component sum.')
    record=annotations.groupby(['record_id','prompt_id','candidate_alias'],as_index=False)[list(SCORES)+['total_score']].mean()
    if len(record)>total_records: raise ValueError('Annotated records exceed source count.')
    overall=record.total_score
    # Equal record weighting: extra annotators do not give a record extra influence.
    candidate=record.groupby('candidate_alias').total_score.agg(['count','mean','median','min','max']).reset_index()
    wide=record.pivot(index='prompt_id',columns='candidate_alias',values='total_score')
    pair_metrics={'matched_prompt_count':0,'mean_A_minus_B':None,'A_wins':0,'B_wins':0,'ties':0}
    paired=pd.DataFrame(columns=['candidate_A','candidate_B','difference_A_minus_B'])
    if {'candidate_A','candidate_B'}.issubset(wide):
        paired=wide[['candidate_A','candidate_B']].dropna().copy()
        paired['difference_A_minus_B']=paired.candidate_A-paired.candidate_B
        if len(paired):
            d=paired.difference_A_minus_B
            pair_metrics={'matched_prompt_count':len(paired),'mean_A_minus_B':float(d.mean()),
                          'A_wins':int(d.gt(0).sum()),'B_wins':int(d.lt(0).sum()),'ties':int(d.eq(0).sum())}
    agreement=[]
    for rid,group in annotations.groupby('record_id'):
        if group.annotator_id.nunique()>=2:
            agreement.append({'record_id':rid,'annotators':group.annotator_id.nunique(),
                'score_range':float(group.total_score.max()-group.total_score.min()),
                'all_exact_total_agreement':bool(group.total_score.nunique()==1)})
    result={'annotation_rows':len(annotations),'annotated_records':len(record),'source_records':total_records,
        'coverage':len(record)/total_records if total_records else None,
        'annotators':int(annotations.annotator_id.nunique()),
        'overall_record_weighted':{'mean':float(overall.mean()),'median':float(overall.median()),
                                  'min':float(overall.min()),'max':float(overall.max())},
        'mean_components_record_weighted':record[list(SCORES)].mean().to_dict(),
        'paired_comparison':pair_metrics,
        'annotation_score_distribution':{str(k):int(v) for k,v in annotations.total_score.value_counts().sort_index().items()},
        'primary_issue_counts_annotation_weighted':annotations.primary_issue.value_counts().to_dict(),
        'low_confidence_annotation_rows':int(annotations.evaluation_confidence.eq('low').sum()),
        'multi_annotated_records':len(agreement),
        'exact_total_agreement':sum(x['all_exact_total_agreement'] for x in agreement)/len(agreement) if agreement else None,
        'data_origins':sorted(annotations.data_origin.unique().tolist()),
        'annotation_sources':sorted(annotations.annotation_source.unique().tolist())}
    return result,record,candidate,paired,pd.DataFrame(agreement,columns=[
        'record_id','annotators','score_range','all_exact_total_agreement'])


def run_analysis(payload, out, mode, write_root=True):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    annotations,rejected=flatten_annotations(payload)
    annotations.to_csv(out/'annotated_dataset.csv',index=False)
    rejected.to_csv(out/'excluded_responses.csv',index=False)
    write_json(out/'raw_annotation_export.json',payload)
    metrics,record,candidate,paired,agreement=analyze(annotations,len(payload))
    metrics.update(mode=mode,excluded_response_groups=len(rejected),
        deployment_verified=False,human_annotations_independently_verified=False,
        limitations=['Submitted responses are attributed to Argilla users, not independently verified people.'] if mode=='live' else
                     ['Synthetic candidate answers and reference scores; not actual LLM outputs or human annotations.',
                      'No Argilla Space was created, uploaded, or exported in this demo.'])
    write_json(out/'analysis_metrics.json',metrics)
    record.to_csv(out/'record_scores.csv',index=False);candidate.to_csv(out/'candidate_statistics.csv',index=False)
    paired.to_csv(out/'paired_comparison.csv',index=True,index_label='prompt_id')
    agreement.to_csv(out/'agreement_by_record.csv',index=False)
    stats=metrics['overall_record_weighted']; pairs=metrics['paired_comparison']
    label='synthetic demonstration' if mode=='demo' else 'Argilla submitted-response export'
    paragraph=(f'The {label} contains {len(annotations)} complete annotation rows across {len(record)} of {len(payload)} response records '
        f'({metrics["coverage"]:.0%} coverage); the record-weighted mean is {stats["mean"]:.2f}/7 '
        f'(median {stats["median"]:.2f}, range {stats["min"]:.0f}-{stats["max"]:.0f}). '
        f'Across {pairs["matched_prompt_count"]} matched prompts, candidate A wins {pairs["A_wins"]}, candidate B wins {pairs["B_wins"]}, and {pairs["ties"]} tie; '
        'the demo fixtures illustrate how correct edge-case handling, documentation and examples affect the rubric' if mode=='demo' else
        f'The {label} contains {len(annotations)} complete annotation rows across {len(record)} of {len(payload)} response records '
        f'({metrics["coverage"]:.0%} coverage); the record-weighted mean is {stats["mean"]:.2f}/7. '
        f'Paired comparison covers {pairs["matched_prompt_count"]} prompts and includes only matched candidate A/B records; inspect comments and component scores before concluding which response is better')
    paragraph += ('; these are synthetic reference labels, so no human/model performance or inter-annotator reliability is established. '
                  'Next, obtain real model outputs, have a colleague review the guidelines, collect blind human ratings in Argilla and replace this demonstration with a live export.\n'
                  if mode=='demo' else '. The main remaining checks are guideline peer review, attribution verification and comment-based error review; next, adjudicate uncertain examples and collect a second independent rater on a shared sample.\n')
    (out/'lab_summary.md').write_text(paragraph,encoding='utf-8')
    if write_root:
        shutil.copy2(out/'annotated_dataset.csv',ROOT/'annotated_dataset.csv')
        shutil.copy2(out/'raw_annotation_export.json',ROOT/'annotated_dataset.json')
        shutil.copy2(out/'lab_summary.md',ROOT/'lab_summary.md')
    print(json.dumps(metrics,indent=2))
    return metrics


def main():
    parser=argparse.ArgumentParser(description='Offline demonstration and live Argilla annotation workflow.')
    parser.add_argument('action',choices=['demo','config','connect','create','upload','export'])
    parser.add_argument('--input',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--min-submitted',type=int,default=1)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--no-write-root',action='store_true')
    args=parser.parse_args();load_dotenv()
    if args.action=='demo':
        from .make_demo import generate_demo
        generate_demo()
        run_analysis(load_json(ROOT/'data/demo/reference_annotation_fixture.json'),args.output or ROOT/'outputs/demo','demo',not args.no_write_root)
    elif args.action=='config':
        write_json(args.output or ROOT/'dataset_settings.json',config_description(args.min_submitted));print('Wrote offline configuration; no server connection.')
    else:
        client=connect()
        if args.action=='connect':return
        if args.action=='create':create_dataset(client,args.min_submitted)
        elif args.action=='upload':
            records=validate_records(load_json(args.input or ROOT/'data/live/evaluation_records.json'))
            upload_records(get_dataset(client),records,args.limit)
        elif args.action=='export':
            payload=snapshot_records(get_dataset(client))
            if not payload:raise ValueError('Remote dataset is empty.')
            # Preserve raw export even if no submitted annotations are available.
            destination=args.output or ROOT/'outputs/live'
            write_json(destination/'raw_annotation_export.json',payload)
            run_analysis(payload,destination,'live',not args.no_write_root)


if __name__=='__main__':main()
