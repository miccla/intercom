from pathlib import Path
from typing import Tuple, Union

import intercom_inviter

# IUGG mean earth radius in kilometers, from
# https://en.wikipedia.org/wiki/Earth_radius#Mean_radius.  Using a
# sphere with this radius results in an error of up to about 0.5%.
EARTH_RADIUS = 6371.009

DUBLIN_OFFICE_COORDINATES = (53.339428, -6.257664,)
ROOT_DIR = Path(intercom_inviter.__file__).parent.parent

Coordinates = Tuple[Union[float, int], Union[float, int]]


class InvalidCustomerException(Exception):
    pass
