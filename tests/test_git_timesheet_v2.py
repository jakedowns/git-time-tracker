import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
sys.path.insert(0, '..')
import git_timesheet_v2  # assuming your script is named git_timesheet_v2.py

class TestGitTimesheetV2(unittest.TestCase):
    @patch('subprocess.check_output')
    def test_git_timesheet_v2(self, mock_output):
        # Mock the output of the subprocess.check_output call
        mock_output.return_value = '\n'.join([
            'commit_hash@@@2021-12-31 10:00:00@@@commit_msg@@@other_author',
            'commit_hash@@@2022-01-01 10:00:00@@@commit_msg@@@mock_author',
            'commit_hash@@@2022-01-01 11:00:00@@@commit_msg@@@mock_author',
            'commit_hash@@@2023-01-01 10:00:00@@@commit_msg@@@mock_author'
        ])

        # Verify that subprocess.check_output was called with the expected arguments
        mock_output.assert_called_once()  # or assert_called() if it's called more than once
        
        # Call the main function of your script
        git_timesheet_v2.main(['-f', 'mock_author', '-s', '2022-01-01', '-e', '2022-12-31'])
        
        # Assert that the total estimated hours is correct
        self.assertEqual(git_timesheet_v2.total_time_worked, 2)