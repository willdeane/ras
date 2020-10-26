import os
import re
import boto3
import botocore.exceptions
import argparse


# Define Functions
def get_profiles() -> list:
    # return list of aws profiles
    aws_config = os.path.expanduser('~/.aws/config')
    aws_profiles = ['default']
    try:
        with open(aws_config, 'r') as config:
            for line in config:
                if '[profile' in line:
                    match = re.search(r"\[([A-Za-z0-9 _-]+)]", line)
                    profile = match.group(1).split("profile ",)[1]
                    aws_profiles.append(profile)
                    # print(f"Adding {profile} to list of profiles to check")
    except OSError as err:
        print(f"Error: {err}")
        print("Ensure AWS config is correct - try running 'aws configure'")
        raise err
    return aws_profiles


def get_regions() -> list:
    aws_regions = []
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_regions()
        # print(response['Regions'])
        # print(type(response['Regions']))
        for region in response['Regions']:
            # print(region['RegionName'])
            aws_regions.append(region['RegionName'])
    except botocore.exceptions.ClientError as err:
        print(f"Error when getting regions: {err.response['Error']['Message']}")
    return aws_regions


def get_public_ips(profile: str, region: str) -> list:
    eips = []
    try:
        session = boto3.Session(profile_name=profile, region_name=region)
        ec2_client = session.client('ec2')
        response = ec2_client.describe_addresses()
        for ip in response['Addresses']:
            # print(ip['PublicIp'])
            eips.append(ip['PublicIp'])
    except botocore.exceptions.ClientError as err:
        print(f"Error when processing request for profile {profile}: {err.response['Error']['Message']}")
    return eips


# Get parameters
parser = argparse.ArgumentParser(description='''
                                  Search AWS account(s) for EIPs \n
                                  By default it uses all configured profiles in 
                                  aws credentials as per AWS CLI; or you can specify a specific profile''')

parser.add_argument('--aws-profile',
                    help='Specify amazon profile to use.',
                    default=None,
                    dest='profile',
                    nargs='*')
parser.add_argument('--regions',
                    help='Specify regions separated by space',
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

