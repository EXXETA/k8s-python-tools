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

from lib.common import AbstractCommand, load_kube, ArgumentConfig
from lib.confirmer import confirm_context


class ListPodsByContext(AbstractCommand):

    def get_attr_config(self) -> ArgumentConfig:
        ac = ArgumentConfig()
        ac.context = True
        return ac

    def run(self, args):
        if args.context is not None:
            context = args.context
        else:
            context = confirm_context()
        load_kube(context)

        v1 = client.CoreV1Api()
        print("Listing pods with their IPs and owner in context:", context)
        ret = v1.list_pod_for_all_namespaces(watch=False)

        print("results:", len(ret.items))
        for i in ret.items:
            owner_reference = ''
            if i.metadata.owner_references:
                owner = i.metadata.owner_references[0]
                owner_reference = owner.kind + "(" + owner.name + ")"
            print("%s\t%s\t%s\t%s\t" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name, owner_reference))

    def get_command(self) -> str:
        return "list pods-by-context"
