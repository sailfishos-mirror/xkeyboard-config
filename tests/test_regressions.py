# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Optional

import pytest
import xkbcommon
from xkbcommon import (
    Control,
    Lock,
    Mod1,
    Mod3,
    Mod4,
    Mod5,
    ModifierMask,
    NoModifier,
    Shift,
)

###############################################################################
# pytest configuration
###############################################################################

# You may skip this section and go to the section “How-to write tests”
# if you only intend to write new tests.
#
# How the test suite works
# ------------------------
#
# Interfacing with xkbcommon requires:
# • Taking care of initialization and finalization of foreign objects.
#   This is done using `xkbcommon.ForeignKeymap` and `xkbcommon.ForeignState`
#   context managers.
# • Updating the state: this is down with `xkbcommon.State`.
#
# pytest fixtures:
# • The only fixture intended in the test code is `keymap`.
# • Other fixtures are just helpers that are used indirectly.
# • The intended use is documented in `TestSuiteDoc`.


KEYCODE_PATTERN = re.compile(
    r"""^(?:
        # Usual keycodes
          [A-Z]         # Start with an upper case letter
          [A-Z0-9]{1,3} # Followed by up to 3 characters
        # Latin aliases
        | Lat[A-Z]
        # Special cases
        | VOL-
        | VOL\+
        )$
     """,
    re.VERBOSE,
)


@pytest.mark.parametrize("key", ("UP", "TAB", "AE01", "RTRN", "VOL-", "I120", "LatA"))
def test_valid_keycode_pattern(key: str):
    assert KEYCODE_PATTERN.match(key)


@pytest.mark.parametrize(
    "key", ("U", "LFTSH", "Shift_L", "lfsh", "9", "1I20", "latA", "Lat9")
)
def test_invalid_keycode_pattern(key: str):
    assert not KEYCODE_PATTERN.match(key)


BASE_GROUP = 1
BASE_LEVEL = 1


def check_keycode(key: str) -> bool:
    """Check that keycode has the required syntax."""
    return bool(KEYCODE_PATTERN.match(key))


@dataclass
class Keymap:
    """Public test methods"""

    Alt: int
    Meta: int
    Super: int
    Hyper: int
    Level3: int
    Level5: int

    has_vmod_queries: bool

    def __init__(
        self,
        keymap: xkbcommon.ForeignKeymap,
        state: xkbcommon.State,
        has_vmod_queries: bool,
    ):
        self._state = state
        self._keymap = keymap
        mod = xkbcommon.xkb_keymap_mod_get_index(keymap, "Alt")
        self.Alt = (1 << mod) if mod != xkbcommon.XKB_MOD_INVALID else 0
        mod = xkbcommon.xkb_keymap_mod_get_index(keymap, "Meta")
        self.Meta = (1 << mod) if mod != xkbcommon.XKB_MOD_INVALID else 0
        mod = xkbcommon.xkb_keymap_mod_get_index(keymap, "Super")
        self.Super = (1 << mod) if mod != xkbcommon.XKB_MOD_INVALID else 0
        mod = xkbcommon.xkb_keymap_mod_get_index(keymap, "Hyper")
        self.Hyper = (1 << mod) if mod != xkbcommon.XKB_MOD_INVALID else 0
        mod = xkbcommon.xkb_keymap_mod_get_index(keymap, "LevelThree")
        self.Level3 = (1 << mod) if mod != xkbcommon.XKB_MOD_INVALID else 0
        mod = xkbcommon.xkb_keymap_mod_get_index(keymap, "LevelFive")
        self.Level5 = (1 << mod) if mod != xkbcommon.XKB_MOD_INVALID else 0
        self.has_vmod_queries = has_vmod_queries

    def press(self, key: str) -> xkbcommon.Result:
        """Update the state by pressing a key"""
        assert check_keycode(key), "key must be a [2-4]-character keycode"
        return self._state.process_key_event(
            key, xkbcommon.xkb_key_direction.XKB_KEY_DOWN
        )

    def release(self, key: str) -> xkbcommon.Result:
        """Update the state by releasing a key"""
        assert check_keycode(key), "key must be a [2-4]-character keycode"
        return self._state.process_key_event(
            key, xkbcommon.xkb_key_direction.XKB_KEY_UP
        )

    def tap(self, key: str) -> xkbcommon.Result:
        """Update the state by tapping a key"""
        assert check_keycode(key), "key must be a [2-4]-character keycode"
        self.press(key)
        return self.release(key)

    def tap_and_check(
        self, key: str, keysym: str, group: int = BASE_GROUP, level: int = BASE_LEVEL
    ) -> xkbcommon.Result:
        """
        Check that tapping a key produces the expected keysym in the
        expected group and level.
        """
        r = self.tap(key)
        assert r.group == group
        assert r.level == level
        assert r.keysym == keysym
        # Return the result for optional further tests
        return r

    def key_down(self, *keys: str) -> _KeyDown:
        """Update the state by holding some keys"""
        assert all(map(check_keycode, keys)), "keys must be a [2-4]-character keycodes"
        return _KeyDown(self, *keys)

    def mask_from_names(self, names: Iterable[str]) -> ModifierMask:
        return xkbcommon.xkb_keymap_get_mod_mask_from_names(self._keymap, names)

    def full_mask(self, mask: ModifierMask) -> ModifierMask:
        return (
            xkbcommon.xkb_keymap_get_usual_mod_mapping(self._keymap, mask)
            if self.has_vmod_queries
            else mask
        )


