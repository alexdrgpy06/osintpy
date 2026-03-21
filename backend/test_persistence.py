import unittest
import os
import sqlite3
import tempfile
from agents.persistence import ProfilePersistenceAgent

class TestProfilePersistenceAgent(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and file for the SQLite database
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.test_dir.name, "test_profiles.db")

        # Override the DB_PATH in ProfilePersistenceAgent for testing
        self.original_db_path = ProfilePersistenceAgent.DB_PATH
        ProfilePersistenceAgent.DB_PATH = self.db_path

    def tearDown(self):
        # Restore the original DB_PATH
        ProfilePersistenceAgent.DB_PATH = self.original_db_path
        # Clean up the temporary directory
        self.test_dir.cleanup()

    def test_save_feedback(self):
        profile_id = "test_profile_123"
        field = "email"
        incorrect_value = "wrong@example.com"
        correct_value = "correct@example.com"
        comment = "Typo in email address"

        ProfilePersistenceAgent.save_feedback(
            profile_id=profile_id,
            field=field,
            incorrect_value=incorrect_value,
            correct_value=correct_value,
            comment=comment
        )

        # Connect to the test database to verify the insertion
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT profile_id, field, incorrect_value, correct_value, comment, status FROM feedback WHERE profile_id = ?", (profile_id,))
        row = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(row, "Feedback was not saved to the database")
        self.assertEqual(row[0], profile_id)
        self.assertEqual(row[1], field)
        self.assertEqual(row[2], incorrect_value)
        self.assertEqual(row[3], correct_value)
        self.assertEqual(row[4], comment)
        self.assertEqual(row[5], "pending") # Default status

if __name__ == '__main__':
    unittest.main()
