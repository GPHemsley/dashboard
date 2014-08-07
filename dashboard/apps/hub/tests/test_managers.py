import json

from django.test import TestCase

from ..models import State 

class TestStateManager(TestCase):
    fixtures = [
        'test_state_status',
    ]

    def test_status_json(self):
        status_json = State.objects.status_json() 
        statuses = json.loads(status_json)
        self.assertEqual(len(statuses), 2)
        status = statuses[0]
        self.assertEqual(status['postal'], "IL")
        self.assertEqual(status['name'], "Illinois")
        self.assertEqual(status['metadata_status'], "partial")
        self.assertEqual(len(status['volunteers']), 1)
        self.assertEqual(status['volunteers'][0]['full_name'], "Aaliyah Clay")
