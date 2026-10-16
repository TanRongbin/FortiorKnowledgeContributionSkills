import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/fortior-knowledge-contributor/scripts'
sys.path.insert(0, str(SCRIPTS))
from validate_capture_extension import validate_extension
from submit import common_feishu_fields


def fixture():
    return {'knowledge_extension':{'schema_version':'fortior.capture-enrichment.v1','relation_intent':'supporting_evidence','independence':'same_case_followup','mechanism':'Synthetic mechanism, not an actual case','contribution_delta':'Additional synthetic observation','related_ids':[], 'evidence_facts':[{'id':'E1','statement':'Synthetic observed result','confidence':'strong_hypothesis','source_ref':{'locator':'redacted test summary','revision':'unknown'}}], 'boundary_conditions':[{'condition':'Synthetic condition','evidence_ids':['E1']}], 'counterexamples':[{'question':'Alternative mechanism?','result':'unknown','evidence_ids':[]}], 'verification':{'status':'not_run','expected_behavior':'synthetic expectation','observed_behavior':'','evidence_ids':[]}}}

class ExtensionTests(unittest.TestCase):
    def test_old_payload_unchanged(self): validate_extension({})
    def test_valid_extension(self): validate_extension(fixture())
    def test_no_mutation(self):
        p=fixture(); old=copy.deepcopy(p); validate_extension(p); self.assertEqual(p,old)
    def test_no_unfounded_pass(self):
        p=fixture(); p['knowledge_extension']['verification']['status']='passed'
        with self.assertRaises(ValueError): validate_extension(p)
    def test_no_unfounded_exclusion(self):
        p=fixture(); p['knowledge_extension']['counterexamples'][0]['result']='excluded'
        with self.assertRaises(ValueError): validate_extension(p)
    def test_source_objects_not_strings(self):
        p=fixture(); p['knowledge_extension']['evidence_facts'][0]['source_ref']='[object Object]'
        with self.assertRaises(ValueError): validate_extension(p)
    def test_unknown_evidence_rejected(self):
        p=fixture(); p['knowledge_extension']['boundary_conditions'][0]['evidence_ids']=['missing']
        with self.assertRaises(ValueError): validate_extension(p)
    def test_raw_json_roundtrip_preserves_extension(self):
        p=fixture(); p.update(contributor={'username':'synthetic'},submission_preferences={'visibility':'private_governance_only','attribution':'anonymous','allow_repository_name':False,'allow_commit_id':False,'allow_file_paths':False,'allow_code_excerpt':False,'rights_confirmed':True})
        fields=common_feishu_fields(p,{})
        self.assertEqual(json.loads(fields['原始JSON'])['knowledge_extension'],p['knowledge_extension'])
        self.assertEqual(fields['公开范围'],'仅治理人员可见')
    def test_duplicate_evidence_rejected(self):
        p=fixture(); p['knowledge_extension']['evidence_facts']*=2
        with self.assertRaises(ValueError): validate_extension(p)

if __name__=='__main__': unittest.main()
