import pytest

from src.business_logic.resolve_times_statuses.utils import (
    MINIMAL_TIMES_STATUSES_LEN,
    TIMES_STATUSES_LEN,
    _get_duration_multiplier_by_times_statues,
    _get_times_statuses_len,
    _no_isolated_selected,
    _no_selected_edge_combination,
    _no_edge_selected_combination,
    check_clicked_index_assertions,
    check_times_statuses_assertions,
    get_initial_times_statuses,
    get_times_statuses_view,
)


def test_times_statuses_len():
    assert TIMES_STATUSES_LEN == 49


def test_minimal_times_statuses_len():
    assert MINIMAL_TIMES_STATUSES_LEN == 3


def test_get_initial_times_statuses():
    assert get_initial_times_statuses() == ["not_selected"] * 49


@pytest.mark.parametrize(
    "duration_multiplier,expected_result",
    [
        (720, 3),
        (480, 4),
        (360, 5),
        (240, 7),
        (120, 13),
        (60, 25),
        (30, 49),
        (20, 73),
        (15, 97),
        (10, 145),
        (5, 289),
    ],
)
def test__get_times_statuses_len(duration_multiplier, expected_result):
    assert _get_times_statuses_len(duration_multiplier) == expected_result


@pytest.mark.parametrize(
    "times_statuses_len,expected_result",
    [
        (3, 720),
        (4, 480),
        (5, 360),
        (7, 240),
        (13, 120),
        (25, 60),
        (49, 30),
        (73, 20),
        (97, 15),
        (145, 10),
        (289, 5),
    ],
)
def test__get_duration_multiplier_by_times_statues(times_statuses_len, expected_result):
    assert _get_duration_multiplier_by_times_statues(times_statuses_len) == expected_result


@pytest.mark.parametrize(
    "times_statuses,expected_result",
    [
        (["not_selected", "not_selected", "not_selected"], True),
        (["not_selected", "not_selected", "selected"], False),
        (["not_selected", "not_selected", "edge"], True),
        (["not_selected", "selected", "not_selected"], False),
        (["not_selected", "selected", "selected"], True),
        (["not_selected", "selected", "edge"], False),
        (["not_selected", "edge", "not_selected"], True),
        (["not_selected", "edge", "selected"], False),
        (["not_selected", "edge", "edge"], True),
        (["selected", "not_selected", "not_selected"], False),
        (["selected", "not_selected", "selected"], False),
        (["selected", "not_selected", "edge"], False),
        (["selected", "selected", "not_selected"], True),
        (["selected", "selected", "selected"], True),
        (["selected", "selected", "edge"], True),
        (["selected", "edge", "not_selected"], False),
        (["selected", "edge", "selected"], False),
        (["selected", "edge", "edge"], False),
        (["edge", "not_selected", "not_selected"], True),
        (["edge", "not_selected", "selected"], False),
        (["edge", "not_selected", "edge"], True),
        (["edge", "selected", "not_selected"], False),
        (["edge", "selected", "selected"], True),
        (["edge", "selected", "edge"], False),
        (["edge", "edge", "not_selected"], True),
        (["edge", "edge", "selected"], False),
        (["edge", "edge", "edge"], True),
        (
            [
                "not_selected",
                "not_selected",
                "not_selected",
                "not_selected",
                "not_selected",
                "not_selected",
                "not_selected",
            ],
            True,
        ),
        (
            [
                "selected",
                "selected",
                "selected",
                "selected",
                "selected",
                "selected",
                "selected",
            ],
            True,
        ),
        (
            [
                "edge",
                "not_selected",
                "selected",
                "selected",
                "not_selected",
                "selected",
                "not_selected",
            ],
            False,
        ),
        (
            [
                "not_seledted",
                "selected",
                "not_selected",
                "selected",
                "not_selected",
                "selected",
                "not_selected",
            ],
            False,
        ),
        (
            [
                "selected",
                "not_seledted",
                "selected",
                "not_selected",
                "selected",
                "not_selected",
                "selected",
                "not_selected",
                "selected",
            ],
            False,
        ),
    ],
)
def test__no_isolated_selected(times_statuses, expected_result):
    assert _no_isolated_selected(times_statuses) is expected_result