# NOTE: Abusing Python’s context manager to enable nice test syntax
class _KeyDown:
    """Context manager that will hold a key."""

    def __init__(self, keymap: Keymap, *keys: str):
        self.keys = keys
        self.keymap = keymap

    def __enter__(self) -> xkbcommon.Result:
        """Press the key in order, then return the last result."""
        return reduce(
            lambda _, key: self.keymap.press(key),
            self.keys,
            xkbcommon.Result(0, 0, "", "", 0, NoModifier, NoModifier, ()),
        )

    def __exit__(self, *_):
        for key in self.keys:
            self.keymap.release(key)


@pytest.fixture(scope="session")
def xkb_base():
    """Get the xkeyboard-config directory from the environment."""
    path = os.environ.get("XKB_CONFIG_ROOT")
    if path:
        return Path(path)
    else:
        raise ValueError("XKB_CONFIG_ROOT environment variable is not defined")


@pytest.fixture(scope="session")
def has_vmod_queries(xkb_base: Path) -> bool:
    return xkbcommon.has_vmod_queries(xkb_base)


# The following fixtures enable them to have default values (i.e. None).


@pytest.fixture(scope="function")
def rules(request: pytest.FixtureRequest):
    return getattr(request, "param", None)


@pytest.fixture(scope="function")
def model(request: pytest.FixtureRequest):
    return getattr(request, "param", None)


@pytest.fixture(scope="function")
def layout(request: pytest.FixtureRequest):
    return getattr(request, "param", None)


@pytest.fixture(scope="function")
def variant(request: pytest.FixtureRequest):
    return getattr(request, "param", None)


@pytest.fixture(scope="function")
def options(request: pytest.FixtureRequest):
    return getattr(request, "param", None)


@pytest.fixture
def keymap(
    xkb_base: Path,
    has_vmod_queries: bool,
    rules: Optional[str],
    model: Optional[str],
    layout: Optional[str],
    variant: Optional[str],
    options: Optional[str],
):
    """Load a keymap, and return a new state."""
    with xkbcommon.ForeignKeymap(
        xkb_base,
        rules=rules,
        model=model,
        layout=layout,
        variant=variant,
        options=options,
    ) as km:
        with xkbcommon.ForeignState(km) as state:
            yield Keymap(km, state, has_vmod_queries)


# Documented example
# The RMLVO parameters (“rules”, “model”, “layout”, “variant” and “options”)
# are optional and are implicitely consumed by the keymap fixture.
@pytest.mark.parametrize("layout", ["us"])
class TestSuiteDoc:
    # The keymap argument is mandatory. It will:
    # • Load the keymap corresponding to the RMLVO input;
    # • Initialize a new state;
    # • Return a convenient `Keymap` object, that will manage the
    #   low-level xkbcommon stuff and provide methods to safely change
    #   the state.
    def test_example(self, keymap: Keymap):
        # Use keymap to change keyboard state
        r = keymap.press("AC01")
        # The return value is used in assertions
        assert r.keysym == "a"
        # When the function returns, if will automatically run the
        # cleanup code of the keymap fixture, i.e. the __exit__
        # function of `xkbcommon.ForeignKeymap` and
        # `xkbcommon.ForeignKeymap`.
        # See further examples in the section “How-to write tests”.


###############################################################################
# How-to write tests
###############################################################################

