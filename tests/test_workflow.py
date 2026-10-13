import contextlib,io,json,tempfile,unittest,copy
from pathlib import Path
from unittest.mock import Mock, patch
from types import SimpleNamespace
import pandas as pd
import httpx
import argilla as rg
from src.workflow import *
from src.make_demo import generate_demo

class WorkflowTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.records,cls.payload=generate_demo()
 def test_demo_structure(self):
  validate_records(self.records)
  self.assertEqual(len(self.records),20)
  self.assertEqual(len({x['prompt_id'] for x in self.records}),10)
  self.assertTrue(all(x['data_origin']=='synthetic_authored_demo' for x in self.records))
 def test_invalid_duplicate_and_missing_fields(self):
  for kind in ['duplicate','missing']:
   raw=copy.deepcopy(self.records)
   if kind=='duplicate':raw[1]['record_id']=raw[0]['record_id']
   else:raw[0]['response']=''
   with self.subTest(kind=kind),self.assertRaises(ValueError):validate_records(raw)
 def test_complete_annotations_and_scores(self):
  frame,rejected=flatten_annotations(self.payload)
  self.assertEqual(len(frame),20);self.assertTrue(rejected.empty)
  self.assertTrue(frame.total_score.eq(frame[list(SCORES)].sum(axis=1)).all())
  self.assertTrue(frame.annotation_source.eq('synthetic_reference_not_human').all())
 def test_drafts_not_counted_as_submissions(self):
  raw=copy.deepcopy(self.payload);raw[0]['responses'][0]['status']='draft'
  frame,rejected=flatten_annotations(raw)
  self.assertEqual(len(frame),19)
  self.assertEqual(rejected.reason.iloc[0],'not_fully_submitted')
 def test_incomplete_or_invalid_scores_excluded(self):
  for kind in ['missing','out_of_range','boolean','comment']:
   raw=copy.deepcopy(self.payload)
   if kind=='missing':raw[0]['responses'].pop()
   elif kind=='out_of_range':raw[0]['responses'][0]['value']=99
   elif kind=='boolean':raw[0]['responses'][0]['value']=True
   else:raw[0]['responses'][-1]['value']=''
   frame,rejected=flatten_annotations(raw)
   self.assertEqual(len(frame),19);self.assertEqual(len(rejected),1)
 def test_duplicate_user_question_rejected(self):
  raw=copy.deepcopy(self.payload);raw[0]['responses'].append(raw[0]['responses'][0])
  with self.assertRaises(ValueError):flatten_annotations(raw)
 def test_multiple_users_join_by_id_not_response_order(self):
  raw=copy.deepcopy(self.payload[:1]);extra=copy.deepcopy(raw[0]['responses'])
  for item in extra:item['user_id']='second-fixture'
  extra.reverse();raw[0]['responses']+=extra
  frame,rejected=flatten_annotations(raw)
  self.assertEqual(len(frame),2);self.assertTrue(rejected.empty)
  self.assertEqual(frame.annotator_id.nunique(),2)
 def test_record_weighting_and_pairing(self):
  frame,_=flatten_annotations(self.payload)
  metrics,_,_,pairs,_=analyze(frame,20)
  duplicate=frame.iloc[[0]].copy();duplicate['annotator_id']='second-fixture'
  weighted=pd.concat([frame,duplicate],ignore_index=True)
  after,_,_,_,_=analyze(weighted,20)
  self.assertEqual(metrics['overall_record_weighted']['mean'],after['overall_record_weighted']['mean'])
  self.assertEqual(after['multi_annotated_records'],1)
  self.assertEqual(len(pairs),10)
  self.assertEqual(metrics['paired_comparison']['A_wins'],5)
  self.assertEqual(metrics['paired_comparison']['B_wins'],5)
 def test_unmatched_pair_reported_and_partial_coverage(self):
  frame,_=flatten_annotations(self.payload[1:])
  m,_,_,pairs,_=analyze(frame,20)
  self.assertEqual(m['coverage'],19/20)
  self.assertEqual(len(pairs),9)
  self.assertIsNone(m['exact_total_agreement'])
 def test_no_annotation_failure_is_explicit(self):
  frame,_=flatten_annotations([{**self.payload[0],'responses':[]}])
  with self.assertRaises(ValueError):analyze(frame,1)
 def test_total_mismatch_rejected(self):
  frame,_=flatten_annotations(self.payload);frame.loc[0,'total_score']=7
  with self.assertRaises(ValueError):analyze(frame,20)
 def test_suggestions_never_count_as_annotations(self):
  raw=copy.deepcopy(self.payload[:1]);raw[0]['suggestions']=raw[0]['responses'];raw[0]['responses']=[]
  frame,rejected=flatten_annotations(raw);self.assertTrue(frame.empty)
 def test_real_sdk_settings_with_mock_transport(self):
  def handler(request):
   self.assertEqual(request.url.host,'offline.invalid')
   return httpx.Response(200,json={'id':'00000000-0000-4000-8000-000000000001','username':'offline','role':'owner'})
  http_client=httpx.Client(base_url='https://offline.invalid',transport=httpx.MockTransport(handler))
  with patch('argilla._api._client.create_http_client',return_value=http_client):
   client=rg.Argilla(api_url='https://offline.invalid',api_key='offline-test-key',retries=0)
  settings=make_settings()
  self.assertEqual(len(settings.fields),3)
  self.assertEqual(len(settings.questions),6)
  self.assertEqual(settings.distribution.min_submitted,1)
  self.assertEqual(settings.questions['code_quality'].values,[0,1,2,3])
 def test_snapshot_preserves_response_status(self):
  responses=[rg.Response('code_quality',3,user_id='00000000-0000-4000-8000-000000000001',status='submitted')]
  record=rg.Record(id='E1',fields={f:'text' for f in FIELDS},metadata={f:'value' for f in METADATA},responses=responses)
  dataset=SimpleNamespace(records=lambda **kwargs:[record])
  exported=snapshot_records(dataset)
  self.assertEqual(exported[0]['responses'][0]['status'],'submitted')
  self.assertEqual(exported[0]['responses'][0]['user_id'],'00000000-0000-4000-8000-000000000001')
 def test_upload_reuses_identical_and_rejects_changed(self):
  rec=self.records[0]
  old=SimpleNamespace(id=rec['record_id'],fields={f:rec[f] for f in FIELDS},metadata={f:rec[f] for f in METADATA})
  collection=Mock();collection.side_effect=lambda **kwargs:[old]
  dataset=SimpleNamespace(records=collection)
  with contextlib.redirect_stdout(io.StringIO()):new,reused=upload_records(dataset,self.records,limit=1)
  self.assertEqual((new,reused),(0,1));collection.log.assert_not_called()
  changed=copy.deepcopy(self.records);changed[0]['response']='changed'
  with self.assertRaises(ValueError):upload_records(dataset,changed,limit=1)
 def test_demo_export_not_human_claim(self):
  with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()):
   metrics=run_analysis(self.payload,tmp,'demo',False)
   self.assertFalse(metrics['human_annotations_independently_verified'])
   self.assertEqual(len(pd.read_csv(Path(tmp)/'annotated_dataset.csv')),20)
   paragraph=(Path(tmp)/'lab_summary.md').read_text().strip()
   self.assertNotIn('\n',paragraph);self.assertIn('synthetic',paragraph)

if __name__=='__main__':unittest.main()
