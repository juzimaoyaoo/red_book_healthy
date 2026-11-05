import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from health_agent.core import (APIError, OpenAIClient, Workflow, cited_urls, digest,
                               run_agent, validate_content, validate_review)

URL = 'https://www.who.int/example-test-fixture'
CONTENT = {'title': '测试标题', 'cover_text': '测试封面', 'body': '仅用于离线测试。' * 50,
           'audience': '普通成年人', 'limitations': '测试数据不能发布', 'tags': ['测试'],
           'slides': [{'heading': str(i), 'text': '测试画面'} for i in range(4)],
           'claims': [{'id': 'c1', 'statement': '测试论断', 'source_urls': [URL]}]}
TOPICS = {'topics': [{'id': 't1', 'title': '测试选题', 'pillar': '运动', 'reader_problem': '测试',
                      'angle': '测试', 'reason': '待验证', 'source_urls': [URL]}]}
GO = {'verdict': 'GO', 'issues': [], 'claim_checks': [
    {'id': 'c1', 'supported': True, 'source_urls': [URL], 'reason': '测试对应关系'}]}


def response(value):
    return {'status': 'completed', 'output': [{'type': 'message', 'content': [
        {'type': 'output_text', 'text': json.dumps(value, ensure_ascii=False)}]}]}


def search_response():
    return {'status': 'completed', 'output': [{'type': 'web_search_call', 'status': 'completed', 'action': {'type': 'open_page', 'url': URL}},
        {'type': 'message', 'content': [{'type': 'output_text', 'text': '虚构测试证据，不是健康建议',
          'annotations': [{'type': 'url_citation', 'url': URL}]}]}]}


def call(name, args=None):
    return {'status': 'completed', 'output': [{'type': 'function_call', 'name': name,
            'call_id': 'test-' + name, 'arguments': json.dumps(args or {})}]}