@pytest.mark.parametrize(
    "times_statuses,expected_result",
    [
        (["not_selected", "not_selected", "not_selected"], True),
        (["not_selected", "not_selected", "selected"], True),
        (["not_selected", "not_selected", "edge"], True),
        (["not_selected", "selected", "not_selected"], True),
        (["not_selected", "selected", "selected"], True),
        (["not_selected", "selected", "edge"], True),
        (["not_selected", "edge", "not_selected"], True),
        (["not_selected", "edge", "selected"], False),
        (["not_selected", "edge", "edge"], True),
        (["selected", "not_selected", "not_selected"], True),
        (["selected", "not_selected", "selected"], True),
        (["selected", "not_selected", "edge"], True),
        (["selected", "selected", "not_selected"], True),
        (["selected", "selected", "selected"], True),
        (["selected", "selected", "edge"], True),
        (["selected", "edge", "not_selected"], True),
        (["selected", "edge", "selected"], False),
        (["selected", "edge", "edge"], True),
        (["edge", "not_selected", "not_selected"], True),
        (["edge", "not_selected", "selected"], True),
        (["edge", "not_selected", "edge"], True),
        (["edge", "selected", "not_selected"], False),
        (["edge", "selected", "selected"], False),
        (["edge", "selected", "edge"], False),
        (["edge", "edge", "not_selected"], True),
        (["edge", "edge", "selected"], False),
        (["edge", "edge", "edge"], True),
    ],
)
def test__no_edge_selected_combination(times_statuses, expected_result):
    assert _no_edge_selected_combination(times_statuses) is expected_result


@pytest.mark.parametrize(
    "times_statuses,expected_result",
    [
        (["not_selected", "not_selected", "not_selected"], True),
        (["not_selected", "not_selected", "selected"], True),
        (["not_selected", "not_selected", "edge"], True),
        (["not_selected", "selected", "not_selected"], True),
        (["not_selected", "selected", "selected"], True),
        (["not_selected", "selected", "edge"], False),
        (["not_selected", "edge", "not_selected"], True),
        (["not_selected", "edge", "selected"], True),
        (["not_selected", "edge", "edge"], True),
        (["selected", "not_selected", "not_selected"], True),
        (["selected", "not_selected", "selected"], True),
        (["selected", "not_selected", "edge"], True),
        (["selected", "selected", "not_selected"], True),
        (["selected", "selected", "selected"], True),
        (["selected", "selected", "edge"], False),
        (["selected", "edge", "not_selected"], False),
        (["selected", "edge", "selected"], False),
        (["selected", "edge", "edge"], False),
        (["edge", "not_selected", "not_selected"], True),
        (["edge", "not_selected", "selected"], True),
        (["edge", "not_selected", "edge"], True),
        (["edge", "selected", "not_selected"], True),
        (["edge", "selected", "selected"], True),
        (["edge", "selected", "edge"], False),
        (["edge", "edge", "not_selected"], True),
        (["edge", "edge", "selected"], True),
        (["edge", "edge", "edge"], True),
    ],
)
def test__no_selected_edge_combination(times_statuses, expected_result):
    assert _no_selected_edge_combination(times_statuses) is expected_result


