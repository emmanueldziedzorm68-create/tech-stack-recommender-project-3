"""Reproducible Python tests and exhaustive three-skill browser parity checks."""
import itertools
import json
from pathlib import Path
import subprocess
import sys
from recommender import Recommender

root = Path(__file__).resolve().parent
subprocess.run([sys.executable, '-m', 'unittest', '-v'], cwd=root, check=True)
engine = Recommender()
profiles = [role['skills'] for role in engine.roles]
profiles += [list(x) for x in itertools.combinations(sorted(engine.idf), 3)]
profiles += [['HTML', 'CSS', 'React'], [' Python ', 'CLOUD', 'Automation'],
             ['python', 'pottery', 'baking'], ['knitting', 'pottery', 'baking']]
samples = [{'skills': skills, 'expected': engine.recommend(skills)} for skills in profiles]
for goals in [['cloud', 'python'], ['pottery'], ['HTML', 'CSS']]:
    skills = ['html', 'css', 'react']
    samples.append({'skills': skills, 'goals': goals, 'expected': engine.recommend(skills, goals=goals)})
subprocess.run(['node', 'test_browser.js'], input=json.dumps(samples), text=True, cwd=root, check=True)
