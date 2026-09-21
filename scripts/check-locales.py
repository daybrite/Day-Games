#!/usr/bin/env python3
"""Check the localization contract across the app, store listings, website, and CI."""
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = set('en ar de es fr hi id it ja ko pt-BR ru zh-CN'.split())
LIMITS = {'name': 30, 'subtitle': 30, 'short': 80, 'promo': 170,
          'keywords': 100, 'description': 4000, 'release-notes': 500}
URLS = {'marketing-url', 'privacy-url', 'support-url'}


def catalog(path):
    # This app uses single-line Fluent patterns. day-build parses the full Fluent syntax.
    entries = re.findall(r'^([\w-]+) = (.*)$', path.read_text(), re.M)
    assert len(entries) == len(dict(entries)), f'{path}: duplicate message'
    return dict(entries)


def main():
    app = ROOT / 'resource/locales'
    assert {p.name for p in app.iterdir() if p.is_dir()} == EXPECTED
    assert {p.name for p in (ROOT / 'store').iterdir() if p.is_dir()} == EXPECTED
    site = tomllib.loads((ROOT / 'website/site.toml').read_text())
    assert set(site['locales']) == EXPECTED
    workflow = (ROOT / '.github/workflows/ci.yml').read_text()
    matrix = re.search(r'^      locales: (.+)$', workflow, re.M)
    assert matrix and set(matrix[1].replace(',', ' ').split()) == EXPECTED
    crates = [ROOT, ROOT / 'gamekit', *sorted((ROOT / 'games').iterdir())]
    crates = [p for p in crates if (p / 'Cargo.toml').exists()]
    total = 0
    for crate in crates:
        directory = crate / 'resource/locales'
        assert {p.name for p in directory.iterdir() if p.is_dir()} == EXPECTED, f'{crate}: missing locale'
        files = {p.name for p in (directory / 'en').glob('*.ftl')}
        for locale in EXPECTED:
            assert {p.name for p in (directory / locale).glob('*.ftl')} == files, f'{crate}/{locale}: missing file'
        for filename in files:
            english = catalog(directory / 'en' / filename)
            total += len(english)
            for locale in EXPECTED:
                translated = catalog(directory / locale / filename)
                assert translated.keys() == english.keys(), f'{crate}/{locale}/{filename}: missing/extra messages'
                for key, value in translated.items():
                    assert value.strip(), f'{crate}/{locale}/{key}: empty message'
                    assert set(re.findall(r'\$\w+', value)) == set(re.findall(r'\$\w+', english[key])), f'{crate}/{locale}/{key}: wrong arguments'
        for source in (crate / 'src').rglob('*.rs'):
            assert not re.search(r'\btr\s*\(', source.read_text()), f'{source}: use generated accessors'
    english = catalog(app / 'en/app.ftl')
    for locale in sorted(EXPECTED):
        translated = catalog(app / locale / 'app.ftl')
        assert translated.keys() == english.keys(), f'{locale}: missing/extra messages'
        for key, value in translated.items():
            assert value.strip(), f'{locale}/{key}: empty message'
            assert set(re.findall(r'\$\w+', value)) == set(re.findall(r'\$\w+', english[key])), f'{locale}/{key}: wrong arguments'
        sudoku = catalog(ROOT / 'games/sudoku/resource/locales' / locale / 'app.ftl')
        for label, help_key in [('checkpoint', 'help_checkpoint_1'),
                                ('commit', 'help_checkpoint_2'),
                                ('revert', 'help_checkpoint_2')]:
            assert f'**{sudoku[label]}**' in sudoku[help_key], f'{locale}/{help_key}: button name differs'
        assert translated['app_title'] == '{ $title }', f'{locale}: app title must use metadata'
        listing = ROOT / 'store' / locale
        assert {p.stem for p in listing.glob('*.txt')} == set(LIMITS) | URLS
        for field, limit in LIMITS.items():
            text = (listing / f'{field}.txt').read_text().strip()
            assert 0 < len(text) <= limit, f'{locale}/{field}: {len(text)} characters (limit {limit})'
        for field in URLS:
            assert (listing / f'{field}.txt').read_text().strip().startswith('https://'), f'{locale}/{field}: URL missing'
        for deck in ['animals', 'food']:
            path = ROOT / 'games/charades/words' / locale / f'{deck}.txt'
            text = path.read_text()
            assert '# title: ' in text and '# blurb: ' in text, f'{path}: missing title/blurb'
            words = [w for w in text.splitlines() if w and not w.startswith('#')]
            assert len(words) >= 100 and len({w.casefold() for w in words}) == len(words), f'{path}: too few or duplicate prompts'
    # Every curated screenshot has a localized title and caption, including Reversi/Pipes.
    script = (ROOT / 'dayscript/games.yaml').read_text()
    maps = re.findall(r'^      (?:title|caption):\n((?:        .+\n)+)', script, re.M)
    assert len(maps) == 24, 'Expected titles and captions for 12 curated screenshots'
    for mapping in maps:
        assert set(re.findall(r'^        ([\w-]+):', mapping, re.M)) == EXPECTED, 'Incomplete screenshot metadata'
    print(f'{len(EXPECTED)} locales: {total} messages across {len(crates)} crate catalogs, store limits, decks, gallery, website and CI agree')


if __name__ == '__main__':
    main()