# • Create one class per topic. It should have a meaningful name prefixed by
#   `Test` and refer to the topic: e.g. TestCompatibilityOption1Option2.
#   If there is a Gitlab issue it can be named after it: e.g. TestGitlabIssue382.
# • The intended use is commented in the following `TestExample` class.


# The RMLVO XKB configuration is set with parameters “rules”, “model”, “layout”,
# “variant” and “options”. They are optional and default to None.
@pytest.mark.parametrize("layout", ["de"])
# Name prefixed with `Test`.
class TestExample:
    # Define one function for each test. Its name must be prefixed by `test_`.
    # The keymap argument is mandatory. It provides methods to safely
    # change the keyboard state.
    def test_example(self, keymap: Keymap):
        # Use keymap to change keyboard state
        r = keymap.press("LFSH")
        # The return value is used in assertions
        assert r.keysym == "Shift_L"
        # We must not forget to release the key, if necessary:
        keymap.release("LFSH")
        # Or we could also use `Keymap.key_down` to achieve the same:
        with keymap.key_down("LFSH") as r:
            assert r.keysym == "Shift_L"
            # Now we can check the impact of modifier on other keys.
            # Manually:
            r = keymap.tap("AC01")
            assert r.level == 2
            assert r.keysym == "A"
            # With helper function:
            keymap.tap_and_check("AC01", "A", level=2)
        # We can also use multiple keys:
        with keymap.key_down("LFSH", "RALT") as r:
            # In this case the result refers to the last key
            assert r.keysym == "ISO_Level3_Shift"
            r = keymap.tap_and_check("AC01", "AE", level=4)
            # We can also check (real) modifiers directly
            Level3 = keymap.Level3 if keymap.has_vmod_queries else NoModifier
            assert r.active_mods == Shift | Mod5 | Level3 == r.consumed_mods


###############################################################################
# Regression Tests
###############################################################################


# https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/382
@pytest.mark.parametrize("layout,variant,options", [("us", "intl", "lv3:lwin_switch")])
class TestIssue382:
    @pytest.mark.parametrize("mod_key", ("RALT", "LWIN"))
    def test_LevelThree(self, keymap: Keymap, mod_key: str):
        """Both RALT and LWIN are LevelThree modifiers"""
        with keymap.key_down(mod_key):
            r = keymap.tap_and_check("AD01", "adiaeresis", level=3)
            Level3 = keymap.Level3 if keymap.has_vmod_queries else NoModifier
            assert r.active_mods == Mod5 | Level3 == r.consumed_mods
            with keymap.key_down("LFSH"):
                r = keymap.tap_and_check("AD01", "Adiaeresis", level=4)
                assert r.active_mods == Shift | Mod5 | Level3 == r.consumed_mods

    def test_ShiftAlt(self, keymap: Keymap):
        """LALT+LFSH works as if there was no option"""
        r = keymap.tap_and_check("AC10", "semicolon", level=1)
        assert r.active_mods == NoModifier
        with keymap.key_down("LFSH", "LALT"):
            r = keymap.tap_and_check("AC10", "colon", level=2)
            Alt = keymap.Alt if keymap.has_vmod_queries else NoModifier
            Meta = keymap.Meta if keymap.has_vmod_queries else NoModifier
            assert r.active_mods == Shift | Mod1 | Alt | Meta
            assert r.consumed_mods == Shift


# https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/90
# https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/346
class TestIssues90And346:
    @pytest.mark.parametrize(
        "layout,key,keysyms",
        [
            ("fi,us", "TLDE", ("section", "grave")),
            ("dk,us", "TLDE", ("onehalf", "grave")),
            ("fi,us,dk", "TLDE", ("section", "grave", "onehalf")),
        ],
    )
    @pytest.mark.parametrize(
        "options,mod_key,mod",
        [
            ("grp:win_space_toggle", "LWIN", Mod4),
            ("grp:alt_space_toggle", "LALT", Mod1),
        ],
    )
    def test_group_switch_on_all_groups(
        self,
        keymap: Keymap,
        mod_key: str,
        mod: ModifierMask,
        key: str,
        keysyms: tuple[str],
    ):
        """LWIN/LALT + SPCE is a group switch on multiple groups"""
        mods = keymap.full_mask(mod)
        for group, keysym in enumerate(keysyms, start=1):
            print(group, keysym)
            keymap.tap_and_check(key, keysym, group=group)
            self.switch_group(keymap, mod_key, mods, group % len(keysyms) + 1)
        # Check the group wraps
        keymap.tap_and_check(key, keysyms[0], group=1)

    @staticmethod
    def switch_group(keymap: Keymap, mod_key: str, mod: ModifierMask, group: int):
        with keymap.key_down(mod_key) as r:
            assert r.group == 1  # only defined on first group
            r = keymap.tap_and_check("SPCE", "ISO_Next_Group", group=group, level=2)
            assert r.active_mods == mod == r.consumed_mods


