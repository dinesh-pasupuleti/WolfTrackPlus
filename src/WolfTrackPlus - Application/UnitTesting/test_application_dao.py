import unittest
from unittest.mock import MagicMock
import sys
import os

currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from DAO.application_dao import application_dao

class TestApplicationDAO(unittest.TestCase):

    def setUp(self):
        self.app_dao = application_dao()
        self.app_dao._application_dao__db = MagicMock()

    def test_add_application_valid(self):
        email = 'user@example.com'
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], None, [(1,)], None, [(1,)], True
        ]
        result = self.app_dao.add_application(
            email, 'Company', 'Location', 'Job', 50000,
            'username', 'password', 'question', 'answer',
            'notes', '2023-10-31', 'Applied', b'Resume data'
        )
        self.assertTrue(result)

    def test_add_application_missing_resume(self):
        email = 'user@example.com'
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(2,)], None, [(2,)], None, [(2,)], True
        ]
        result = self.app_dao.add_application(
            email, 'Company', 'Location', 'Job', 60000,
            'username', 'password', 'question', 'answer',
            'notes', '2023-10-31', 'Pending', None
        )
        self.assertTrue(result)

    def test_get_application_by_status(self):
        email = 'user@example.com'
        status = 'Applied'
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], [
                ['Company A', 'Applied', '2023-10-31', 1, 'Location A', 'Job A', 50000, 'notes A'],
                ['Company B', 'Applied', '2023-10-30', 2, 'Location B', 'Job B', 60000, 'notes B']
            ]
        ]
        result = self.app_dao.get_application(email, status)
        self.assertEqual(len(result), 2)

    def test_get_resume_existing_user(self):
        email = 'user@example.com'
        encoded_resume = 'UmVzdW1lIGRhdGE='
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], [(encoded_resume,)]
        ]
        result = self.app_dao.get_resume(email)
        self.assertEqual(result, b'Resume data')

    def test_update_application_valid(self):
        application_id = 1
        self.app_dao._application_dao__db.run_query.side_effect = [
            [('Company Old', 1, 'Role Old', 1)], None, [(2,)], None, [(2,)], True
        ]
        result = self.app_dao.update_application(
            'Company New', 'Location New', 'Role New', 70000,
            'username', 'password', 'question', 'answer',
            'notes', '2023-10-31', 'Interview', application_id
        )
        self.assertTrue(result)

    def test_delete_application(self):
        application_id = 1
        self.app_dao._application_dao__db.run_query.return_value = True
        result = self.app_dao.delete_application(application_id)
        self.assertTrue(result)

    def test_change_status(self):
        application_id = 1
        new_status = 'Offer'
        self.app_dao._application_dao__db.run_query.return_value = True
        result = self.app_dao.change_status(application_id, new_status)
        self.assertTrue(result)

    def test_get_locations_for_application(self):
        email = 'user@example.com'
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], [('Location A',), ('Location B',)]
        ]
        result = self.app_dao.get_locations_for_application(email)
        self.assertEqual(result, ['Location A', 'Location B'])

    def test_get_company_names_for_application(self):
        email = 'user@example.com'
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], [('Company A',), ('Company B',)]
        ]
        result = self.app_dao.get_company_names_for_application(email)
        self.assertEqual(result, ['Company A', 'Company B'])

    def test_add_application_invalid_email(self):
        email = 'invalid@example.com'
        self.app_dao._application_dao__db.run_query.side_effect = [
            []
        ]
        with self.assertRaises(IndexError):
            self.app_dao.add_application(
                email, 'Company', 'Location', 'Job', 50000,
                'username', 'password', 'question', 'answer',
                'notes', '2023-10-31', 'Applied', b'Resume data'
            )

    def test_add_application_missing_mandatory_fields(self):
        email = 'user@example.com'
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)]
        ]
        with self.assertRaises(TypeError):
            self.app_dao.add_application(
                email, None, 'Location', 'Job', 50000,
                'username', 'password', 'question', 'answer',
                'notes', '2023-10-31', 'Applied', b'Resume data'
            )

    def test_get_application_no_results(self):
        email = 'user@example.com'
        status = 'Nonexistent'
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], []
        ]
        result = self.app_dao.get_application(email, status)
        self.assertEqual(len(result), 0)

    def test_get_resume_no_resume(self):
        email = 'user@example.com'
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], []
        ]
        result = self.app_dao.get_resume(email)
        self.assertIsNone(result)

    def test_update_application_nonexistent(self):
        application_id = 999
        self.app_dao._application_dao__db.run_query.side_effect = [
            []
        ]
        with self.assertRaises(IndexError):
            self.app_dao.update_application(
                'Company', 'Location', 'Job', 50000,
                'username', 'password', 'question', 'answer',
                'notes', '2023-10-31', 'Applied', application_id
            )

    def test_change_status_invalid_application_id(self):
        application_id = 999
        self.app_dao._application_dao__db.run_query.return_value = True
        result = self.app_dao.change_status(application_id, 'Interview')
        self.assertTrue(result)

    def test_delete_application_nonexistent(self):
        application_id = 999
        self.app_dao._application_dao__db.run_query.return_value = True
        result = self.app_dao.delete_application(application_id)
        self.assertTrue(result)

    def test_add_application_sql_injection(self):
        email = 'user@example.com'
        malicious_input = "'; DROP TABLE users;--"
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], None, [(1,)], None, [(1,)], True
        ]
        result = self.app_dao.add_application(
            email, malicious_input, 'Location', 'Job', 50000,
            'username', 'password', 'question', 'answer',
            'notes', '2023-10-31', 'Applied', None
        )
        self.assertTrue(result)

    def test_add_application_large_input(self):
        email = 'user@example.com'
        large_text = 'A' * 10000
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], None, [(1,)], None, [(1,)], True
        ]
        result = self.app_dao.add_application(
            email, large_text, 'Location', 'Job', 50000,
            'username', 'password', 'question', 'answer',
            'notes', '2023-10-31', 'Applied', None
        )
        self.assertTrue(result)

    def test_add_application_negative_salary(self):
        email = 'user@example.com'
        salary = -50000
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], None, [(1,)], None, [(1,)], True
        ]
        result = self.app_dao.add_application(
            email, 'Company', 'Location', 'Job', salary,
            'username', 'password', 'question', 'answer',
            'notes', '2023-10-31', 'Applied', None
        )
        self.assertTrue(result)

    def test_get_application_invalid_email(self):
        email = 'invalidemail'
        self.app_dao._application_dao__db.run_query.side_effect = [
            []
        ]
        with self.assertRaises(IndexError):
            self.app_dao.get_application(email, '')

    def test_add_application_invalid_date(self):
        email = 'user@example.com'
        invalid_date = '31-10-2023'
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], None, [(1,)], None, [(1,)], True
        ]
        result = self.app_dao.add_application(
            email, 'Company', 'Location', 'Job', 50000,
            'username', 'password', 'question', 'answer',
            'notes', invalid_date, 'Applied', None
        )
        self.assertTrue(result)

    def test_get_locations_for_application_no_results(self):
        email = 'user@example.com'
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], []
        ]
        result = self.app_dao.get_locations_for_application(email)
        self.assertEqual(result, [])

    def test_get_company_names_for_application_no_results(self):
        email = 'user@example.com'
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], []
        ]
        result = self.app_dao.get_company_names_for_application(email)
        self.assertEqual(result, [])

    def test_add_application_null_optional_fields(self):
        email = 'user@example.com'
        notes = None
        resume = None
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], None, [(1,)], None, [(1,)], True
        ]
        adjusted_notes = notes if notes is not None else ''
        result = self.app_dao.add_application(
            email, 'Company', 'Location', 'Job', 50000,
            'username', 'password', 'question', 'answer',
            adjusted_notes, '2023-10-31', 'Applied', resume
        )
        self.assertTrue(result)

    def test_get_application_empty_status(self):
        email = 'user@example.com'
        status = ''
        self.app_dao._application_dao__db.run_query.side_effect = [
            [(1,)], [
                ['Company A', 'Applied', '2023-10-31', 1, 'Location A', 'Job A', 50000, 'notes A']
            ]
        ]
        result = self.app_dao.get_application(email, status)
        self.assertEqual(len(result), 1)

    def test_get_resume_nonexistent_user(self):
        email = 'nonexistent@example.com'
        self.app_dao._application_dao__db.run_query.side_effect = [
            []
        ]
        result = self.app_dao.get_resume(email)
        self.assertIsNone(result)

    def test_delete_application_invalid_id(self):
        application_id = 'invalid'
        self.app_dao._application_dao__db.run_query.return_value = True
        result = self.app_dao.delete_application(application_id)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
