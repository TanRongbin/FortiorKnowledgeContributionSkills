import concurrent.futures
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'skills/fortior-knowledge-contributor/scripts'))
import submit
from fastapi.testclient import TestClient
import gateway.app as gateway

class RetryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.payload=json.loads((ROOT/'skills/fortior-knowledge-contributor/examples/experience-example.json').read_text('utf8'))
  self.cfg={'FORTIOR_REQUEST_STATE_FILE':str(self.root/'请求 space.json'),'FORTIOR_CONTRIBUTION_ENDPOINT':'http://testserver'}
  self.env=patch.dict(os.environ,{'FORTIOR_GATEWAY_SINK':'mock','FORTIOR_GATEWAY_MODE':'open','FORTIOR_GATEWAY_MOCK_LOG':str(self.root/'mock.jsonl'),'FORTIOR_GATEWAY_RATE_LIMIT_PER_HOUR':'1000'});self.env.start();importlib.reload(gateway)
 def tearDown(self):self.env.stop();self.tmp.cleanup()
 def body(self):return {'type':'experience','payload':self.payload,'client_metadata':submit.metadata(self.payload,self.cfg)}
 def test_restart_returns_original_receipt_and_conflict(self):
  body=self.body();client=TestClient(gateway.app);one=client.post('/v1/contributions',json=body).json();importlib.reload(gateway)
  two=TestClient(gateway.app).post('/v1/contributions',json=self.body()).json()
  self.assertEqual(one['record_id'],two['record_id']);self.assertEqual(one['submission_id'],two['submission_id']);self.assertTrue(two['duplicate'])
  body['payload']={**self.payload,'title':'Different synthetic content'};self.assertEqual(client.post('/v1/contributions',json=body).status_code,409)
 def test_concurrent_and_independent_similar_content(self):
  body=self.body()
  def call(_):return TestClient(gateway.app).post('/v1/contributions',json=body).json()
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(call,range(4)))
  self.assertEqual(len({r['record_id'] for r in rows}),1)
  other=submit.metadata(self.payload,{**self.cfg,'FORTIOR_REQUEST_STATE_FILE':str(self.root/'independent.json')})
  self.assertNotEqual(TestClient(gateway.app).post('/v1/contributions',json={**body,'client_metadata':other}).json()['record_id'],rows[0]['record_id'])
 def test_success_then_response_timeout_reconciles_without_create(self):
  body=self.body();client=TestClient(gateway.app)
  def remote(method,url,payload,headers):
   response=client.post('/v1/contributions',json=payload)
   if not payload['client_metadata']['reconcile_only']:raise TimeoutError('synthetic response lost AFTER write')
   return response.json()
  with patch.object(submit,'http_json',remote):
   with self.assertRaisesRegex(RuntimeError,"outcome_unknown"):submit.submit_gateway(self.cfg,'experience',self.payload,body['client_metadata'])
   result=submit.submit_gateway(self.cfg,'experience',self.payload,submit.metadata(self.payload,self.cfg))
  self.assertTrue(result['duplicate']);self.assertEqual(len((self.root/'mock.jsonl').read_text('utf8').splitlines()),1)
 def test_uncertain_no_visible_record_is_unknown_not_create(self):
  body=self.body();body['client_metadata']['reconcile_only']=True
  r=TestClient(gateway.app).post('/v1/contributions',json=body);self.assertEqual(r.status_code,202);self.assertEqual(r.json()['status'],'outcome_unknown');self.assertFalse((self.root/'mock.jsonl').exists())
 def test_state_change_requires_explicit_revision(self):
  before=submit.metadata(self.payload,self.cfg)
  with self.assertRaisesRegex(RuntimeError,'revision'):submit.metadata({**self.payload,'title':'changed'},self.cfg)
  self.assertEqual(submit.metadata(self.payload,self.cfg)['request_id'],before['request_id'])
 def test_feishu_success_timeout_uses_durable_search_not_retry_create(self):
  rows=[];creates=[]
  conf={'FEISHU_APP_ID':'synthetic','FEISHU_APP_SECRET':'synthetic','FEISHU_APP_TOKEN':'syn','FEISHU_EXPERIENCE_TABLE_ID':'syn-table'}
  def http(method,url,data,headers,**kwargs):
   if '/records/search?' in url:return {'code':0,'data':{'items':rows,'has_more':False}}
   creates.append(data);rows.append({'record_id':'syn-created-once','fields':data['fields']});raise TimeoutError('response lost after success')
  with patch.object(gateway,'SINK','feishu'),patch.object(gateway,'cfg',return_value=conf),patch.object(gateway,'feishu_tenant_access_token',return_value='synthetic'),patch.object(gateway,'http_json',http):
   result=TestClient(gateway.app).post('/v1/contributions',json=self.body());self.assertEqual(result.status_code,200);self.assertEqual(result.json()['record_id'],'syn-created-once');self.assertEqual(len(creates),1)
 def test_new_revision_must_resolve_parent_case(self):
  body=self.body();client=TestClient(gateway.app);one=client.post('/v1/contributions',json=body).json()
  import uuid
  two={**body,'payload':{**self.payload,'title':'Explicit revision'},'client_metadata':{**body['client_metadata'],'request_id':str(uuid.uuid4()),'parent_request_id':one['request_id'],'case_id':one['case_id'],'revision':2}}
  result=client.post('/v1/contributions',json=two);self.assertEqual(result.status_code,200,result.text);self.assertEqual(result.json()['case_id'],one['case_id'])
  two['client_metadata']['request_id']=str(uuid.uuid4());two['client_metadata']['case_id']='forged';self.assertEqual(client.post('/v1/contributions',json=two).status_code,409)
 def test_legacy_fresh_submission_uuid_is_not_a_persistent_request(self):
  body=self.body();body['client_metadata'].pop('request_id');self.assertEqual(TestClient(gateway.app).post('/v1/contributions',json=body).status_code,428)

if __name__=='__main__':unittest.main()
