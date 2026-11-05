import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from health_agent.production import ProductionAgent, normalize_review, DIMENSIONS
from health_agent.model_adapter import CodexModel


class DummyModel:
    usage=[]
    def complete(self,*args,**kwargs):
        raise AssertionError('Unexpected model call')


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.memory_patch=patch('health_agent.production.load_reference_memory',return_value=([],None))
        self.memory_patch.start()
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.packet=self.root/'packet.json'
        self.packet.write_text(json.dumps({'sources':[{'id':'ref','kind':'reference','title':'test','text':'reference phrase'},
                                                      {'id':'fact','kind':'official_fact','title':'fact','text':'actual guideline evidence'}]}))
        self.agent=ProductionAgent(self.root/'run',self.packet,{'request':'test'},DummyModel())
    def tearDown(self):
        self.memory_patch.stop();self.tmp.cleanup()
    def test_unread_quote_cannot_pass(self):
        with self.assertRaises(ValueError):self.agent.citations([{'source_id':'fact','quote':'actual guideline'}],official=True)
    def test_quote_must_exist_and_reference_cannot_prove_health(self):
        self.agent.read_sources({'ids':['ref','fact']})
        self.agent.citations([{'source_id':'fact','quote':'actual guideline'}],official=True)
        for c in [{'source_id':'ref','quote':'reference phrase'},{'source_id':'fact','quote':'imaginary result'}]:
            with self.assertRaises(ValueError):self.agent.citations([c],official=True)
    def test_no_content_before_approved_opening(self):
        with self.assertRaises(ValueError):self.agent.submit_content({'post_id':'x'})
    def test_resume_rejects_replaced_source(self):
        p=json.loads(self.packet.read_text());p['sources'][0]['text']='replaced';self.packet.write_text(json.dumps(p))
        with self.assertRaises(ValueError):ProductionAgent(self.root/'run',self.packet,{'request':'test'},DummyModel(),resume=True)
    def test_resume_rejects_changed_human_task(self):
        with self.assertRaises(ValueError):ProductionAgent(self.root/'run',self.packet,{'request':'different'},DummyModel(),resume=True)
    def test_top_go_does_not_override_bad_dimension(self):
        r={'verdict':'GO','checks':[{'dimension':'reader_value','verdict':'REVISE','location':'body','quote':'hello','reason':'weak'}],'issues':[]}
        self.assertEqual(normalize_review(r,['reader_value'],{'body':'hello'})['verdict'],'REVISE')
    def test_missing_review_or_fake_quote_is_rejected(self):
        for checks in [[],[{'dimension':'reader_value','verdict':'PASS','location':'body','quote':'not present','reason':'ok'}]]:
            r={'verdict':'GO','checks':checks,'issues':[]}
            self.assertEqual(normalize_review(r,['reader_value'],{'body':'hello'})['verdict'],'REVISE')
    def test_blind_public_map_excludes_author_pitch(self):
        from health_agent.production import public_map
        r=public_map({'title':'hi','body':'body','purpose':'valuable','reference_application':['pitch'],
                      'image_plan':[{'number':1,'headline':'head','copy':'copy','source_notes':'source','purpose':'author defense'}]},'blind_reader')
        self.assertNotIn('author defense',json.dumps(r));self.assertNotIn('valuable',json.dumps(r))
    def test_exact_model_medium_tool_isolation(self):
        m=CodexModel(self.root/'model');args=m.command(self.root)
        self.assertEqual(args[args.index('--model')+1],'gpt-6.1-sol')
        self.assertIn('model_reasoning_effort="medium"',args)
        self.assertIn('web_search="disabled"',args)
        self.assertIn('features.shell_tool=false',args)
        self.assertIn('read-only',args)
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox',args)
    def test_resume_preserves_call_numbers(self):
        d=self.root/'model';d.mkdir();(d/'003-actor-input.json').write_text('{}')
        m=CodexModel(d)
        self.assertEqual(m.calls,3)

    def test_public_prefix_alias_still_requires_exact_quote(self):
        r={'verdict':'GO','checks':[{'dimension':'reader_value','verdict':'PASS','location':'public.body','quote':'hello','reason':'ok'}],'issues':[]}
        self.assertEqual(normalize_review(r,['reader_value'],{'body':'hello'})['verdict'],'GO')
        r['checks'][0]['quote']='invented'
        self.assertEqual(normalize_review(r,['reader_value'],{'body':'hello'})['verdict'],'REVISE')
    def test_blind_reader_has_no_hidden_evidence_job(self):
        seen={}
        class Capture:
            usage=[]
            def complete(self,role,system,payload,schema,images):
                seen.update(system=system,payload=payload,schema=schema)
                return {'verdict':'GO','checks':[{'dimension':d,'verdict':'PASS','location':'body','quote':'hello','reason':'ok'} for d in DIMENSIONS['blind_reader']], 'issues':[], 'keep_strengths':[]}
        self.agent.model=Capture()
        r=self.agent.review('blind_reader',{'title':'test','body':'hello'})
        self.assertEqual(r['verdict'],'GO')
        self.assertNotIn('sources',seen['payload'])
        self.assertIn('不得因没有隐藏原文',seen['system'])
        dimensions=seen['schema']['properties']['checks']['items']['properties']['dimension']['enum']
        self.assertNotIn('authoritative_evidence',dimensions)
    def test_resume_rejects_changed_protocol_code_identity(self):
        state=json.loads((self.root/'run/state.json').read_text());state['protocol_hash']='obsolete'
        (self.root/'run/state.json').write_text(json.dumps(state))
        with self.assertRaises(ValueError):ProductionAgent(self.root/'run',self.packet,{'request':'test'},DummyModel(),resume=True)
    def test_topic_id_cannot_escape_run_directory(self):
        with self.assertRaises(ValueError):self.agent.propose_topics({'topics':[{'id':'../../escape'},{'id':'p02'}]})

    def test_existing_run_cannot_be_silently_reset(self):
        before=(self.root/'run/state.json').read_bytes()
        with self.assertRaises(ValueError):ProductionAgent(self.root/'run',self.packet,{'request':'test'},DummyModel())
        self.assertEqual(before,(self.root/'run/state.json').read_bytes())
