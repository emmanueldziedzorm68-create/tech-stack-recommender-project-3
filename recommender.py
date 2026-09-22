"""Dependency-free, skill-level TF-IDF and cosine similarity recommender."""
import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

DATASET = Path(__file__).with_name('raw_skills.csv')
ALIASES = {
    'cloud': 'cloud computing', 'ml': 'machine learning',
    'ai/ml': 'machine learning', 'js': 'javascript', 'ts': 'typescript',
    'react.js': 'react', 'reactjs': 'react', 'postgresql': 'sql',
    'structured query language': 'sql', 'continuous integration': 'ci/cd',
    'rest api': 'apis', 'rest apis': 'apis', 'api': 'apis',
    'data visualisation': 'data visualization', 'ux': 'ux research',
    'ui': 'ui design', 'test automation': 'testing',
}


def normalize(skill):
    name = ' '.join(skill.strip().lower().split())
    return ALIASES.get(name, name)


def cosine(a, b):
    denominator = math.sqrt(sum(v*v for v in a.values())) * math.sqrt(sum(v*v for v in b.values()))
    return sum(v * b.get(k, 0) for k, v in a.items()) / denominator if denominator else 0.0


class Recommender:
    def __init__(self, path=DATASET):
        with open(path, encoding='utf-8-sig', newline='') as source:
            reader = csv.DictReader(source)
            required = {'role', 'skills', 'tools', 'description'}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError('Dataset must contain role, skills, tools and description columns.')
            self.roles = []
            for row in reader:
                skills = sorted({normalize(s) for s in row['skills'].split(';') if s.strip()})
                if not row['role'].strip() or not skills:
                    raise ValueError('Each role needs a name and at least one skill.')
                self.roles.append({**row, 'skills': skills, 'tools': row['tools'].split(';')})
        if not self.roles:
            raise ValueError('Dataset is empty.')
        if len({r['role'] for r in self.roles}) != len(self.roles):
            raise ValueError('Role names must be unique.')
        frequencies = Counter(s for role in self.roles for s in role['skills'])
        self.idf = {s: math.log(len(self.roles) / count) for s, count in frequencies.items()}
        self.vectors = [self.vector(role['skills']) for role in self.roles]

    def vector(self, skills):
        counts = Counter(s for s in skills if s in self.idf)
        total = sum(counts.values())
        return {s: count / total * self.idf[s] for s, count in counts.items()} if total else {}

    def recommend(self, skills, limit=3, goals=None):
        if not isinstance(skills, list) or any(not isinstance(s, str) for s in skills):
            raise ValueError('Provide skills as a list of text values.')
        normalized = sorted({normalize(s) for s in skills if s.strip()})
        if len(normalized) < 3:
            raise ValueError('Enter at least three different skills. Aliases count as the same skill.')
        if not isinstance(limit, int) or limit < 1:
            raise ValueError('The result limit must be a positive integer.')
        goals = [] if goals is None else goals
        if not isinstance(goals, list) or any(not isinstance(s, str) for s in goals):
            raise ValueError('Provide career-goal skills as a list of text values.')
        goal_skills = sorted({normalize(s) for s in goals if s.strip()})
        recognized = [s for s in normalized if s in self.idf]
        unknown = [s for s in normalized if s not in self.idf]
        recognized_goals = [s for s in goal_skills if s in self.idf]
        profile_skills = sorted(set(recognized + recognized_goals))
        profile = self.vector(profile_skills)
        ranked = []
        for role, vector in zip(self.roles, self.vectors):
            score = cosine(profile, vector)
            if score > 0:
                ranked.append({**role, 'score': score,
                               'matched_skills': sorted(set(recognized) & set(role['skills'])),
                               'matched_goal_skills': sorted(set(recognized_goals) & set(role['skills'])),
                               'skills_to_explore': sorted(set(role['skills']) - set(recognized))})
        ranked.sort(key=lambda r: (-r['score'], r['role']))
        return {'input_skills': normalized, 'recognized_skills': recognized,
                'goal_skills': goal_skills,
                'unknown_goal_skills': [s for s in goal_skills if s not in self.idf],
                'unknown_skills': unknown, 'recommendations': ranked[:limit],
                'limited_profile': len(recognized) < 3}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills', help='Comma-separated skills; otherwise prompted interactively.')
    parser.add_argument('--json', action='store_true', help='Print machine-readable results.')
    parser.add_argument('--goals', default='', help='Optional comma-separated skills you want to develop.')
    args = parser.parse_args()
    try:
        entered = args.skills if args.skills is not None else input('Enter at least 3 skills, separated by commas: ')
        result = Recommender().recommend(entered.split(','), goals=args.goals.split(','))
    except (ValueError, OSError, EOFError) as error:
        parser.exit(2, f'Error: {error}\n')
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print('\nTech Stack Recommender | Educational sample dataset')
    if result['unknown_skills']:
        print('Skills outside vocabulary:', ', '.join(result['unknown_skills']))
    if result['unknown_goal_skills']:
        print('Goal skills outside vocabulary:', ', '.join(result['unknown_goal_skills']))
    if result['limited_profile']:
        print('Limited profile: fewer than three recognized skills. Add known skills for a fuller comparison.')
    for index, role in enumerate(result['recommendations'], 1):
        print(f"\n{index}. {role['role']} | Similarity: {role['score']:.3f}")
        print('   Matched:', ', '.join(role['matched_skills']))
        if role['matched_goal_skills']:
            print('   Matches your goals:', ', '.join(role['matched_goal_skills']))
        print('   Tools:', ', '.join(role['tools']))
        print('   Explore:', ', '.join(role['skills_to_explore']) or 'All listed skills matched')
    if not result['recommendations']:
        print('No matching roles. Try skills from the dataset, such as python, sql, and statistics.')
    print('\nSimilarity measures overlap, not job readiness or hiring probability.')


if __name__ == '__main__':
    main()
