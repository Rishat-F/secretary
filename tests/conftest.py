from pytest import MonkeyPatch


monkeypatch = MonkeyPatch()
monkeypatch.setenv("TIMEZONE", "Europe/Moscow")
