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
import importlib
import os
import pkgutil

from lib.common import AbstractCommand

ACTION_MODULES = ["execute", "list", "drop"]


class Register:
    """
    This class automatically imports everything of the directories above in *lib.actions*.
    """

    def all_commands(self) -> [AbstractCommand]:
        for i in ACTION_MODULES:
            module_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "actions", i)
            for (module_loader, name, ispkg) in pkgutil.iter_modules([module_path]):
                importlib.import_module('.actions.' + i + "." + name, __package__)
        # the following line loads ALL known direct subclasses of AbstractCommand
        return [cls() for cls in AbstractCommand.__subclasses__()]

    def command_list(self) -> dict:
        """
        Returns a tree-like dict of command structure. everything is dynamic.
        :return:
        """
        job_dict = dict()
        commands = self.all_commands()
        # print("Loading", len(commands), "commands")
        for abstract_cmd in commands:
            if abstract_cmd.subcommand not in job_dict.keys():
                job_dict[abstract_cmd.subcommand] = set()
            job_dict[abstract_cmd.subcommand].add(abstract_cmd.subsubcommand)

        return job_dict


def main():
    pass


if __name__ == "__main__":
    main()
