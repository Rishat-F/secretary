import pytest

from src.business_logic.resolve_days_statuses.utils import get_selected_days_view


@pytest.mark.parametrize(
    "days,expected_result",
    [
        ([], ""),
        ([1], "1"),
        ([25], "25"),
        ([2, 8], "2, 8"),
        ([1, 2], "1-2"),
        ([1, 2, 3, 4, 5], "1-5"),
        ([1, 4, 5, 6], "1, 4-6"),
        ([1, 5, 6], "1, 5-6"),
        ([1, 3, 5, 6, 9, 10, 11, 12, 22, 23, 24], "1, 3, 5-6, 9-12, 22-24"),
    ]
)
def test_get_selected_days_view(days, expected_result):
    assert get_selected_days_view(days) == expected_result
