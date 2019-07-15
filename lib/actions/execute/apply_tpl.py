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
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load
except ImportError:
    from yaml import Loader, Dumper

import subprocess
from typing import Iterable

from lib.common import AbstractCommand, ArgumentConfig, CustomParameter, DynamicArgs, choose_context, YamlTemplateRunner
from lib.confirmer import confirm


class ApplyTpl(AbstractCommand):
    """
    Input one or several yaml files with jinja2 syntax and render these templates with input values (= the template
    vars) and store them on the filesystem.
    Optional the user is able to exec a native "kubectl apply -f generated_files"
    """

    def get_command(self) -> str:
        return "execute apply-tpl"

    def get_additional_attr_config(self) -> Iterable[CustomParameter]:
        return (CustomParameter("path", "an absolute template directory path", DynamicArgs.INPUT_TYPE_PATH),
                CustomParameter("files", "one or several space-separated relative yaml template file paths", str,
                                multi=True),
                CustomParameter("name", "a release name for the new template (e.g. dev)", str),)

    def get_attr_config(self) -> ArgumentConfig:
        args = ArgumentConfig()
        args.context = True
        return args

    def run(self, args):
        context = choose_context(args.context)
        arguments = DynamicArgs(context, args, self.get_additional_attr_config())

        path = arguments.val("path")
        tpl_files = arguments.val("files")
        name = arguments.val("name")

        if isinstance(tpl_files, str):
            tpl_files = [tpl_files, ]

        for i in tpl_files:
            print(i)
            tpl = YamlTemplateRunner(path, str(i), name)
            if tpl.is_ready():
                if confirm("Do you want to apply the contents of file with kubectl apply -f " + tpl.rendered_tpl + ""):
                    # apply generated file via kubectl apply -f
                    kubectl_cmd = "kubectl apply -f " + tpl.rendered_tpl
                    print("executing:", kubectl_cmd)
                    print("---")
                    subprocess.run(kubectl_cmd, shell=True)
                    print("---")
                else:
                    print("File is not applied to context", context)
            else:
                print("problem with file", i)
