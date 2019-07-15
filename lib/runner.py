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
import argparse
import os

from lib.register import Register

# this is the env key we search for to exclude mingw shells
MSYSTEM = "MSYSTEM"


class Runner(object):

    def handle_args(self):
        """
        The following lines builds up the command (line arguments) structure
        :return:
        """
        reg = Register()
        job_dict = reg.command_list()

        # check for correct shell environment
        # basically exclude mingw shells
        if not self.check_shells():
            raise SystemExit("Please use Powershell!")

        self.main_parser = argparse.ArgumentParser(add_help=True, prog="python3 main.py")
        subparsers = self.main_parser.add_subparsers(dest="subcmd")
        self.command_parsers = dict()
        for tl_subcommand in job_dict.keys():
            self.parse_single_command(reg, subparsers, tl_subcommand)

        self.args = self.main_parser.parse_args()
        return self.args

    def parse_single_command(self, reg, subparsers, tl_subcommand):
        command_parser = subparsers.add_parser(tl_subcommand, help=tl_subcommand + " -h")
        subsubparser = command_parser.add_subparsers(dest="subsubcmd")
        self.command_parsers[tl_subcommand] = command_parser
        subsubcommands = set()
        for subsubcommand in reg.all_commands():
            if subsubcommand.subcommand != tl_subcommand:
                continue
            parser = subsubparser.add_parser(subsubcommand.subsubcommand)
            subsubcommand.build_args(subsubcommand.get_attr_config(), parser)
            if subsubcommand.get_additional_attr_config() is not None \
                    and len(subsubcommand.get_additional_attr_config()) != 0:
                for j in subsubcommand.get_additional_attr_config():
                    try:
                        if j.multi:
                            parser.add_argument("--" + j.name, help=j.help, type=j.input_type, nargs="+")
                        else:
                            parser.add_argument("--" + j.name, help=j.help, type=j.input_type)
                    except ValueError:
                        parser.add_argument("--" + j.name, help=j.help, type=str)

            subsubcommands.add(subsubcommand.subsubcommand)

    def handle_invalid_input(self):
        # print help messages if parameters are missing
        if self.args.subcmd is None:
            self.main_parser.print_help()
            exit(0)

        if self.args.subsubcmd is None:
            if self.args.subcmd in self.command_parsers.keys():
                self.command_parsers[self.args.subcmd].print_help()
            else:
                self.main_parser.print_help()
            exit(0)

    def execute(self):
        command = self.args.subcmd
        subcommand = self.args.subsubcmd
        is_executed = False

        for cmd in Register().all_commands():
            if cmd.subcommand == command and cmd.subsubcommand == subcommand:
                # run the command!
                cmd.run(self.args)
                is_executed = True
                break

        if not is_executed:
            print("No valid input")
            self.main_parser.print_help()

    def check_shells(self) -> bool:
        if MSYSTEM in os.environ.keys() and os.environ.get(MSYSTEM) == "MINGW64":
            return False
        return True
