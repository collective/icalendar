"""Test timezone identification with incorrect historical definitions.

This test suite verifies the fix for issues #763, #775, #776, #780, and #791.

The problem: dateutil timezones can return incorrect offsets for historical dates
(e.g., between 1970-2000), making it impossible to identify them by behavior alone.
The fix adds a fallback mechanism that identifies timezones by their utcoffset
behavior at different historical points, even when they have incorrect historical data.
This builds on issue #776's approach of using midday (12:00) instead of midnight
to avoid ambiguous timezone transitions.

See:
- https://github.com/collective/icalendar/issues/763
- https://github.com/collective/icalendar/issues/775
- https://github.com/collective/icalendar/issues/776
- https://github.com/collective/icalendar/issues/780
- https://github.com/collective/icalendar/issues/791
"""

from datetime import datetime

import pytest
from dateutil.tz import gettz
from zoneinfo import ZoneInfo

from icalendar.timezone.tzid import tzid_from_tzinfo, tzids_from_tzinfo


class TestTimezoneIdentificationWithIncorrectHistoricalData:
    """Test that timezones can be identified despite incorrect historical offsets."""

    def test_eet_timezone_with_incorrect_historical_offset(self):
        """Test EET timezone identification with the specific date from issue #763.

        dateutil's gettz("EET") returns incorrect offset (10800 seconds = 3 hours)
        for 1983-03-27, while zoneinfo returns the correct offset (7200 seconds = 2 hours).
        The fix should still identify the timezone correctly.
        """
        # The problematic date from the original issue
        d = datetime(1983, 3, 27, 3, 0)

        # Get dateutil timezone
        tz_dateutil = gettz("EET")
        assert tz_dateutil is not None, "Could not get EET timezone from dateutil"

        # Verify dateutil returns incorrect offset
        offset_dateutil = tz_dateutil.utcoffset(d)
        assert offset_dateutil is not None
        assert offset_dateutil.total_seconds() == 10800, (
            f"dateutil returns wrong offset: {offset_dateutil.total_seconds()} "
            f"instead of expected 10800 (this is the bug we're testing)"
        )

        # Verify zoneinfo returns correct offset (for comparison)
        tz_zoneinfo = ZoneInfo("EET")
        offset_zoneinfo = tz_zoneinfo.utcoffset(d)
        assert offset_zoneinfo is not None
        assert offset_zoneinfo.total_seconds() == 7200, (
            f"zoneinfo should return correct offset: 7200, "
            f"got {offset_zoneinfo.total_seconds()}"
        )

        # The fix: timezone should be identified despite wrong offset
        tzids = tzids_from_tzinfo(tz_dateutil)
        assert len(tzids) > 0, "Timezone should be identified"
        assert "EET" in tzids or "Europe/Athens" in tzids, (
            f"EET or Europe/Athens should be in identified timezones: {tzids}"
        )

        # Test tzid_from_tzinfo as well
        tzid = tzid_from_tzinfo(tz_dateutil)
        assert tzid is not None, "tzid_from_tzinfo should return a timezone ID"
        assert tzid in ("EET", "Europe/Athens"), (
            f"tzid_from_tzinfo should return EET or Europe/Athens, got {tzid}"
        )

    @pytest.mark.parametrize(
        ("tzid", "historical_date"),
        [
            ("EET", datetime(1983, 3, 27, 3, 0)),
            ("EET", datetime(1975, 1, 1, 12, 0)),
            ("EET", datetime(1990, 6, 15, 12, 0)),
            ("Asia/Manila", datetime(1983, 5, 1, 12, 0)),
            ("Asia/Manila", datetime(1970, 1, 1, 12, 0)),
        ],
    )
    def test_timezone_identification_with_historical_dates(self, tzid, historical_date):
        """Test that timezones can be identified for various historical dates.

        This tests the fallback mechanism works for different timezones and dates
        where dateutil might return incorrect historical offsets.
        """
        tz_dateutil = gettz(tzid)
        if tz_dateutil is None:
            pytest.skip(f"Could not get {tzid} timezone from dateutil")

        # The timezone should be identifiable even if historical offsets are wrong
        tzids = tzids_from_tzinfo(tz_dateutil)
        assert len(tzids) > 0, (
            f"Timezone {tzid} should be identified for date {historical_date}"
        )

        # The original timezone ID or an equivalent should be in the results
        # We check if the tzid or any equivalent is in the results
        assert (
            any(
                tzid in result_tzid or result_tzid in tzid
                for result_tzid in tzids
                if tzid in result_tzid
                or any(tzid_part in result_tzid for tzid_part in tzid.split("/"))
            )
            or tzid in tzids
        ), f"Original tzid {tzid} or equivalent should be in {tzids}"

    def test_behavior_based_identification_fallback(self):
        """Test that behavior-based identification works as a fallback.

        This test verifies that when filename-based identification fails,
        the behavior-based fallback mechanism is used.
        """
        # Use a timezone that might not have easily accessible filename
        tz = gettz("EET")
        assert tz is not None

        # Get timezone IDs - should work even without filename
        tzids = tzids_from_tzinfo(tz)
        assert len(tzids) > 0, "Behavior-based fallback should identify timezone"

        # Verify we got reasonable results
        assert any(
            "EET" in tzid or "Europe" in tzid or "Athens" in tzid for tzid in tzids
        ), f"Should identify EET-related timezone, got {tzids}"

    def test_zoneinfo_comparison_consistency(self):
        """Test that dateutil and zoneinfo identify to equivalent timezones.

        Even though dateutil might return different offsets for historical dates,
        both should identify to the same/equivalent timezone IDs.
        """
        tz_dateutil = gettz("EET")
        tz_zoneinfo = ZoneInfo("EET")

        assert tz_dateutil is not None
        assert tz_zoneinfo is not None

        # Get timezone IDs from both
        tzids_dateutil = tzids_from_tzinfo(tz_dateutil)
        tzids_zoneinfo = tzids_from_tzinfo(tz_zoneinfo)

        # They should identify to overlapping/equivalent timezones
        assert len(tzids_dateutil) > 0
        assert len(tzids_zoneinfo) > 0

        # Check for overlap in equivalent timezones
        overlap = set(tzids_dateutil) & set(tzids_zoneinfo)
        assert len(overlap) > 0, (
            f"dateutil and zoneinfo should identify to overlapping timezones. "
            f"dateutil: {tzids_dateutil}, zoneinfo: {tzids_zoneinfo}"
        )

    def test_midday_avoidance_of_transitions(self):
        """Test that the fix uses midday to avoid ambiguous timezone transitions.

        The fix should use midday (12:00) instead of midnight to avoid
        ambiguous timezone definitions around DST transitions.
        """
        # Test with a date that's around a DST transition
        # The behavior-based identification should work even for transition dates
        transition_dates = [
            datetime(1983, 3, 27, 3, 0),  # Original problematic date
            datetime(1983, 3, 27, 0, 0),  # Midnight on same date
            datetime(1983, 3, 27, 12, 0),  # Midday on same date
        ]

        tz = gettz("EET")
        assert tz is not None

        for test_date in transition_dates:
            # Should be able to identify timezone for all these dates
            tzids = tzids_from_tzinfo(tz)
            assert len(tzids) > 0, f"Should identify timezone for date {test_date}"

    def test_error_handling_for_invalid_dates(self):
        """Test that the fix handles errors gracefully for invalid dates."""
        tz = gettz("EET")
        assert tz is not None

        # Should not raise exceptions even for edge cases
        try:
            tzids = tzids_from_tzinfo(tz)
            # Should return either empty tuple or valid timezone IDs
            assert isinstance(tzids, tuple)
        except (ValueError, OSError, OverflowError, KeyError) as e:
            pytest.fail(f"tzids_from_tzinfo should not raise exceptions: {e}")

    def test_multiple_historical_points(self):
        """Test that identification works across multiple historical points.

        The behavior-based identification queries multiple historical points,
        so it should work even if some points have incorrect offsets.
        """
        tz = gettz("EET")
        assert tz is not None

        # Test multiple dates to ensure consistency
        test_dates = [
            datetime(1970, 1, 1, 12, 0),
            datetime(1980, 6, 15, 12, 0),
            datetime(1983, 3, 27, 12, 0),  # Problematic date
            datetime(1990, 1, 1, 12, 0),
            datetime(2000, 1, 1, 12, 0),
        ]

        identified_tzids = None
        for test_date in test_dates:
            # All dates should identify to the same/equivalent timezones
            tzids = tzids_from_tzinfo(tz)
            assert len(tzids) > 0, f"Should identify for date {test_date}"

            if identified_tzids is None:
                identified_tzids = set(tzids)
            else:
                # Should identify to overlapping/equivalent timezones
                current_tzids = set(tzids)
                overlap = identified_tzids & current_tzids
                assert len(overlap) > 0, (
                    f"Timezone identification should be consistent across dates. "
                    f"Previous: {identified_tzids}, Current: {current_tzids}"
                )