@pytest.mark.parametrize(
    "times_statuses",
    [
        ["not_selected", "not_selected", "not_selected"],
        ["not_selected", "not_selected", "edge"],
        ["not_selected", "selected", "selected"],
        ["not_selected", "edge", "not_selected"],
        ["selected", "selected", "not_selected"],
        ["selected", "selected", "selected"],
        ["edge", "not_selected", "not_selected"],
        [
            "not_selected",
            "edge",
            "not_selected",
            "selected",
            "selected",
            "not_selected",
            "selected",
            "selected",
            "not_selected",
        ],
    ],
)
def test_check_times_statuses_assertions_passes(
    times_statuses,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.business_logic.resolve_times_statuses.utils.TIMES_STATUSES_LEN", len(times_statuses))
    assert check_times_statuses_assertions(times_statuses) is None


@pytest.mark.parametrize(
    "times_statuses",
    [
        ["not_selected", "not_selected", "selected"],
        ["not_selected", "selected", "not_selected"],
        ["not_selected", "selected", "edge"],
        ["not_selected", "edge", "selected"],
        ["not_selected", "edge", "edge"],
        ["selected", "not_selected", "not_selected"],
        ["selected", "not_selected", "selected"],
        ["selected", "not_selected", "edge"],
        ["selected", "selected", "edge"],
        ["selected", "edge", "not_selected"],
        ["selected", "edge", "selected"],
        ["selected", "edge", "edge"],
        ["edge", "not_selected", "selected"],
        ["edge", "not_selected", "edge"],
        ["edge", "selected", "not_selected"],
        ["edge", "selected", "selected"],
        ["edge", "selected", "edge"],
        ["edge", "edge", "not_selected"],
        ["edge", "edge", "selected"],
        ["edge", "edge", "edge"],
        ["not_selected", "not_selected", "not_selected", "not_selected"],
        ["not_selected", "finish", "not_selected"],
    ],
)
def test_check_times_statuses_assertions_raises_assertion_error(
    times_statuses,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.business_logic.resolve_times_statuses.utils.TIMES_STATUSES_LEN", 3)
    with pytest.raises(AssertionError):
        check_times_statuses_assertions(times_statuses)


@pytest.mark.parametrize("clicked_index", [0, 1, 2])
def test_check_clicked_index_assertions_passes(
    clicked_index,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.business_logic.resolve_times_statuses.utils.TIMES_STATUSES_LEN", 3)
    assert check_clicked_index_assertions(clicked_index) is None


@pytest.mark.parametrize("clicked_index", [-10, -1, 3, 5, 10])
def test_check_clicked_index_assertions_raises_assertion_error(
    clicked_index,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.business_logic.resolve_times_statuses.utils.TIMES_STATUSES_LEN", 3)
    with pytest.raises(AssertionError):
        check_clicked_index_assertions(clicked_index)


@pytest.mark.parametrize(
    "times_statuses,expected_result",
    [
        (
            ["not_selected", "not_selected", "not_selected", "not_selected"],
            "Рабочие часы не выбраны",
        ),
        (
            ["edge", "not_selected", "not_selected", "not_selected"],
            "Выбранные рабочие часы:\n00:00-...",
        ),
        (
            ["not_selected", "not_selected", "not_selected", "edge"],
            "Выбранные рабочие часы:\n...-00:00",
        ),
        (
            ["not_selected", "edge", "not_selected", "not_selected"],
            "Выбранные рабочие часы:\n...-08:00-...",
        ),
        (
            ["selected", "selected", "selected"],
            "Выбранные рабочие часы:\n00:00-00:00",
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            "Выбранные рабочие часы:\n00:00-00:00",
        ),
        (
            ["edge", "not_selected", "selected", "selected", "not_selected"],
            "Выбранные рабочие часы:\n00:00-...\n12:00-18:00",
        ),
        (
            ["selected", "selected", "not_selected", "edge", "not_selected"],
            "Выбранные рабочие часы:\n00:00-06:00\n...-18:00-...",
        ),
        (
            ["selected", "selected", "not_selected", "selected", "selected"],
            "Выбранные рабочие часы:\n00:00-06:00\n18:00-00:00",
        ),
        (
            [
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected",
            ],
            "Выбранные рабочие часы:\n00:00-00:00",
        ),
        (
            [
                "selected", "selected", "not_selected", "not_selected",
                "selected", "selected", "selected", "not_selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected",
            ],
            "Выбранные рабочие часы:\n00:00-00:30\n02:00-03:00\n04:00-06:30\n16:00-00:00",
        ),
        (
            [
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "not_selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected",
            ],
            "Выбранные рабочие часы:\n08:00-12:00\n13:00-17:00",
        ),
    ],
)
def test_get_times_statuses_view(times_statuses, expected_result):
    assert get_times_statuses_view(times_statuses) == expected_result
