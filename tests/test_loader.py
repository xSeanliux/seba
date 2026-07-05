from seba.models import Agenda
from seba.session.loader import load_overlay, load_profile, recovery_prompt, system_prompt


def agenda():
    return Agenda(goal="g", subject="probability", session_number=1,
                  briefing="Session 1.", review_items=[], teach_concept=None,
                  practice_quota=3, pace_hint="steady")


def test_load_bundled_profiles():
    p = load_profile("probability")
    assert p.max_reviews_per_session == 6 and p.kind == "technical"
    i = load_profile("italian")
    assert i.max_reviews_per_session == 20
    assert load_profile("nonexistent") is None


def test_user_profile_overrides(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path))
    d = tmp_path / "subjects" / "astronomy"
    d.mkdir(parents=True)
    (d / "profile.yaml").write_text(
        "name: astronomy\nkind: technical\nmax_reviews_per_session: 4\n"
        "item_types: [recall]\nsession_shape: teach-heavy\n")
    assert load_profile("astronomy").max_reviews_per_session == 4


def test_overlay_and_system_prompt():
    overlay = load_overlay("probability")
    assert "σ-algebra" in overlay
    sp = system_prompt(agenda(), overlay)
    assert "Session 1." in sp and "σ-algebra" in sp and "{overlay}" not in sp


def test_recovery_prompt():
    rp = recovery_prompt("the transcript", "goal: g")
    assert "the transcript" in rp and "goal: g" in rp
