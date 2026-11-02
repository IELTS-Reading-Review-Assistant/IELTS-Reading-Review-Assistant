import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'analysis' / 'error-review'))
sys.path.insert(0, str(ROOT / 'analysis' / 'recommendations'))

import mapping
import stats


def row(correct=True, cause=None):
    return {'correct': correct, 'cause': cause}


class MappingTests(unittest.TestCase):
    def test_options_are_stable_and_labelled(self):
        keys = [k for k, _ in mapping.options()]
        self.assertEqual(keys, ['vocabulary', 'sentence', 'evidence', 'qualifier'])
        self.assertTrue(all(mapping.label(k) for k in keys))

    def test_advice_for_known_and_unknown_cause(self):
        self.assertTrue(mapping.advice_for('vocabulary'))
        self.assertEqual(mapping.advice_for('unknown'), [])
        self.assertFalse(mapping.is_cause('unknown'))

    def test_advice_for_records_sorted_by_count(self):
        records = [row(False, 'evidence'), row(False, 'evidence'),
                   row(False, 'vocabulary'), row(True, None)]
        result = mapping.advice_for_records(records)
        self.assertEqual([r['cause'] for r in result], ['evidence', 'vocabulary'])
        self.assertEqual(result[0]['count'], 2)
        self.assertTrue(result[0]['advice'])


class StatsTests(unittest.TestCase):
    def test_empty_input(self):
        result = stats.summary([])
        self.assertEqual(result['total'], 0)
        self.assertEqual(result['accuracy'], 0.0)
        self.assertEqual(result['top'], [])
        self.assertEqual(result['most_frequent'], '')

    def test_counts_accuracy_and_pending(self):
        records = [row(True), row(False, 'evidence'), row(False, 'evidence'),
                   row(False, 'sentence'), row(False, None)]
        result = stats.summary(records)
        self.assertEqual(result['total'], 5)
        self.assertEqual(result['wrong'], 4)
        self.assertEqual(result['correct'], 1)
        self.assertEqual(result['accuracy'], 0.2)
        self.assertEqual(result['confirmed'], 3)
        self.assertEqual(result['pending'], 2)
        self.assertEqual(result['by_cause'][0], {'cause': 'evidence', 'label': '证据定位错', 'count': 2})
        self.assertEqual(len(result['top']), 2)
        self.assertEqual(result['most_frequent'], '证据定位错')

    def test_unknown_cause_is_not_counted(self):
        result = stats.summary([row(False, 'unknown')])
        self.assertEqual(result['confirmed'], 0)
        self.assertEqual(result['pending'], 1)


if __name__ == '__main__':
    unittest.main()
