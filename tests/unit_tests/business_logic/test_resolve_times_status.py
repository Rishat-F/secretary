import pytest

from src.business_logic.resolve_times_statuses import resolve_times_statuses


@pytest.mark.parametrize(
    "times_statuses,clicked_element,expected_result",
    [
        (
            ["not_selected", "not_selected", "not_selected"],
            1,
            ["edge", "not_selected", "not_selected"],
        ),
        (
            ["not_selected", "not_selected", "not_selected"],
            2,
            ["not_selected", "edge", "not_selected"],
        ),
        (
            ["not_selected", "not_selected", "not_selected"],
            3,
            ["not_selected", "not_selected", "edge"],
        ),
        (
            ["not_selected", "not_selected", "edge"],
            1,
            ["selected", "selected", "selected"],
        ),
        (
            ["not_selected", "not_selected", "edge"],
            2,
            ["not_selected", "selected", "selected"],
        ),
        (
            ["not_selected", "not_selected", "edge"],
            3,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["not_selected", "edge", "not_selected"],
            1,
            ["selected", "selected", "not_selected"],
        ),
        (
            ["not_selected", "edge", "not_selected"],
            2,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["not_selected", "edge", "not_selected"],
            3,
            ["not_selected", "selected", "selected"],
        ),
        (
            ["not_selected", "selected", "selected"],
            1,
            ["selected", "selected", "selected"],
        ),
        (
            ["not_selected", "selected", "selected"],
            2,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["not_selected", "selected", "selected"],
            3,
            ["not_selected", "edge", "not_selected"],
        ),
        (
            ["edge", "not_selected", "not_selected"],
            1,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["edge", "not_selected", "not_selected"],
            2,
            ["selected", "selected", "not_selected"],
        ),
        (
            ["edge", "not_selected", "not_selected"],
            3,
            ["selected", "selected", "selected"],
        ),
        (
            ["selected", "selected", "not_selected"],
            1,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "not_selected"],
            2,
            ["edge", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "not_selected"],
            3,
            ["selected", "selected", "selected"],
        ),
        (
            ["selected", "selected", "selected"],
            1,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected"],
            2,
            ["edge", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected"],
            3,
            ["selected", "selected", "not_selected"],
        ),
        (
            [
                "not_selected", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
            3,
            [
                "not_selected", "not_selected",
                "edge", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
        ),
        (
            [
                "not_selected", "not_selected",
                "edge", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
            6,
            [
                "not_selected", "not_selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
        ),
        (
            [
                "not_selected", "not_selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
            1,
            [
                "edge", "not_selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
        ),
        (
            [
                "edge", "not_selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
            4,
            [
                "selected", "selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
        ),
        (
            [
                "edge", "not_selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
            10,
            [
                "selected", "selected",
                "selected", "selected",
                "selected", "selected",
                "selected", "selected",
                "selected", "selected",
            ],
        ),
        (
            ["not_selected", "not_selected", "not_selected", "edge", "not_selected"],
            2,
            ["not_selected", "selected", "selected", "selected", "not_selected"],
        ),
        (
            ["selected", "selected", "not_selected", "edge", "not_selected"],
            2,
            ["selected", "selected", "selected", "selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            5,
            ["selected", "selected", "selected", "selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            4,
            ["selected", "selected", "selected", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            3,
            ["selected", "selected", "not_selected", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            2,
            ["edge", "not_selected", "not_selected", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            1,
            ["not_selected", "not_selected", "not_selected", "not_selected", "not_selected"],
        ),
    ],
)
def test_resolve_times_statuses(
    times_statuses,
    clicked_element,
    expected_result,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.business_logic.utils.TIMES_STATUSES_LEN", len(times_statuses))
    clicked_index = clicked_element - 1
    assert resolve_times_statuses(times_statuses, clicked_index) == expected_result


@pytest.mark.parametrize(
    "times_statuses",
    [
        ["not_selected", "not_selected", "selected"],
        ["not_selected", "edge", "edge"],
        ["not_selected", "edge", "selected"],
        ["not_selected", "selected", "not_selected"],
        ["not_selected", "selected", "edge"],
        ["edge", "not_selected", "edge"],
        ["edge", "not_selected", "selected"],
        ["edge", "edge", "not_selected"],
        ["edge", "edge", "edge"],
        ["edge", "edge", "selected"],
        ["edge", "selected", "not_selected"],
        ["edge", "selected", "edge"],
        ["edge", "selected", "selected"],
        ["selected", "not_selected", "not_selected"],
        ["selected", "not_selected", "edge"],
        ["selected", "not_selected", "selected"],
        ["selected", "edge", "not_selected"],
        ["selected", "edge", "edge"],
        ["selected", "edge", "selected"],
        ["selected", "selected", "edge"],
        ["not_selected", "finish", "not_selected"],
        ["selected", "selected", "selected", "selected"],
    ],
)
def test_resolve_times_statuses_raises_assertion_error(
    times_statuses,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.business_logic.utils.TIMES_STATUSES_LEN", 3)
    with pytest.raises(AssertionError):
        resolve_times_statuses(times_statuses, clicked_index=1)
