import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'analysis' / 'error-review'))
sys.path.insert(0, str(ROOT / 'analysis' / 'recommendations'))

import service
import storage


class ErrorReviewFlowTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._old = storage.DATA
        storage.DATA = Path(self._tmp.name)

    def tearDown(self):
        storage.DATA = self._old
        self._tmp.cleanup()

    def test_save_marks_answer_correctly(self):
        right = service.save(question='The capital is ...', learner='Paris', accepted=['Paris'])
        wrong = service.save(question='The number is ...', learner='12', accepted=['13'])
        self.assertTrue(storage.get(right)['correct'])
        self.assertFalse(storage.get(wrong)['correct'])

    def test_validation_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            service.save(question='  ', learner='A', accepted=['A'])
        with self.assertRaises(ValueError):
            service.save(question='Q', learner='A', accepted=[])
        with self.assertRaises(ValueError):
            service.save(question='Q', learner='A', accepted=['A'], cause='guess')
        with self.assertRaises(ValueError):
            service.save(question='Q' * 2001, learner='A', accepted=['A'])

    def test_new_record_is_pending_until_confirmed(self):
        mistake_id = service.save(question='Q', learner='B', accepted=['A'])
        self.assertEqual([r['id'] for r in service.pending()], [mistake_id])
        service.confirm(mistake_id, 'evidence')
        self.assertEqual(service.pending(), [])
        self.assertEqual(storage.get(mistake_id)['cause'], 'evidence')

    def test_confirm_many_and_reset(self):
        ids = [service.save(question='Q%d' % i, learner='B', accepted=['A']) for i in range(3)]
        self.assertEqual(service.confirm_many(ids[:2], 'sentence'), 2)
        self.assertEqual(len(service.pending()), 1)
        storage.reset(ids[0])
        self.assertEqual(len(service.pending()), 2)
        with self.assertRaises(ValueError):
            service.confirm(ids[2], 'nonsense')

    def test_detail_returns_hint_and_advice(self):
        mistake_id = service.save(question='Q', learner='B', accepted=['A'], cause='vocabulary')
        detail = service.detail(mistake_id)
        self.assertIn('不一致', detail['hint'])
        self.assertTrue(detail['advice'])
        with self.assertRaises(ValueError):
            service.detail(9999)

    def test_summary_after_confirmation(self):
        a = service.save(question='Q1', learner='B', accepted=['A'])
        b = service.save(question='Q2', learner='C', accepted=['A'])
        c = service.save(question='Q3', learner='A', accepted=['A'])
        service.confirm_many([a, b], 'evidence')
        result = service.summary()
        self.assertEqual(result['total'], 3)
        self.assertEqual(result['wrong'], 2)
        self.assertEqual(result['pending'], 1)
        self.assertEqual(result['most_frequent'], '证据定位错')
        self.assertTrue(c)

    def test_delete_removes_record(self):
        mistake_id = service.save(question='Q', learner='B', accepted=['A'])
        storage.delete(mistake_id)
        self.assertIsNone(storage.get(mistake_id))


if __name__ == '__main__':
    unittest.main()