# https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/383
@pytest.mark.parametrize("layout", ["us,ru"])
@pytest.mark.parametrize(
    "options,mod_key,mod",
    [
        ("misc:typo,grp:win_space_toggle,lv3:ralt_switch", "LWIN", Mod4),
        ("misc:typo,grp:alt_space_toggle,lv3:ralt_switch", "LALT", Mod1),
    ],
)
class TestIssue383:
    def test_group_switch(self, keymap: Keymap, mod_key: str, mod: ModifierMask):
        """LWIN + SPCE is a group switch on both groups"""
        mods = keymap.full_mask(mod)
        # Start with us layout
        self.check_keysyms(keymap, 1, "AC01", "a", "combining_acute")
        # Switch to ru layout
        self.switch_group(keymap, mod_key, mods, 2)
        self.check_keysyms(keymap, 2, "AC01", "Cyrillic_ef", "combining_acute")
        # Switch back to us layout
        self.switch_group(keymap, mod_key, mods, 1)
        self.check_keysyms(keymap, 1, "AC01", "a", "combining_acute")

    @staticmethod
    def switch_group(keymap: Keymap, mod_key: str, mod: ModifierMask, group: int):
        with keymap.key_down(mod_key) as r:
            assert r.group == 1  # only defined on first group
            r = keymap.tap_and_check("SPCE", "ISO_Next_Group", group=group, level=2)
            assert r.active_mods == mod == r.consumed_mods

    @staticmethod
    def check_keysyms(
        keymap: Keymap, group: int, key: str, base_keysym: str, typo_keysym: str
    ):
        # Base keysym
        keymap.tap_and_check(key, base_keysym, group=group, level=1)
        # typo keysym
        with keymap.key_down("RALT") as r:
            assert r.group == 1  # only defined on first group
            r = keymap.tap_and_check(key, typo_keysym, group=group, level=3)
            Level3 = keymap.Level3 if keymap.has_vmod_queries else NoModifier
            assert r.active_mods == Mod5 | Level3 == r.consumed_mods


