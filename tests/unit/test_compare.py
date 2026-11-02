import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'analysis' / 'error-review'))

import compare


class CompareTests(unittest.TestCase):
    def test_normalize_ignores_case_space_and_punctuation(self):
        self.assertEqual(compare.normalize('  TRUE. '), 'true')
        self.assertEqual(compare.normalize('Not\t given'), 'not given')
        self.assertEqual(compare.normalize('“答案”'), '答案')

    def test_text_answer_accepts_any_listed_variant(self):
        accepted = ['Not Given', 'NG']
        self.assertTrue(compare.is_correct('not  given.', accepted))
        self.assertTrue(compare.is_correct('ng', accepted))
        self.assertFalse(compare.is_correct('False', accepted))

    def test_blank_answer_is_never_correct(self):
        self.assertFalse(compare.is_correct('', ['A']))
        self.assertFalse(compare.is_correct('   ', ['A']))

    def test_empty_accepted_list_is_never_correct(self):
        self.assertFalse(compare.is_correct('A', []))

    def test_multiple_choice_compares_letter_sets(self):
        self.assertTrue(compare.is_correct('A,C', ['AC'], multiple=True))
        self.assertTrue(compare.is_correct('ca', ['AC'], multiple=True))
        self.assertFalse(compare.is_correct('A', ['AC'], multiple=True))
        self.assertFalse(compare.is_correct('A,B,D', ['AC'], multiple=True))

    def test_multiple_choice_accepts_any_key(self):
        self.assertTrue(compare.is_correct('B', ['B', 'b'], multiple=True))

    def test_diff_hint_explains_mismatch(self):
        self.assertIn('没有填写', compare.diff_hint('', ['A']))
        self.assertIn('一致', compare.diff_hint('a', ['A']))
        self.assertIn('不一致', compare.diff_hint('B', ['A']))


if __name__ == '__main__':
    unittest.main()
