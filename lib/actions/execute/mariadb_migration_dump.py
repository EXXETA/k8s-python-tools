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
from typing import Iterable

from lib.actions.migrator import MariaDBMigration
from lib.common import AbstractCommand, ArgumentConfig, CustomParameter, choose_context, DynamicArgs


class MariaDBMigrationDump(AbstractCommand):
    """
    This class generates a full dump on source pod with mysqldump and downloads it to local folder (where the cmd is executed).
    sha256sum is used for content consistency check. If gzip is available, its used.
    Then, the dump file is uploaded to (potentially another) context, namespace and pod and imported with mysql.
    """

    def get_command(self) -> str:
        return "execute mariadb-migration-dump"

    def get_attr_config(self) -> ArgumentConfig:
        args = ArgumentConfig()
        args.context = True
        return args

    def get_additional_attr_config(self) -> Iterable[CustomParameter]:
        return (
            CustomParameter("snamespace", "source namespace", DynamicArgs.INPUT_TYPE_NAMESPACE),
            CustomParameter("spod", "source pod", DynamicArgs.INPUT_TYPE_POD, dependency="snamespace"),
            CustomParameter("sport", "source mariadb database port", int, default="3306"),
            CustomParameter("suser", "source mariadb database user", str),
            CustomParameter("spw", "source mariadb database password", str, prompt=True),
            CustomParameter("slocation", "source mariadb database dump location", str, required=False, default="/tmp"),
            CustomParameter("tcontext", "target context", DynamicArgs.INPUT_TYPE_CONTEXT),
            CustomParameter("tnamespace", "target namespace", DynamicArgs.INPUT_TYPE_NAMESPACE),
            CustomParameter("tpod", "target pod", DynamicArgs.INPUT_TYPE_POD, dependency="tnamespace"),
            CustomParameter("tport", "target mariadb database port", int, default="3306"),
            CustomParameter("tuser", "target mariadb database user", str),
            CustomParameter("tpw", "target mariadb database password", str),
            CustomParameter("tlocation", "target mariadb database dump location", str, required=False,
                            default="/tmp"),)

    def run(self, args):
        context_src = choose_context(args.context)

        arguments = DynamicArgs(context_src, args, self.get_additional_attr_config())
        MariaDBMigration(context_src, arguments).run()
