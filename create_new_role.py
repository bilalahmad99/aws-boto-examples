#!/usr/bin/python

import logging
import os
import time
import argparse
import botocore.session
import botocore.exceptions


def role_exists(iam, role_name):
    """Checks if the role exists already"""
    try:
        iam.get_role(RoleName=role_name)
    except botocore.exceptions.ClientError:
        return False
    return True


def get_role_arn(iam, role_name):
    """Gets the ARN of role"""
    response = iam.get_role(RoleName=role_name)
    return response['Role']['Arn']


def create_role(iam, policy_name, assume_role_policy_document, policy_str):
    """Creates a new role if there is not already a role by that name"""
    if role_exists(iam, policy_name):
        logging.info('Role "%s" already exists. Assuming correct values.', policy_name)
        return get_role_arn(iam, policy_name)
    else:
        response = iam.create_role(RoleName=policy_name,
                                   AssumeRolePolicyDocument=assume_role_policy_document)
        iam.put_role_policy(RoleName=policy_name,
                            PolicyName='inlinepolicy', PolicyDocument=policy_str)
        logging.info('response for creating role = "%s"', response)
        return response['Role']['Arn']


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument("--aws-profile", required=True)
    parser.add_argument("--aws-region", default="us-east-1")

    args = parser.parse_args()
    session = botocore.session.Session(profile=args.aws_profile)

    iam_client = session.create_client('iam', args.aws_region)
    role_arn = create_role(iam_client, 'my_basic_role',
                           '{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Principal": '
                           '{"Service": "ec2.amazonaws.com"},"Action": "sts:AssumeRole"}]}',
                           open(os.path.join(os.path.dirname(__file__), 'role_policy.json')).read())
