from seba.session.loader import load_overlay, load_profile


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


def test_overlay():
    overlay = load_overlay("probability")
    assert "σ-algebra" in overlay
    assert load_overlay("nonexistent") == ""