# https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/500
@pytest.mark.parametrize("layout,variant", [("us", "3l")])
class TestIssue500:
    def test_levels_1_and_3(self, keymap: Keymap):
        r = keymap.tap_and_check("AD01", "q", level=1)
        # Level 3
        with keymap.key_down("AC11"):
            r = keymap.tap_and_check("AD01", "quotedbl", level=3)
            Level3 = keymap.Level3 if keymap.has_vmod_queries else NoModifier
            assert r.active_mods == Mod5 | Level3 == r.consumed_mods

    def test_no_conflict(self, keymap: Keymap):
        """LevelFive and Super are independent; no Hyper mapping"""
        # Level 5
        with keymap.key_down("AB10"):
            r = keymap.tap_and_check("AD01", "Prior", level=5)
            Level5 = keymap.Level5 if keymap.has_vmod_queries else NoModifier
            assert r.active_mods == Mod3 | Level5 == r.consumed_mods
        # Super
        with keymap.key_down("LWIN"):
            r = keymap.tap_and_check("AD01", "q", level=1)
            Super = keymap.Super if keymap.has_vmod_queries else NoModifier
            assert r.active_mods == Mod4 | Super
            assert r.consumed_mods == 0
        # Hyper is not mapped
        with keymap.key_down("HYPR"):
            r = keymap.tap_and_check("AD01", "q", level=1)
            assert r.active_mods == 0 == r.consumed_mods

    @pytest.mark.parametrize(
        "options,hyper_key,control_key",
        (("caps:hyper", "CAPS", "LCTL"), ("ctrl:hyper_capscontrol", "LCTL", "CAPS")),
    )
    def test_LevelThree_Hyper_conflict(
        self, keymap: Keymap, hyper_key: str, control_key: str
    ):
        """LevelFive conflicts with Hyper (Mod3)"""
        self.test_levels_1_and_3(keymap)
        # Level 5 and Hyper
        Level5 = keymap.Level5 if keymap.has_vmod_queries else NoModifier
        Hyper = keymap.Hyper if keymap.has_vmod_queries else NoModifier
        level5_key = "AB10"
        for mod_key in (level5_key, hyper_key):
            with keymap.key_down(mod_key):
                r = keymap.tap_and_check("AD01", "Prior", level=5)
                assert r.active_mods == Mod3 | Level5 | Hyper == r.consumed_mods
        # Control
        with keymap.key_down(control_key):
            r = keymap.tap_and_check("AD01", "q", level=1)
            assert r.active_mods == Control
            assert r.consumed_mods == 0
        # Super
        with keymap.key_down("LWIN"):
            r = keymap.tap_and_check("AD01", "q", level=1)
            Super = keymap.Super if keymap.has_vmod_queries else NoModifier
            assert r.active_mods == Mod4 | Super
            assert r.consumed_mods == 0

    @pytest.mark.parametrize(
        "options,hyper_key,control_key",
        (
            ("caps:hyper,hyper:mod4", "CAPS", "LCTL"),
            ("ctrl:hyper_capscontrol,hyper:mod4", "LCTL", "CAPS"),
        ),
    )
    def test_Super_Hyper_conflict(
        self, keymap: Keymap, hyper_key: str, control_key: str
    ):
        """Super conflicts with Hyper (Mod4)"""
        self.test_levels_1_and_3(keymap)
        # Level 5
        with keymap.key_down("AB10"):
            r = keymap.tap_and_check("AD01", "Prior", level=5)
            Level5 = keymap.Level5 if keymap.has_vmod_queries else NoModifier
            assert r.active_mods == Mod3 | Level5 == r.consumed_mods
        # Control
        with keymap.key_down(control_key):
            r = keymap.tap_and_check("AD01", "q", level=1)
            assert r.active_mods == Control
            assert r.consumed_mods == 0
        # Super and Hyper
        super_key = "LWIN"
        for mod_key in (super_key, hyper_key):
            with keymap.key_down(mod_key):
                r = keymap.tap_and_check("AD01", "q", level=1)
                Super = keymap.Super if keymap.has_vmod_queries else NoModifier
                Hyper = keymap.Hyper if keymap.has_vmod_queries else NoModifier
                assert r.active_mods == Mod4 | Super | Hyper
                assert r.consumed_mods == 0


# https://gitlab.freedesktop.org/xkeyboard-config/xkeyboard-config/-/issues/512
@pytest.mark.parametrize("model", ["jp106", "applealu_jis"])
@pytest.mark.parametrize(
    "layout,variant",
    [
        ("jp", ""),
        ("jp", "OADG109A"),
        ("jp", "kana"),
        ("jp,jp", ",OADG109A"),
        ("jp,jp", "OADG109A,"),
        ("jp,jp", "OADG109A,kana"),
        ("jp,us", ","),
        ("us,jp", ","),
        ("jp,jp,jp", ",OADG109A,kana"),
        ("jp,us,gb", "kana,,"),
        ("us,jp,gb", ",kana,"),
        ("us,gb,jp", ",,kana"),
        ("us,jp,jp,jp", ",,kana,OADG109A"),
        ("jp,es,de,us", "mac,,,"),
        ("us,jp,es,de", ",mac,,"),
        ("us,es,jp,de", ",,mac,"),
        ("us,es,de,jp", ",,,mac"),
    ],
)
@pytest.mark.parametrize("options", ["grp:menu_toggle"])
class TestIssue512:
    def test_eisu(self, keymap: Keymap, layout: str):
        """Eisu_toggle does not toggle CapsLock on Japanese layouts"""
        layouts = layout.split(",")
        for layout_index, layout_ in enumerate(layouts, start=1):
            self.tap_and_check(keymap, "CAPS", layout_index if layout_ == "jp" else 1)
            keymap.tap_and_check("MENU", "ISO_Next_Group", group=1, level=1)

    @staticmethod
    def tap_and_check(keymap: Keymap, key: str, layout: int):
        r = keymap.tap(key)
        if r.keysym == "Caps_Lock":
            # Cancel CapsLock
            r = keymap.tap(key)
            assert r.active_mods is Lock
            r = keymap.tap("AB01")
            assert r.active_mods is NoModifier
        else:
            # Check Eisu does not trigger CapsLock
            assert r.keysym == "Eisu_toggle"
            assert r.layout == layout
            assert r.level == 1
            assert r.active_mods is NoModifier
