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

from lib.common import AbstractCommand, ArgumentConfig, load_kube
from lib.confirmer import confirm_context


class ListIngressByContext(AbstractCommand):

    def get_command(self) -> str:
        return "list ingress-by-context"

    def get_attr_config(self) -> ArgumentConfig:
        attr = ArgumentConfig()
        attr.context = True
        return attr

    def run(self, args):
        if args.context:
            context = args.context
        else:
            context = confirm_context()
        load_kube(context)

        # use the following for manual interaction with the k8s python api:
        # api = client.ExtensionsV1beta1Api()
        # api = client.CoreV1Api()
        # ret = api.list_ingress_for_all_namespaces()

        api = client.ExtensionsV1beta1Api()
        print("Listing ingresses in all namespaces of context:", context)
        ret = api.list_ingress_for_all_namespaces()

        print("results:", len(ret.items))
        for i in ret.items:
            if i.spec.rules is not None:
                for rule in i.spec.rules:
                    print("%s\t%s\t%s\t" % (rule.host, i.metadata.namespace, i.metadata.name))
