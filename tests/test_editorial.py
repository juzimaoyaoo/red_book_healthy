import copy
import json
import tempfile
import unittest
from pathlib import Path
from health_agent.editorial import audit_text, audit_content
from health_agent.backtest import load_cases
import test_workflow as fixtures
from test_workflow import CONTENT, GO, search_response, response


class EditorialTests(unittest.TestCase):
    def test_assertive_food_medicine_blocked_but_debunk_not_blocked(self):
        self.assertIn('food_as_medicine', audit_text('天然胰岛素食物', '多吃就行')['must_rewrite'])
        self.assertNotIn('food_as_medicine', audit_text('“天然胰岛素”不靠谱',
                                                      '不能把普通食物当成药物替代品。')['must_rewrite'])

    def test_unrelated_disclaimer_does_not_cancel_promise(self):
        audit = audit_text('身体里的炎症全部消失', '仅供参考，不替代就医。')
        self.assertIn('guaranteed_outcome', audit['must_rewrite'])

    def test_source_check_does_not_mean_false(self):
        audit = audit_text('膳食数值', '普通成年人每天需要某营养素2.4μg，应核适用人群。')
        self.assertFalse(audit['medical_accuracy_verified'])
        self.assertFalse(audit['must_rewrite'])
        self.assertIn('numeric_claim', [s['code'] for s in audit['signals']])

    def test_cooking_and_reproduction_numeric_misses_covered(self):
        for body in ['30只蚊子经历两代繁殖后增加。', '鸡蛋煮10分钟是否全熟，应考虑鸡蛋大小。']:
            self.assertIn('numeric_claim', [s['code'] for s in audit_text('科普', body)['signals']])

    def test_ordinary_small_action_not_numeric_health_claim(self):
        audit = audit_text('先做一个小改变', '今晚花2分钟把手机放到够不到的地方，看看是否更方便。')
        self.assertEqual(audit['signals'], [])

    def test_quotes_and_negation_are_clause_local(self):
        self.assertFalse(audit_text('不要相信天然胰岛素', '仍然需要按医嘱管理')['must_rewrite'])
        self.assertTrue(audit_text('天然胰岛素食物', '不要熬夜，多吃就行')['must_rewrite'])

    def test_slides_and_cover_are_also_checked(self):
        c = copy.deepcopy(CONTENT)
        c['slides'][2]['text'] = '食物就是天然胰岛素'
        self.assertIn('food_as_medicine', audit_content(c)['must_rewrite'])
        c['slides'][2]['text'] = '普通文案'
        c['cover_text'] = '炎症全部消失'
        self.assertIn('guaranteed_outcome', audit_content(c)['must_rewrite'])

    def test_dataset_tampering_or_duplicate_not_counted(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            rows = [{'sample_id':'s1','author':'a','body':'健康'*50}]*50
            (p/'data.json').write_text(json.dumps(rows))
            (p/'labels.json').write_text('[]')
            with self.assertRaises(ValueError):
                load_cases(p/'data.json',p/'labels.json')



class GateTests(unittest.TestCase):
    setUp = fixtures.WorkflowTests.setUp
    tearDown = fixtures.WorkflowTests.tearDown
    flow = fixtures.WorkflowTests.flow

    def test_model_go_cannot_override_required_rewrite(self):
        c = copy.deepcopy(CONTENT)
        c['cover_text'] = '身体里的炎症全部消失'
        flow = self.flow([search_response(), response(GO)])
        flow.state.update(status='DRAFT', content=c, content_hash='before', revision=1,
                          evidence={'urls':[]})
        review = flow.review_content()
        self.assertEqual(review['verdict'], 'REVISE')
        self.assertFalse((flow.dir/'mobile-handoff.json').exists())

    def test_malformed_blocked_is_never_downgraded(self):
        flow = self.flow([search_response(), response({'verdict':'BLOCKED','issues':None})])
        flow.state.update(status='DRAFT', content=CONTENT, content_hash='before', revision=1,
                          evidence={'urls':[]})
        self.assertEqual(flow.review_content()['verdict'], 'BLOCKED')
