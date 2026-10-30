"""Prepare the shared questionnaire and build the browser-only GitHub Pages edition."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from scoring import QUESTIONS, ABILITY_OPTIONS

(ROOT / 'frontend/src/pages-questions.json').write_text(json.dumps([
    {**question, 'options': ABILITY_OPTIONS if question['type'] == 'ability' else ['Yes', 'No']}
    for question in QUESTIONS
], indent=2) + '\n')
node = os.environ.get('NODE_BINARY', 'node')
base = os.environ.get('PAGES_BASE', '/act-longevity-ai-mvp/')
subprocess.run([node, str(ROOT / 'node_modules/vite/bin/vite.js'), 'build', '--base', base],
               cwd=ROOT, env={**os.environ, 'VITE_GITHUB_PAGES': 'true'}, check=True)
(ROOT / 'dist/.nojekyll').touch()
