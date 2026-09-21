//! Exercise launch catalogs, including Chinese tags used by Apple and browsers.
#[test]
fn every_launch_locale_resolves_app_strings_and_arguments() {
    let (default, catalogs) = dayapp::window().locales.unwrap();
    day::install_locales(default, catalogs);
    for (locale, _) in catalogs {
        day::prelude::set_locale(locale);
        let title = dayapp::res::str::app_title("Fork Title").format();
        assert!(title.contains("Fork Title"), "{locale}: {title}");
        let closed = gamekit::res::chrome::str::close().format();
        assert!(!closed.is_empty() && closed != "gk_close", "{locale}");
        let level = breakout::res::str::level_clear(7).format();
        assert!(
            !level.contains('$') && !level.contains('{'),
            "{locale}: {level}"
        );
    }
    day::prelude::set_locale("zh-CN");
    let chinese = gamekit::res::chrome::str::close().format();
    for locale in ["zh-Hans", "zh-Hans-CN", "zh-SG"] {
        day::prelude::set_locale(locale);
        assert_eq!(
            gamekit::res::chrome::str::close().format(),
            chinese,
            "{locale}"
        );
    }
}

/// Every game deliberately uses the same key: the catalog carried by its accessor decides it.
#[test]
fn game_titles_are_private_and_follow_locale_switches() {
    let titles = [
        (blockblast::res::str::game_title(), "Block Blast"),
        (breakout::res::str::game_title(), "Breakout"),
        (charades::res::str::game_title(), "Charades"),
        (mines::res::str::game_title(), "Mines"),
        (reversi::res::str::game_title(), "Reversi"),
        (pipes::res::str::game_title(), "Pipes"),
        (sirtet::res::str::game_title(), "Sirtet"),
        (solitaire::res::str::game_title(), "Solitaire"),
        (sudoku::res::str::game_title(), "Sudoku"),
        (twentyfortyeight::res::str::game_title(), "2048"),
    ];
    day::install_locales("en", &[("en", "game_title = Wrong app-global title\n")]);
    day::prelude::set_locale("en");
    for (title, expected) in &titles {
        assert_eq!(title.format(), *expected);
    }
    day::prelude::set_locale("ja");
    assert_eq!(
        titles[0].0.format(),
        blockblast::res::str::game_title().format()
    );
    assert_eq!(titles[3].0.format(), "マインスイーパー");
    // A per-source-file scope also imports the crate-wide app.ftl functions.
    assert_eq!(
        gamekit::res::chrome::str::score().format(),
        gamekit::res::str::score().format()
    );
}

#[test]
fn every_private_message_formats_in_every_shipped_locale() {
    let catalogs = [
        &gamekit::res::locales::SCOPE,
        &gamekit::res::chrome::locales::SCOPE,
        &blockblast::res::locales::SCOPE,
        &breakout::res::locales::SCOPE,
        &charades::res::locales::SCOPE,
        &mines::res::locales::SCOPE,
        &reversi::res::locales::SCOPE,
        &pipes::res::locales::SCOPE,
        &sirtet::res::locales::SCOPE,
        &solitaire::res::locales::SCOPE,
        &sudoku::res::locales::SCOPE,
        &twentyfortyeight::res::locales::SCOPE,
    ];
    for catalog in catalogs {
        assert_eq!(catalog.locales.len(), 13, "{}", catalog.name);
        for (locale, source) in catalog.locales {
            for line in source.lines().filter(|l| !l.starts_with('#')) {
                let Some((key, value)) = line.split_once(" = ") else {
                    continue;
                };
                let args: Vec<_> = value
                    .split('$')
                    .skip(1)
                    .map(|part| {
                        let name: String = part
                            .chars()
                            .take_while(|c| c.is_alphanumeric() || *c == '_')
                            .collect();
                        (name, day::FArg::Num(7.0))
                    })
                    .collect();
                let rendered = day::format_catalog(catalog, locale, key, &args);
                assert!(
                    !rendered.is_empty() && !rendered.contains('⟨') && !rendered.contains('{'),
                    "{}::{key}/{locale}: {rendered}",
                    catalog.name
                );
            }
        }
    }
}
