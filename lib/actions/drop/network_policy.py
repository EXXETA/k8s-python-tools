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
from lib.checker import wait_for_network_policy_is_away
from lib.common import AbstractCommand, choose_context_and_namespace, ArgumentConfig
from lib.confirmer import confirm_network_policy, confirm
from lib.remover import remove_network_policy

# DO NOT TOUCH! this file is auto-generated and will be overwritten. Use templates/action_removal.py.j2


class DropNetworkPolicy(AbstractCommand):

    def get_command(self) -> str:
        return "drop network_policy"

    def get_attr_config(self) -> ArgumentConfig:
        arg = ArgumentConfig()
        arg.context = True
        arg.namespace = True
        arg.network_policy = True
        return arg

    def run(self, args):
        
        context, namespace = choose_context_and_namespace(args.context, args.namespace)

        if args.network_policy:
            remove_network_policy(context, namespace, args.network_policy)
            wait_for_network_policy_is_away(context, namespace, args.network_policy)
        else:
            obj = confirm_network_policy(context, namespace)
            if obj is not None and confirm("Do you really want to delete NetworkPolicy " + obj + " in namespace " + namespace + "?"):
                remove_network_policy(context, namespace, obj)
                wait_for_network_policy_is_away(context, namespace, obj)
            else:
                print("No NetworkPolicy removal executed")
        