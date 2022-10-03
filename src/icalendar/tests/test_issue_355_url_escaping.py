"""Tests for Issue 355.

see https://github.com/collective/icalendar/issues/355
"""

def test_facebook_link_is_correctly_parsed(events):
    """The facebook link must not be damaged.

    see https://github.com/collective/icalendar/pull/356#issuecomment-1222626128
    """
    events.issue_355_url_escaping["DESCRIPTION"] == "https://www.facebook.com/events/756119502186737/?acontext=%7B%22source%22%3A5%2C%22action_history%22%3A[%7B%22surface%22%3A%22page%22%2C%22mechanism%22%3A%22main_list%22%2C%22extra_data%22%3A%22%5C%22[]%5C%22%22%7D]%2C%22has_source%22%3Atrue%7D"