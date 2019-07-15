#
# Copyright (c) 2019 EXXETA AG and others.
#
# This file is part of k8s-python-tools
# (see https://github.com/EXXETA/k8s-python-tools).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
from kubernetes import client

from lib.common import AbstractCommand, ArgumentConfig, choose_context_and_namespace, confirm_number
from lib.confirmer import confirm_deployment, confirm


class ScaleDeployment(AbstractCommand):
    """
    This class provides a mechanism to scale deployments
    """
    def get_command(self) -> str:
        return "execute scale-deployment"

    def get_attr_config(self) -> ArgumentConfig:
        attr = ArgumentConfig()
        attr.context = True
        attr.namespace = True
        attr.deployment = True
        return attr

    def run(self, args):
        print("Starting scaling deployment")
        context, namespace = choose_context_and_namespace(args.context, args.namespace)

        if args.deployment is not None:
            deployment = args.deployment
        else:
            deployment = confirm_deployment(context, namespace)

        api = client.ExtensionsV1beta1Api()
        ret, status, _ = api.read_namespaced_deployment_scale_with_http_info(deployment, namespace)

        # detected desired and current state
        desired_replica_count = "undefined"
        current_replica_count = "undefined"
        if hasattr(ret.spec, "replicas") and ret.spec.replicas is not None:
            desired_replica_count = int(ret.spec.replicas)
        if hasattr(ret.status, "replicas") and ret.status is not None:
            current_replica_count = int(ret.status.replicas)

        print("Deployment %s has %s/%s replicas" % (ret.metadata.name, desired_replica_count, current_replica_count))

        replica_count = confirm_number("Please enter a number of replicas for scaling",
                                       "Current replicas: %s" % current_replica_count)

        if confirm(
                "Do you really want to scale Deployment '%s' in context '%s' from %d to %d replicas?"
                % (deployment, context, current_replica_count, replica_count)):
            print("Scaling deployment %s to %d replicas..." % (deployment, replica_count))
            ret, status, _ = api.patch_namespaced_deployment_scale_with_http_info(deployment, namespace, {
                'spec': {
                    'replicas': replica_count,
                }})
            print("Finish scale scaling deployment '%s'" % deployment)
        else:
            print("No change executed in namespace '%s'." % namespace)
