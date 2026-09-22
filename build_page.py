"""Refresh the standalone page after editing the dataset or browser engine."""
import json
import re
from pathlib import Path
from recommender import ALIASES, Recommender


def build():
    engine = Recommender()
    model = json.dumps({'roles': engine.roles, 'idf': engine.idf, 'aliases': ALIASES}, ensure_ascii=True).replace('<', '\\u003c')
    path = Path(__file__).with_name('index.html')
    page = path.read_text(encoding='utf-8')
    blocks = {
        'catalogue': '<script id="catalogue" type="application/json">' + model + '</script>',
        'browser-engine': '<script id="browser-engine">\n' + Path(__file__).with_name('browser_engine.js').read_text(encoding='utf-8') + '\n</script>',
    }
    for name, block in blocks.items():
        if f'<script id="{name}"' in page:
            page = re.sub(fr'<script id="{name}".*?</script>', lambda _: block, page, flags=re.S)
        else:
            page = page.replace('<script>', block + '\n<script>', 1)
    path.write_text(page, encoding='utf-8')


if __name__ == '__main__':
    build()
