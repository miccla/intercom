import os
import tempfile
import unittest

from intercom_inviter.constants import EARTH_RADIUS
from intercom_inviter.inviter import Inviter


class TestInviter(unittest.TestCase):
    def test_is_valid_lat_long(self):
        inviter = Inviter()
        actual = inviter._is_valid_coordinates((91, 0,))
        self.assertFalse(actual)
        actual = inviter._is_valid_coordinates((0, -181,))
        self.assertFalse(actual)
        actual = inviter._is_valid_coordinates((0, 0,))
        self.assertTrue(actual)
        with self.assertRaises(TypeError):
            inviter._is_valid_coordinates(('test', 0,))

    def test_get_customers_from_file_ok(self):
        expected = {"latitude": "51.92893", "user_id": 1, "name": "Alice Cahill", "longitude": "-10.27699",
                    'coordinates': (51.92893, -10.27699,)}
        inviter = Inviter()
        customer_test = '{"latitude": "51.92893", "user_id": 1, "name": "Alice Cahill", "longitude": "-10.27699"}'
        with tempfile.TemporaryDirectory() as temp_dir:
            f_path = os.path.join(temp_dir, 'customers.txt')
            with open(f_path, 'w') as f:
                f.write(customer_test)
            with open(f_path, 'r') as f:
                actual = inviter._get_customers_from_file(f).__next__()
            self.assertEqual(actual, expected)

    def test_get_customers_from_file_with_bad_json(self):
        inviter = Inviter()
        customer_test = '{zzzzz"latitude": "0", "user_id": 1, "name": "Alice Cahill", "longitude": "0"}'
        with tempfile.TemporaryDirectory() as temp_dir:
            f_path = os.path.join(temp_dir, 'customers.txt')
            with open(f_path, 'w') as f:
                f.write(customer_test)
            with self.assertRaises(StopIteration):
                with open(f_path, 'r') as f:
                    inviter._get_customers_from_file(f).__next__()

    def test_get_customers_from_file_with_invalid_lat_long(self):
        inviter = Inviter()
        customer_test = '{"latitude": "-91", "user_id": 1, "name": "Alice Cahill", "longitude": "0"}'
        with tempfile.TemporaryDirectory() as temp_dir:
            f_path = os.path.join(temp_dir, 'customers.txt')
            with open(f_path, 'w') as f:
                f.write(customer_test)
            with self.assertRaises(StopIteration):
                with open(f_path, 'r') as f:
                    inviter._get_customers_from_file(f).__next__()

    def test__are_two_points_within_km_ok(self):
        inviter = Inviter()
        point_a = (53.339428, -6.257664,)  # constants.DUBLIN_OFFICE_COORDINATES
        point_b = (53.339280, -6.281314,)  # Facebook Dublin
        self.assertTrue(inviter._is_two_points_within_km(point_a, point_b, 100))
        self.assertTrue(inviter._is_two_points_within_km(point_a, point_b, 10))
        self.assertFalse(inviter._is_two_points_within_km(point_a, point_b, 1))
        self.assertFalse(inviter._is_two_points_within_km(point_a, point_b, -100))

    def test__get_customers_ok(self):
        expected = [
            {"latitude": "0", "user_id": 1, "name": "a", "longitude": "0", "coordinates": (0, 0,)},
            {"latitude": "0", "user_id": 2, "name": "b", "longitude": "0", "coordinates": (0, 0,)},
            {"latitude": "0", "user_id": 3, "name": "c", "longitude": "0", "coordinates": (0, 0,)}
        ]
        inviter = Inviter()
        customer_test = ['{"latitude": "0", "user_id": 2, "name": "b", "longitude": "0"}',
                         '{"latitude": "0", "user_id": 3, "name": "c", "longitude": "0"}',
                         '{"latitude": "0", "user_id": 1, "name": "a", "longitude": "0"}']
        with tempfile.TemporaryDirectory() as temp_dir:
            f_path = os.path.join(temp_dir, 'customers.txt')
            with open(f_path, 'w') as f:
                f.write('\n'.join(customer_test))

            actual = inviter._get_customers(f_path)
            self.assertEqual(actual, expected)

    def test__get_customers_bad_file(self):
        inviter = Inviter()
        with tempfile.TemporaryDirectory() as temp_dir:
            f_path = os.path.join(temp_dir, 'customers.txt')
            with self.assertRaises(IOError):
                inviter._get_customers(f_path)

    def test_get_customers_to_invite(self):
        expected = [
            {"user_id": 2, "name": "b"},
            {"user_id": 3, "name": "c"}
        ]
        inviter = Inviter()
        customer_test = ['{"latitude": "53.339428", "user_id": 2, "name": "b", "longitude": "-6.257664"}',  # constants.DUBLIN_OFFICE_COORDINATES
                         '{"latitude": "53.339280", "user_id": 3, "name": "c", "longitude": "-6.281314"}',  # Facebook Dublin
                         '{"latitude": "51.886170", "user_id": 1, "name": "a", "longitude": "-8.402208"}',  # EMC Cork
                         '{"latitude": "-900", "user_id": 1, "name": "a", "longitude": ""}',  # Bad Data]
                         'zzz{"latitude": "53.339428", "user_id": 2, "name": "b", "longitude": "-6.257664"}']  # Bad Data
        with tempfile.TemporaryDirectory() as temp_dir:
            f_path = os.path.join(temp_dir, 'customers.txt')
            with open(f_path, 'w') as f:
                f.write('\n'.join(customer_test))

            actual = inviter.get_customers_to_invite(f_path)
            self.assertEqual(actual, expected)

    # def test_get_customers_to_invite(self):
    #     from intercom_inviter.constants import EARTH_RADIUS, ROOT_DIR
    #     inviter = Inviter()
    #     print(inviter.get_customers_to_invite(ROOT_DIR / 'tests' / 'customers.txt'))

    def test__great_circle_distance(self):
        # Some know distances grabbed from Google
        expected1 = 1.57
        point_a = (53.339428, -6.257664,)  # constants.DUBLIN_OFFICE_COORDINATES
        point_b = (53.339280, -6.281314,)  # Facebook Dublin
        inviter = Inviter()
        actual = inviter._great_circle_distance(point_a, point_b, EARTH_RADIUS)
        self.assertAlmostEquals(actual, expected1, places=2)
        expected2 = 463.15
        point_b = (51.509865, -0.118092,)  # London
        inviter = Inviter()
        actual = inviter._great_circle_distance(point_a, point_b, EARTH_RADIUS)
        self.assertAlmostEquals(actual, expected2, places=2)


if __name__ == '__main__':
    unittest.main()
