import unittest
from icalendar import Calendar, Event

class TestIssue950(unittest.TestCase):
    def test_with_uid(self):
        # Setup: Create calendar and event with a specific UID
        cal = Calendar()
        event = Event()
        target_uid = 'student-test-uid-950'
        event.add('uid', target_uid)
        cal.add_component(event)
        
        # Action: Try to find the event using the new method
        # If the fix works, this should return a list containing the event
        found = cal.with_uid(target_uid)
        
        # Assert: Check we found exactly one item and it has the right UID
        self.assertEqual(len(found), 1, "Should find exactly one component")
        self.assertEqual(found[0].get('uid'), target_uid, "UID should match")

    def test_missing_uid(self):
        # Setup: Empty calendar
        cal = Calendar()
        
        # Action: Search for non-existent UID
        found = cal.with_uid('ghost-uid')
        
        # Assert: Should return empty list, not crash
        self.assertEqual(found, [], "Should return empty list for missing UID")
