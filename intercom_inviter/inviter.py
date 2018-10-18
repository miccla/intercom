import io
import json
import logging
from json import JSONDecodeError
from typing import List, Union

from math import cos, sin, radians, acos

from intercom_inviter.constants import InvalidCustomerException, Coordinates, DUBLIN_OFFICE_COORDINATES, EARTH_RADIUS

logger = logging.getLogger(__name__)


class Inviter:
    @staticmethod
    def _is_valid_coordinates(coordinates: Coordinates) -> bool:
        if coordinates[0] < -90.0 or coordinates[0] > 90.0 or coordinates[1] < -180 or coordinates[1] > 180:
            logger.warning('(%s, %s) are invalid coordinates.' % (coordinates[0], coordinates[1]))
            return False
        else:
            return True

    def _get_customers_from_file(self, customer_file: io.TextIOBase) -> dict:
        for customer_json in customer_file:
            try:
                customer = json.loads(customer_json)
                coordinates = (float(customer['latitude']), float(customer['longitude']),)
                if self._is_valid_coordinates(coordinates):
                    customer['coordinates'] = coordinates
                    yield customer
                else:
                    raise InvalidCustomerException
            except(JSONDecodeError, InvalidCustomerException, ValueError):
                logger.error('Unable to parse customer: %s' % customer_json)

    def _is_two_points_within_km(self, point_a: Coordinates, point_b: Coordinates, distance: Union[int, float]) -> bool:
        if distance < 0:
            logger.warning('%s is invalid. Distance must be >= 0.' % distance)
        else:
            calculated_distance = self._great_circle_distance(point_a, point_b, EARTH_RADIUS)
            if calculated_distance <= distance:
                return True

        return False

    def _great_circle_distance(self, point_a: Coordinates, point_b: Coordinates, radius: float) -> float:
        """
        Formula from: https://en.wikipedia.org/wiki/Great-circle_distance
        """
        if self._is_valid_coordinates(point_a) and self._is_valid_coordinates(point_b):
            lat_a, lng_a = radians(point_a[0]), radians(point_a[1])
            lat_b, lng_b = radians(point_b[0]), radians(point_b[1])

            sin_lat1, cos_lat1 = sin(lat_a), cos(lat_a)
            sin_lat2, cos_lat2 = sin(lat_b), cos(lat_b)

            delta_lng = lng_b - lng_a
            cos_delta_lng = cos(delta_lng)

            d = acos(sin_lat1 * sin_lat2 + cos_lat1 * cos_lat2 * cos_delta_lng)
            return radius * d

    def _get_customers(self, customer_file_path: str) -> List[dict]:
        customers = []
        try:
            with open(customer_file_path, 'r') as f:
                for customer in self._get_customers_from_file(f):
                    customers.append(customer)

            customers = sorted(customers, key=lambda x: x['user_id'])
            return customers
        except IOError:
            logger.error('Unable to open file: %s' % customer_file_path)
            raise

    def get_customers_to_invite(self, customer_file_path: str) -> List[dict]:
        invitees = []
        customers = self._get_customers(customer_file_path)
        for customer in customers:
            if self._is_two_points_within_km(customer['coordinates'], DUBLIN_OFFICE_COORDINATES, 100):
                invitees.append({'name': customer['name'], 'user_id': customer['user_id']})
        return invitees
