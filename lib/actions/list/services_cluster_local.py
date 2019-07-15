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

from lib.common import AbstractCommand, ArgumentConfig, choose_context


class ServicesClusterLocal(AbstractCommand):
    """
    A command for listing all services and ingresses with "cluster.local" in field "spec.external_name"
     or "spec.rules[].host".
    Could be extended to spec.hostname and spec.subdomain of pods.
    """

    def get_command(self) -> str:
        return "list svc-cluster-local"

    def get_attr_config(self) -> ArgumentConfig:
        args = ArgumentConfig()
        args.context = True
        return args

    def run(self, args):
        context = choose_context()
        print("Listing all services with cluster.local in external_name", context)

        api = client.CoreV1Api()
        svcs = api.list_service_for_all_namespaces()
        print("Found", len(svcs.items), "services in all namespaces")
        counter = 0
        key = "cluster.local"
        print("Namespace\tService\tExternalName\t")
        for svc in svcs.items:
            if key in str(svc.spec.external_name):
                print("%s\t%s\t%s" % (svc.metadata.namespace, svc.metadata.name, svc.spec.external_name))
                counter += 1
        print("Found %u services with an external name containing '%s'" % (counter, key))
        # ingress hosts
        api2 = client.ExtensionsV1beta1Api()
        ingresses = api2.list_ingress_for_all_namespaces()
        print("Found %d ingresses in all namespaces" % len(ingresses.items))
        counter = 0
        print("Namespace\tIngress name\tHost name")
        for ing in ingresses.items:
            if ing.spec.rules is not None:
                for rule in ing.spec.rules:
                    if key in str(rule.host):
                        print("%s\t%s\t%s" % (ing.metadata.namespace, ing.metadata.name, rule.host))
        print("Found %u ingresses with host names containing '%s'" % (counter, key))
