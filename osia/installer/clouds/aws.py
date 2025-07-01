# -*- coding: utf-8 -*-
#
# Copyright 2020 Osia authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module implements configuration object for aws installation"""
import configparser
import logging

from typing import Optional

import boto3

from .base import AbstractInstaller


def _get_connection(*args, **kwargs):
    return boto3.client("ec2", *args, **kwargs)


class AWSInstaller(AbstractInstaller):
    """Object containing all configuration related
    to aws installation"""

    def __init__(self, cluster_region=None, list_of_regions=None, credentials_file=None, **kwargs):
        super().__init__(**kwargs)
        self.cluster_region = cluster_region
        self.list_of_regions = list_of_regions if list_of_regions else []
        self.credentials_file = credentials_file

        self.boto_kwargs = {}

        if self.credentials_file:
            config = configparser.ConfigParser()
            config.read(self.credentials_file)

            self.boto_kwargs["aws_access_key_id"] = config["default"][
                "aws_access_key_id"
            ]
            self.boto_kwargs["aws_secret_access_key"] = config["default"][
                "aws_secret_access_key"
            ]

    def get_template_name(self):
        return 'aws.jinja2'

    def acquire_resources(self):
        region = self.get_free_region()

        if region is None:
            logging.error("No free region amongst selected ones: %s",
                          ', '.join(self.list_of_regions))
            raise Exception("No free region found")
        logging.info("Selected region %s", region)
        self.cluster_region = region

    def get_api_ip(self) -> Optional[str]:
        return None

    def get_apps_ip(self):
        return None

    def post_installation(self):
        pass

    def get_free_region(self) -> Optional[str]:
        """Finds first free region in provided list,
        if provided list is empty, it searches all regions"""
        candidates = self.list_of_regions[:]
        if len(candidates) == 0:
            candidates = [v['RegionName'] for v in _get_connection(**self.boto_kwargs).describe_regions()['Regions']]
        for candidate in candidates:
            region = _get_connection(candidate, **self.boto_kwargs)
            count = len(region.describe_vpcs()['Vpcs'])
            if count < 5:
                logging.debug("Selected region %s", candidate)
                return candidate
        return None