class FakeClient:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.usage = []
        self.requests = []

    def request(self, **kwargs):
        self.requests.append(copy.deepcopy(kwargs))
        if not self.outputs:
            raise AssertionError('unexpected API request')
        return copy.deepcopy(self.outputs.pop(0))


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'config').mkdir()
        (self.root / 'config/account.json').write_text(json.dumps({'xiaohongshu_id': '2689093300',
                                                                 'phone_masked': '134****2834'}))

    def tearDown(self):
        self.tmp.cleanup()

    def flow(self, outputs=()):
        return Workflow(FakeClient(outputs), self.root)

    def test_full_react_flow_exports_unpublished_handoff(self):
        flow = self.flow([call('plan_topics', {'brief': '测试'}), search_response(), response(TOPICS),
                          call('create_content', {'topic_id': 't1'}), response(CONTENT),
                          call('review_content'), search_response(), response(GO)])
        result = run_agent(flow, '仅离线测试')
        self.assertEqual(result['status'], 'READY_FOR_ASSETS')
        handoff = json.loads((flow.dir / 'mobile-handoff.json').read_text())
        self.assertFalse(handoff['published'])
        self.assertEqual(handoff['account_id'], '2689093300')
        self.assertTrue((flow.dir / 'content.md').exists())

    def test_revise_then_go_audits_new_version(self):
        revise = dict(GO, verdict='REVISE', issues=['调整表达'])
        flow = self.flow([search_response(), response(TOPICS), response(CONTENT), search_response(),
                          response(revise), response(dict(CONTENT, title='修订标题')),
                          search_response(), response(GO)])
        flow.plan_topics('测试')
        flow.create_content('t1')
        old_hash = flow.state['content_hash']
        flow.review_content()
        self.assertFalse((flow.dir / 'mobile-handoff.json').exists())
        flow.create_content('t1')
        self.assertNotEqual(old_hash, flow.state['content_hash'])
        self.assertNotIn('review', flow.state)
        flow.review_content()
        self.assertEqual(flow.state['revision'], 2)

    def test_research_without_actual_search_fails(self):
        flow = self.flow([response({'text': '假装有证据'})])
        with self.assertRaises(ValueError):
            flow.plan_topics('测试')
        self.assertEqual(flow.state['status'], 'NEW')

    def test_search_snippet_without_open_page_is_insufficient(self):
        r = search_response()
        r['output'][0]['action'] = {'type': 'search'}
        flow = self.flow([r])
        with self.assertRaises(ValueError):
            flow.plan_topics('测试')

    def test_untrusted_host_cannot_impersonate_who(self):
        r = search_response()
        r['output'][1]['content'][0]['annotations'][0]['url'] = 'https://who.int.evil.example/a'
        self.assertEqual(cited_urls(r), [])

    def test_missing_or_invented_source_rejected(self):
        self.assertTrue(validate_content(CONTENT, []))
        c = copy.deepcopy(CONTENT)
        c['claims'] = []
        self.assertTrue(validate_content(c, [URL]))

    def test_review_cannot_skip_claims_or_fake_support(self):
        for review in (dict(GO, claim_checks=[]), dict(GO, issues=['仍有错误']),
                       dict(GO, claim_checks=[dict(GO['claim_checks'][0], supported=False)]),
                       dict(GO, claim_checks=[dict(GO['claim_checks'][0], source_urls=['https://fake.example'])])):
            self.assertTrue(validate_review(review, CONTENT, [URL]))

    def test_audit_missing_claim_downgrades_go(self):
        flow = self.flow([search_response(), response(dict(GO, claim_checks=[]))])
        flow.state.update(status='DRAFT', content=CONTENT, content_hash=digest(CONTENT), revision=1,
                          evidence={'urls': [URL]})
        flow.review_content()
        self.assertEqual(flow.state['status'], 'REVISE')
        self.assertFalse((flow.dir / 'mobile-handoff.json').exists())

    def test_blocked_has_no_handoff(self):
        flow = self.flow([search_response(), response(dict(GO, verdict='BLOCKED', issues=['危险建议']))])
        flow.state.update(status='DRAFT', content=CONTENT, content_hash=digest(CONTENT), revision=1,
                          evidence={'urls': [URL]})
        flow.review_content()
        self.assertEqual(flow.state['status'], 'BLOCKED')
        self.assertFalse((flow.dir / 'mobile-handoff.json').exists())
        with self.assertRaises(ValueError):
            flow.create_content('t1')

    def test_changed_content_invalidates_review(self):
        flow = self.flow()
        flow.state.update(status='READY_FOR_ASSETS', content=dict(CONTENT, title='偷偷改稿'),
                          review={'content_hash': digest(CONTENT)})
        with self.assertRaises(ValueError):
            flow.export_handoff()

    def test_cannot_write_before_topics_or_repeat_review(self):
        flow = self.flow()
        with self.assertRaises(ValueError):
            flow.create_content('t1')
        with self.assertRaises(ValueError):
            flow.review_content()

    def test_premature_model_finish_is_failure(self):
        flow = self.flow([response({'message': '已经完成'})])
        with self.assertRaises(ValueError):
            run_agent(flow, '测试')

    def test_missing_key_and_call_budget_fail_closed(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
            with self.assertRaises(APIError):
                OpenAIClient()
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'not-a-real-key'}):
            client = OpenAIClient(max_calls=0)
            with self.assertRaises(APIError):
                client.request(input='test')

    def test_api_payload_preserves_exact_model_and_medium(self):
        from io import BytesIO
        class Context(BytesIO):
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.close()
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'not-a-real-key'}), patch(
                'health_agent.core.urlopen', return_value=Context(json.dumps(response({})).encode())) as fetch:
            client = OpenAIClient()
            client.request(input='test')
            payload = json.loads(fetch.call_args.args[0].data)
            self.assertEqual(payload['model'], 'gpt-6.1-sol')
            self.assertEqual(payload['reasoning']['effort'], 'medium')
            self.assertFalse(payload['store'])
            self.assertIn('reasoning.encrypted_content', payload['include'])


if __name__ == '__main__':
    unittest.main()
