# Localization

Day Games supports the same 13 languages as the Swift Faire-Games app: English, Arabic,
German, Spanish, French, Hindi, Indonesian, Italian, Japanese, Korean, Brazilian Portuguese,
Russian and Simplified Chinese. The canonical project tags are `en ar de es fr hi id it ja ko
pt-BR ru zh-CN`. Day's store staging maps these to each store's tags, including Apple's
`zh-Hans`. At runtime the Chinese catalog is also registered as `zh` so Apple/browser
`zh-Hans` and `zh-Hans-CN` preferences work without duplicated translation files.

Each Fluent catalog contains the same messages and arguments, including game rules,
accessibility labels, the Charades preview and the motion-permission explanation. Suitable
short translations were adapted from the corresponding Faire-Games `Localizable.xcstrings`
catalogs; new game text and instructions were translated for this app. The product name stays
metadata-driven (`app_title = { $title }`); “Day Games” in store names is the product brand.

Translations are owned by the crate that uses them: the app root keeps identity and
permission reasons, each `games/<game>/resource/locales/<locale>/app.ftl` owns that game's
strings, and `gamekit/resource/locales/` owns shared labels. `gamekit` also demonstrates
per-source-file catalogs: `chrome.ftl` owns the shell controls and imports its crate-wide
`app.ftl`. All 352 messages remain translated into all 13 languages.

Each reusable crate calls `day_build::generate_locales()` in `build.rs` and
`day_fluent::locales!()` in `lib.rs`. Use generated functions, for example
`blockblast::res::str::game_title()`, `crate::res::str::level_clear(n)`,
`gamekit::res::str::score()` or `gamekit::res::chrome::str::done()`.
Do not use `tr("key")`, even for dynamic choices: select an accessor or `LocalizedText`
value instead. Keys are private, so every game can use `game_title` without a global prefix.
The root app retains the backwards-compatible `day::resources!()` catalog. Dayscript text
assertions name the owning catalog, e.g. `reversi::black_turn`; keyboard keys are unchanged.

These generated APIs require the accompanying local `day/` changes; publish those framework
changes before CI fetches `day@main`. Locale tests cover every private message and the
per-file imports, in addition to the normal game tests.

Charades has original animal and food decks in every added language, with more than 100
unique prompts per deck. The existing English collection retains its 21 themes. Localized
players see their own decks; additional themes can be added following
[`games/charades/words/README.md`](../games/charades/words/README.md). Store descriptions state
this difference. The localized decks are curated for familiar words rather than requiring
one-to-one equivalence with the English lists.

`store/<locale>/` contains the name, subtitle, short and full descriptions, promotional text,
keywords, release notes and URLs. Descriptions cover all ten games, including Reversi and
Pipes. Shared URLs deliberately point to the same project/support/privacy destinations.
Release notes should be reviewed for each release. Run `day store stage` to generate Apple
and Google fastlane metadata; this does not upload anything.

The website reads those store descriptions. `dayscript/games.yaml` contains localized titles
and captions for all curated gallery rows. CI runs all four gameplay scripts in all 13
locales on the eight primary targets; those captures populate the localized galleries.
The shared `daysite` template carries translated controls and forwards the landing page's
locale to the hosted web app. Publish its companion changes before running the app CI that
fetches `daysite@main`; the local preview uses the modified checkout.

## Checks

```sh
python3 scripts/check-locales.py
cargo test --workspace --lib
cargo test --test locales
# Install Playwright and its chosen browser, then configure the Day web driver as documented
# in day/docs/web.md. Run from the app root:
day launch -p web-dom --env DAY_GAMES_SEED=15 \
  --locales 'en ar de es fr hi id it ja ko pt-BR ru zh-CN' \
  --script dayscript/smoke.yaml --script dayscript/games.yaml \
  --script dayscript/reversi.yaml --script dayscript/pipes.yaml
```

The checker verifies the catalog keys/arguments, store text limits, word-deck coverage,
gallery metadata and agreement between website and CI locales. The normal Rust build parses
Fluent syntax; Charades tests validate deck contents; the locale integration test checks actual
message rendering, metadata title interpolation and Chinese aliases.

## Local website

Use the conventional `website/.daysite/` template checkout and its preview command described
in the daysite README. `day build -p web-dom` produces the browser app under
`build/day/cargo/web-dom/debug/dist/`; copy its contents into the template's `public/webapp/`
before building the website. Browser app links accept `?locale=fr`, `?locale=ar`, etc.

## Submission prerequisites

All localized text can be staged locally. A real App Store submission still needs the
reviewer's first name, last name and phone number in `store/app.toml` (the existing email is
`hello@daybrite.dev`), and screenshots for the required Apple device sizes from the platform
CI runs. Browser screenshots alone do not replace those required device captures.
