xkeyboard-config [2.45] - 2025-06-08
====================================

[2.45]: https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/tree/xkeyboard-config-2.45

## Models

### Fixes

- Norwegian Macintosh layout: Fixed the `apostrophe` key to actually output
  `apostrophe` instead of `bar`.

  Contributed by Håvard Bærug
  ([!801](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/merge_requests/801))


## Layouts

### Breaking changes

- Deleted obsolete `jp(kana86)` layout.
  ([#502](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/502))

### New

- Added Colemak variant for Swedish: `se(colemak)`.

  Contributed by satricus
  ([!761](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/merge_requests/761))
- French (AZERTY, AFNOR): Implemented the “European character” dead key on `AltGr+H`,
  as documented at the [offical web page](https://norme-azerty.fr/img/EU_level.png).
  Also fixed the missing upper Theta Θ on `Q`.
- `ru(typo)`: Added bar symbol on the `<BKSL>` key.

  Contributed by Boolat Kamalov
  ([!814](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/merge_requests/814))

### Fixes

- `us(colemak_dh)`: Fix the CapsLock remapping being difficult to override.
  ([#490](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/490))
- Japanese layouts: Fix Eisu toggle triggering CapsLock when the layout is not in
  the first position. ([#512](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/512))
- Apple: fix ISO keyboards International English layout (`<TLDE>`, `<LSGT>` keys permutation).

  Contributed by Andrey Butirsky
  ([!793](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/merge_requests/793))
- Faroese `fo`: use comma as the decimal separator for the numpad.

  Contributed by Ragnar Kruse
  ([!815](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/merge_requests/815))


## Options

### New

- Added two compatibility options related to `Hyper`:
  - `hyper:mod3`: maps the virtual modifier `Hyper` to `Mod3`; *conflicts with `LevelFive`*.
    Loaded by default when using any option with `Hyper`.
  - `hyper:mod4`: maps the virtual modifier `Hyper` to `Mod3`; *conflicts with `Super`*.
    Use this option if using both `Hyper` *and* `LevelFive`, e.g. for layouts with 5+ levels.

### Fixes

- `shift:breaks_caps`: Fix missing `Shift_{L,R}` keysyms that prevented
  keyboard shortcuts to work correctly in some setups.


## Miscellaneous

### Breaking changes

- Added `KEY_ZENKAKUHANKAKU` mapping for touchpad toggle.

  Pressing the touchpad toggle key on some notebooks produces the key sequence
  `Super + Control + KEY_ZENKAKUHANKAKU`. Actual Japanese Hankaku/Zenkaku keys
  however do not use this keycode, but the <TLDE> one instead.

  Contributed by Werner Sembach
  ([!810](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/merge_requests/810))
- The default mapping of the virtual modifier `Hyper` to `Mod3` is now deactivated
  by default, because it conflicts with `LevelFive`, which is used in various layouts
  with 5+ levels.

  It is now enabled only when using any option binding `Hyper` keysyms or when
  using the new option `hyper:mod3`. However, if one one want to use `LevelFive`
  and `Hyper` simultaneously (e.g. for layouts with 5+ levels), then the new
  alternative option `hyper:mod4` should be used instead.


## Build system

### Breaking changes

- Switched to versioned install directories and files, to enable installing
  multiple versions of xkeyboard-config to be installed in parallel.

  - Moved the keyboard keymap data to a namespace dedicated to xkeyboard-config:
    `<prefix>/<datadir>/xkeyboard-config-2`.
  - Created symbolic link to maintain backward-compatibility with the X11 namespace:
    `<prefix>/<datadir>/X11/xkb` → `<prefix>/<datadir>/xkeyboard-config-2`.
  - Renamed `pkg-config`, translation and manual files to include a version:
    - `<prefix>/<datadir>/pkgconfig/xkeyboard-config-2.pc`
    - `<prefix>/<mandir>/man7/xkeyboard-config-2.7`
    - `<prefix>/<localedir>/**/xkeyboard-config-2.mo`
  - Created unversioned symbolic links to the previous files for backward-compatibility:
    - `<prefix>/<datadir>/pkgconfig/`: `xkeyboard-config.pc` → `xkeyboard-config-2.pc`
    - `<prefix>/<mandir>/man7/`: `xkeyboard-config.7` → `xkeyboard-config-2.7`
    - `<prefix>/<localedir>/**/`: `xkeyboard-config.mo` → `xkeyboard-config-2.mo`

  See [our versioning documentation](VERSIONING.md) for further information.


xkeyboard-config [2.44] - 2025-02-05
====================================

[2.44]: https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/tree/xkeyboard-config-2.44

## Models

### Fixes

- Fixed rules for vendor-specific layouts, in particular for Sun and Apple
  Aluminium keyboards.
  ([#112](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/112))
- Apple: swap `<TLDE>` and `<LSGT>` keysyms for Russian layout.


## Layouts

### Breaking changes

- Breton: Fixed capitalization of “c’h” and “ch”
  [multigraphs](https://en.wikipedia.org/wiki/Multigraph_%28orthography%29) using
  CapsLock, as well as Greek letters. A few Greeks letters were moved to more
  intuitive places.
  ([#480.breton](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/480.breton))

### New

- Added Noted layout `de(noted)` for German.

  Contributed by Benjamin Drung
  ([!681](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/merge_requests/681))


## Options

### Breaking changes

- Disabled "Alt and Meta are on Alt" by default. The old behavior can be restored
  by enabling the `altwin:meta_alt` option.
  ([#488](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/488))


## Miscellaneous

### New

- inet: Added `XF86Assistant` as default mapping to the Super + Shift + F23
  keyboard combo, aka the "Copilot Key".
- inet: Added mapping to the following new keysyms:
  - `XF86RefreshRateToggle`
  - `XF86Accessibility`
  - `XF86DoNotDisturb`

  Relevant upstream merge request: [xorgproto-91].

  [xorgproto-91]: https://gitlab.freedesktop.org/xorg/proto/xorgproto/-/merge_requests/91

### Fixes

- Fixed missing virtual modifiers declarations, in order to allow all sections to
  be used in isolation.


xkeyboard-config [2.43] - 2024-10-01
====================================

[2.43]: https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/tree/xkeyboard-config-2.43

## Models

### New

- Restore geometries for Brazilian ABNT2 (`abnt2`), Japanese 106 (`jp106`)
  and Korean 106 (`kr106`) models. ([#292](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/292))

### Fixes

- geometry: Fixed label of `<LSGT>` key in Kinesis.

  Contributed by Arlen Kleinsasser


## Layouts

### Breaking changes

- `us(colemak_dh_wide_iso)`: Swapped `<AB06>` and `<AD12>` keys to match [specification](https://colemakmods.github.io/mod-dh/keyboards.html)

  Contributed by Callum Andrew ([#442](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/442))
- Updated `de(e1)` and `de(e2)`: implemented the changes made to these layouts in the latest revision of the specification, DIN 2137-1:2023-08; namely, some of the *group 2* symbols, that are accessed by first pressing Alt&nbsp;Gr+f, for keys `´`, `u`, `p`, `,`, and space bar were altered.

  Contributed by Jan Henning Klasen and Jakob Kramer. ([#745](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/745))
- `us(colemak_dh)`: Made `<CAPS>` key behave as Caps Lock by default, as shown in the [specification](https://colemakmods.github.io/mod-dh/keyboards.html).

### New

- Added Diktor layout `ru(diktor)` for Russian.

  Contributed by Hloya Nizhelska ([!712](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/merge_requests/712))
- Added the RuIntl keyboard layouts set `ru(ruintl_ru)`, `ru(ruintl_en)`.

  Contributed by Denis Kaliberov ([!752](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/merge_requests/752))
- Updated layout `us 3l` to include qwerty symbols and correct symbols for less than or equal and greater than or equal.

### Fixes

- rules: Fix broken layout compatibility rules, for symbols sections that where renamed or moved. ([#478](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/478))


## Options

### Breaking changes

- Map `Hyper` to `Mod3` by default to make `Super` and `Hyper` independent
  modifiers. ([#440](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/440))

### New

- Added `caps:return` to make the `Caps Lock` key an additional `Return` key. ([#121](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/121))
- Added `fkeys:basic_13-24`: define `F13-F24` keys with their corresponding function keysyms.

  Contributed by twistedturtle ([#306](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/306))
- Added `altwin:swap_ralt_rwin` to swap right `Alt` with right `Win`. ([#474](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/474))
- Added `caps:digits_row_independent_lock` option to lock digits on the digits
  row (Azerty layouts).

  Contributed by Alexandre Petit
- Added option `lv3:caps_switch_capslock_with_ctrl` to use Caps Lock as
  3rd-level chooser and Ctrl + Caps Lock as original Caps Lock action.

  Contributed by Helfried Wiesinger

### Fixes

- Added `caps:ctrl_shifted_capslock`: make `Caps Lock` an additional `Ctrl`
  and `Shift + Caps Lock` the regular `Caps Lock`.

  Contributed by Han-Miru Kim ([#447](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/447))


## Miscellaneous

### New

- Added `<I570>` keycode (`KEY_REFRESH_RATE_TOGGLE`).


## Build system

### New

- Add a new build option `non-latin-layouts-list` to generate lists of
  non-Latin layouts, e.g. layouts that cannot produce the basic A-Z Latin
  letters. This can be used e.g. in an OS installer to add automatically
  a default layout in such case. ([#120](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/120))

### Fixes

- Relaxed Python version requirement to support ≥ 3.9.
  Improved version detection and corresponding error messages. ([#465](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/465))


xkeyboard-config [2.42] - 2024-06-07
====================================

[2.42]: https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/tree/xkeyboard-config-2.42

## Models

### Breaking

- Removed the old Macs
- Removed the MacBook 78/79
- Removed the Intel Classmate
- Removed a few old Nokia devices


## Layouts

### Breaking change

- `dz`: Renamed `la` to `azerty-oss`.
- `br`: Removed the default `Scroll_Lock` mapping.

### New

- `ara(mac-phonetic)`: use new dead key `dead_hamza`.
- `dz`: Added `kab` to the language list.
- `fr`: Added Ergo‑L layout and variant (`ergol`, `ergol_iso`).
- `gr`: Added missing characters from `cp1253` and `varEpsilon`.
- `hu`: Added Old Hungarian layouts for users in SK
- symbols: Added grab and srvrkeys with a single section
- `ru`: Updated Rulemak to latest version.
- `ru(ruu)`: Added `Ukrainian_i` as `Cyrillic_i` alternative to the
   3rd level of `<AB05>`.
- `ua`: Enabled typing “g” with `AltGr`.

### Fixes

- `fr(oss)`: Updated behaviour of space key to match doc.
  [#439](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/439)
- `fr(bepo_afnor)`: Removed unnecessary include.
  [#448](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/448)


## Options

## New

- Added `eurosign:E`.
  [#444](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/444)
- Added `caps:digits_row` for Azerty layouts.
- Added `scrolllock:mod3`.


Older versions
==============

Unfortunately there is no detailed changelog for older versions. Please use the
[git log](https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/commits/master).
