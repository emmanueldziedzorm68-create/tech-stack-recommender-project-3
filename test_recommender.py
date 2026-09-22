import json
import math
import threading
import tempfile
from pathlib import Path
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer
from app import Handler
from recommender import Recommender, cosine


class RecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Recommender()

    def test_cosine_known_geometry(self):
        self.assertAlmostEqual(cosine({'x': 1}, {'x': 1, 'y': 1}), 1/math.sqrt(2))
        self.assertEqual(cosine({}, {'x': 1}), 0)
        self.assertEqual(cosine({'x': 1}, {'y': 1}), 0)

    def test_exact_profile_is_first_with_unit_similarity(self):
        for role in self.engine.roles:
            match = self.engine.recommend(role['skills'])['recommendations'][0]
            self.assertEqual(match['role'], role['role'])
            self.assertAlmostEqual(match['score'], 1)

    def test_aliases_and_duplicate_validation(self):
        a = self.engine.recommend([' Python ', 'CLOUD', 'Automation'])
        b = self.engine.recommend(['python', 'cloud computing', 'automation'])
        self.assertEqual(a, b)
        with self.assertRaises(ValueError):
            self.engine.recommend(['python', 'cloud', 'cloud computing'])

    def test_unknown_profile_does_not_return_arbitrary_roles(self):
        result = self.engine.recommend(['knitting', 'pottery', 'baking'])
        self.assertEqual(result['recommendations'], [])
        self.assertEqual(len(result['unknown_skills']), 3)

    def test_partial_profile_is_disclosed(self):
        result = self.engine.recommend(['python', 'pottery', 'baking'])
        self.assertTrue(result['limited_profile'])
        self.assertTrue(all('python' in r['matched_skills'] for r in result['recommendations']))

    def test_top_three_sorted_and_repeatable(self):
        skills = ['Python', 'Cloud Computing', 'Automation']
        result = self.engine.recommend(skills)
        scores = [r['score'] for r in result['recommendations']]
        self.assertEqual(len(scores), 3)
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(result, self.engine.recommend(skills))

    def test_document_idf_formula(self):
        count = sum('python' in r['skills'] for r in self.engine.roles)
        self.assertAlmostEqual(self.engine.idf['python'], math.log(len(self.engine.roles)/count))

    def test_goals_are_explicit_and_do_not_bypass_minimum(self):
        skills = ['html', 'css', 'react']
        goal = ['javascript', 'apis']
        result = self.engine.recommend(skills, goals=goal)
        combined = self.engine.recommend(skills + goal)
        self.assertEqual([r['score'] for r in result['recommendations']], [r['score'] for r in combined['recommendations']])
        self.assertTrue(any(r['matched_goal_skills'] for r in result['recommendations']))
        with self.assertRaises(ValueError):
            self.engine.recommend(['python'], goals=['sql', 'statistics'])
        with self.assertRaises(ValueError):
            self.engine.recommend(skills, goals='cloud')

    def test_universal_skills_zero_vector(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'roles.csv'
            path.write_text('role,skills,tools,description\nRole A,python;sql;git,Python,Example\nRole B,python;sql;git,SQL,Example\n')
            result = Recommender(path).recommend(['python', 'sql', 'git'])
            self.assertEqual(result['recommendations'], [])


class BrowserAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_page_vocabulary_and_recommendations(self):
        with urlopen(self.base) as response:
            self.assertIn(b'Tech Stack Recommender', response.read())
        with urlopen(self.base+'/api/skills') as response:
            self.assertIn('python', json.load(response)['skills'])
        request = Request(self.base+'/api/recommend', data=json.dumps({'skills': ['python', 'cloud', 'automation']}).encode(), headers={'Content-Type': 'application/json'})
        with urlopen(request) as response:
            self.assertEqual(len(json.load(response)['recommendations']), 3)

    def test_invalid_input_is_user_error(self):
        for payload in [{'skills': ['python']}, {'skills': None}, [], {'skills': [1, 2, 3]}]:
            with self.assertRaises(HTTPError) as error:
                urlopen(Request(self.base+'/api/recommend', data=json.dumps(payload).encode()))
            self.assertEqual(error.exception.code, 400)
            error.exception.close()


if __name__ == '__main__':
    unittest.main()
