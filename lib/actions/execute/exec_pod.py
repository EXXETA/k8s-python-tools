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
from lib.common import AbstractCommand, ArgumentConfig
from lib.confirmer import confirm_pod


class ExecPod(AbstractCommand):
    """
    Execute commands in a pod
    TODO improve "shell input" and use more features of prompt_toolkit!
    """

    def get_attr_config(self) -> ArgumentConfig:
        ac = ArgumentConfig()
        ac.context = True
        ac.namespace = True
        ac.pod = True
        return ac

    def run(self, args):
        context, namespace = common.choose_context_and_namespace(args.context, args.namespace)

        if args.pod:
            pod = args.pod
        else:
            pod = confirm_pod(context, namespace)
        print("using pod", pod)

        print("For interactive shell in (the first container of) a pod please use:\n"
              "kubectl config use-context %s\n"
              "kubectl exec -ti %s %s -n %s" % (context, pod, "sh", namespace))

    def get_command(self) -> str:
        return "execute pod"
