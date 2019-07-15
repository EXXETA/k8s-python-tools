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


class ListPvcsByContext(AbstractCommand):
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

        api = client.CoreV1Api()
        print("Listing pvcs in all namespaces of context:", context)
        ret = api.list_persistent_volume_claim_for_all_namespaces()

        print("results:", len(ret.items))
        for i in ret.items:
            owner_reference = ''
            if i.metadata.owner_references:
                owner = i.metadata.owner_references[0]
                owner_reference = owner.kind + "(" + owner.name + ")"
            print("%s\t%s\t%s\t%s\t" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name, owner_reference))

    def get_command(self) -> str:
        return "list pvc-by-context"
