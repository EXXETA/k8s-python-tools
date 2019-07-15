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
from lib import common
from lib.checker import wait_for_set_is_away
from lib.common import AbstractCommand, ArgumentConfig
from lib.confirmer import confirm_set, confirm
from lib.remover import remove_set


class RemoveSet(AbstractCommand):

    def get_command(self) -> str:
        return "drop set"

    def get_attr_config(self) -> ArgumentConfig:
        ac = ArgumentConfig()
        ac.context = True
        ac.namespace = True
        ac.set_type = True
        ac.set_name = True
        ac.no_wait = True
        return ac

    def run(self, args):
        context, namespace = common.choose_context_and_namespace(args.context, args.namespace)

        if args.set_type is not None and args.set_name is not None:
            remove_set(context, namespace, args.set_type, args.set_name)
            if args.no_wait is None or args.no_wait is False:
                wait_for_set_is_away(context, namespace, args.set_type, args.set_name)
        else:
            set = confirm_set(context, namespace)
            set_type = common.detect_set_type(set)

            set_name = set.metadata.name
            if set_name and confirm(
                    "Do you really want to delete set " + set_name + " in namespace " + namespace + "?"):
                remove_set(context, namespace, set_type, set_name)
                if args.no_wait is None or args.no_wait is False:
                    wait_for_set_is_away(context, namespace, set_type, set_name)
            else:
                print("NO set removal executed")
