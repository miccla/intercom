import argparse
import logging

from intercom_inviter.inviter import Inviter

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--customers', help='Path to text file of json formatted customers.', type=str, required=True)
    args = parser.parse_args()
    inviter = Inviter()

    print('The following users are within 100k of the Intercom Dublin Office (Ordered by user_id).:')
    for invitee in inviter.get_customers_to_invite(args.customers):
        print(' ', end='')
        print(invitee)
