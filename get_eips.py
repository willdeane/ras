import boto3
import botocore.exceptions
import argparse
from core_functions import get_regions, get_profiles, get_public_ips

# Get parameters
parser = argparse.ArgumentParser(description='''
                                  Search AWS account(s) for EIPs \n
                                  By default it uses all configured profiles in 
                                  aws credentials as per AWS CLI; or you can specify specific profile(s)''')

parser.add_argument('--aws-profile',
                    help='Specify one or more amazon profiles separated by a space.',
                    default=None,
                    dest='profile',
                    nargs='*')
parser.add_argument('--regions',
                    help='Specify one or more regions separated by a space.',
                    default=None,
                    dest='requested_regions',
                    nargs='*')
args = parser.parse_args()

# Setup either specified or all profiles
if args.profile:
    profiles = args.profile
else:
    profiles = get_profiles()

# Setup either specified or all regions
if args.requested_regions:
    regions = args.requested_regions
else:
    regions = get_regions()


print(f"profiles to use: {profiles}")
print(f"regions to use: {regions}")

all_public_ips = []

for p in profiles:
    try:
        session = boto3.Session(profile_name=p)
        sts_client = session.client('sts')
        response = sts_client.get_caller_identity()
        print(f"Checking for public IPs in account: {response['Account']} (profile: {p}) in regions:")
        for r in regions:
            print(f"{r}:")
            x = get_public_ips(p, r)
            if x:
                all_public_ips.extend(x)
                print(*x, sep='\n')
                print("\n")
    except botocore.exceptions.ClientError as err:
        print(f"Error when processing request for profile {p}: {err.response['Error']['Message']}")
    except botocore.exceptions.ProfileNotFound as err:
        print(f"Profile {p} not found")
