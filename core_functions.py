# Module: core_functions
# Contains core functions useful for AWS scripts:
#  #get_profiles - returns list of profiles configured for AWS CLI
#  #get_regions - returns a list of 'enabled' aws regions for an account - uses default aws cli profile
#  #get_public_ips - returns a list of IPs for a the specified profile,region

import boto3
import botocore.exceptions
import os
import re


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
        for region in response['Regions']:
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
            eips.append(ip['PublicIp'])
    except botocore.exceptions.ClientError as err:
        print(f"Error when processing request for profile {profile}: {err.response['Error']['Message']}")
    except botocore.exceptions.ProfileNotFound as err:
        print(f"Profile {profile} not found")
    return eips
