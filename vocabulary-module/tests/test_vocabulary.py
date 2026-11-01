import tempfile
import unittest
from pathlib import Path
import storage
from vocabulary import recommend


class VocabularyTests(unittest.TestCase):
    def test_case_counts_and_original_sentences(self):
        result = recommend('Research supports biodiversity. RESEARCH protects biodiversity.')
        self.assertEqual(result[0]['word'], 'research')
        self.assertEqual(result[0]['count'], 2)
        self.assertEqual(len(result[0]['sentences']), 2)
        self.assertIn('RESEARCH', result[0]['sentences'][1]['text'])

    def test_filters_and_limit(self):
        self.assertEqual(recommend('The research is research.', ['research']), [])
        words = ['candidate' + chr(97 + i) for i in range(26)]
        self.assertEqual(len(recommend(' '.join(words))), 20)
        self.assertEqual(len(recommend('biodiversity')), 1)

    def test_validation(self):
        for text in ['', '   ', '1234 中文', 'x ' * 5001, 'a' * 50001]:
            with self.assertRaises(ValueError):
                recommend(text)

    def test_apostrophes_hyphens_no_lemmatisation(self):
        words = {r['word'] for r in recommend("researcher's low-quality studies study")}
        self.assertIn("researcher's", words)
        self.assertIn('quality', words)
        self.assertIn('studies', words)

    def test_persistence_preserves_edits_and_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = storage.DATA
            storage.DATA = Path(tmp)
            try:
                item = recommend('Biodiversity supports ecosystems.')[0]
                storage.save_word(item, 'original', 'passage one')
                storage.update_word(item['word'], 'personal', True)
                storage.save_word(item, 'overwrite attempt', 'passage two')
                record = storage.wordbook()[0]
                self.assertEqual(record['meaning'], 'personal')
                self.assertEqual(record['mastered'], 1)
                self.assertEqual(len(storage.wordbook()), 1)
                self.assertEqual(len(storage.sources(item['word'])), 2)
                storage.update_word(item['word'], 'personal', False)
                self.assertEqual(storage.wordbook()[0]['mastered'], 0)
                storage.save_passage('A saved passage.')
                self.assertEqual(storage.passages(), ['A saved passage.'])
            finally:
                storage.DATA = old

    @unittest.skipUnless((Path(__file__).parents[1] / 'data' / 'dictionary.db').exists(),
                         'Run setup.ps1 to install the ECDICT database.')
    def test_real_dictionary(self):
        self.assertNotEqual(storage.lookup('research'), '暂无释义')
        self.assertEqual(storage.lookup('zzzzunlistedtestword'), '暂无释义')


if __name__ == '__main__':
    unittest.main()
