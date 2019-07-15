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
import datetime
import os
from abc import abstractmethod, ABC

from lib.checker import wait_for_pod_is_up
from lib.common import load_kube
from lib.exec import CommandChecker, run_command_in_pod, RemoteFileHash, DownloadFile, LocalFileHash, EnoughSpaceCheck, \
    RemoteDirExists, UploadFile


class Migrator(ABC):
    """
    Basic class to use for a database migration process
    """

    def __init__(self, context_src, arguments, db_vendor):
        self.context_src = context_src
        self.arguments = arguments
        self.db_vendor = db_vendor

    def run(self):
        print("start of", self.db_vendor, "migration process")

        namespace_src = self.arguments.val("snamespace")
        namespace_dest = self.arguments.val("tnamespace")
        pod_src = self.arguments.val("spod")
        pod_dest = self.arguments.val("tpod")

        # check if the pods are there
        wait_for_pod_is_up(self.context_src, namespace_src, pod_src)
        wait_for_pod_is_up(self.context_src, namespace_dest, pod_dest)

        # generate dump cmd
        cmd, has_gzip, src_dump_file = self.generate_backup_cmd()

        print(self.db_vendor, "backup cmd:", cmd)

        # dump on source pod
        output = run_command_in_pod(self.context_src, namespace_src, pod_src, cmd)
        print(self.db_vendor, "backup cmd output:", output)

        # download file and upload to target
        # sha256 hashes are checked
        dest_file = self.checked_move_between_pods_via_local(self.context_src, has_gzip, src_dump_file)
        print("start importing dump")
        import_cmd = self.generate_restore_cmd(dest_file, has_gzip)

        print(self.db_vendor, "restore cmd:", import_cmd)
        output = run_command_in_pod(self.context_src, namespace_dest, pod_dest, import_cmd)
        print(self.db_vendor, "restore cmd output:", output)

        print("finish of", self.db_vendor, "migration process")

    @abstractmethod
    def generate_restore_cmd(self, dest_file, has_gzip) -> str:
        ...

    @abstractmethod
    def generate_backup_cmd(self):
        ...

    def checked_move_between_pods_via_local(self, context_src, has_gzip, src_dump_file):
        """
        This method moves a file to the destination via a local copy.
        sha256sum is checked in each step for consistency

        :param context_src:
        :param has_gzip:
        :param src_dump_file:
        :return:
        """
        context_dest = self.arguments.val("tcontext")
        namespace_dest = self.arguments.val("tnamespace")
        namespace_src = self.arguments.val("snamespace")
        pod_dest = self.arguments.val("tpod")
        pod_src = self.arguments.val("spod")

        hash1 = RemoteFileHash(context_src, namespace_src, pod_src, src_dump_file).run()
        now = datetime.datetime.today()
        local_dump_file = os.getcwd() + "/dump-" + context_src + "-" + namespace_src + "-" \
                          + pod_src + "-" + now.strftime("%y-%m-%d-%H%M%S") + ".sql"
        if has_gzip:
            print("using gzip")
            local_dump_file += ".gz"
        print("Downloading dump file to", local_dump_file)
        DownloadFile(context_src, namespace_src, pod_src, src_dump_file, local_dump_file).run()
        hash_local = LocalFileHash(local_dump_file).run()
        if hash1 != hash_local:
            raise SystemExit("Something went wrong during download of dump file. Hashes do not match! Exiting.")
        else:
            print("Hashes do match.")

        self.space_check(context_src, local_dump_file)

        remote_path = self.arguments.val("tlocation")
        remote_dir_exists = RemoteDirExists(context_dest, namespace_dest, pod_dest, remote_path).run()
        if not remote_dir_exists:
            raise SystemExit(
                "invalid remote path %s on target namespace '%s' in pod '%s'" % (remote_path, namespace_dest, pod_dest))

        dest_file = remote_path + "/" + os.path.basename(local_dump_file)
        print("dest_file name", dest_file)
        print("Uploading dump file from", local_dump_file, "to", dest_file)
        UploadFile(context_src, namespace_dest, pod_dest, local_dump_file, dest_file).run()
        hash2 = RemoteFileHash(context_src, namespace_dest, pod_dest, dest_file).run()
        if hash1 != hash2 != hash_local:
            raise SystemExit("Something went wrong during upload of dump file. Hashes do not match! Exiting.")
        else:
            print("Hashes do match..")
        return dest_file

    def space_check(self, context_src, local_dump_file):
        """
        Method to read the local file size and checking if the remote pod has enough free space available

        :param context_src:
        :param local_dump_file:
        :return:
        """
        context_dest = self.arguments.val("tcontext")
        namespace_src = self.arguments.val("snamespace")
        namespace_dest = self.arguments.val("tnamespace")
        pod_src = self.arguments.val("spod")
        pod_dest = self.arguments.val("tpod")

        file_size_kb = (os.path.getsize(local_dump_file) // 1024)
        file_size_mb = (file_size_kb // 1024) + 1
        if file_size_kb < 10000:
            print("file size:", file_size_kb, "KB")
        else:
            print("file size:", file_size_mb, "MB")
        # switch kube-ctl context
        load_kube(context_dest)
        has_enough_space = EnoughSpaceCheck(context_src, namespace_src, pod_src, file_size_mb).run()
        if not has_enough_space:
            raise SystemExit(
                "Not enough space on target pod " + pod_dest + " in namespace " + namespace_dest + " and context " + context_dest)


class MariaDBMigration(Migrator):

    def __init__(self, context_src, arguments):
        super().__init__(context_src, arguments, "MariaDB")

    def generate_restore_cmd(self, dest_file, has_gzip) -> str:
        pw_arg = ""
        target_pw = self.arguments.val("tpw")
        if target_pw is not None or target_pw is not "":
            pw_arg = "-p" + target_pw
        if has_gzip:
            import_cmd = ("gunzip -c %s | " % dest_file) + "mysql -u %s %s -P %s" \
                         % (self.arguments.val("tuser"), pw_arg, self.arguments.val("tport"))
        else:
            import_cmd = "mysql -u %s %s -P %s < %s" % (self.arguments.val("tuser"), pw_arg, self.arguments.val(
                "tport"), dest_file)
        return import_cmd

    def generate_backup_cmd(self):
        """
                This method is used to generate the backup cmd with pg_dumpall

                :param arguments:
                :param context:
                :return:
                """
        namespace_src = self.arguments.val("snamespace")
        pod_src = self.arguments.val("spod")
        context_src = self.context_src

        cmd = "mysqldump --all-databases -u " + str(self.arguments.val("suser")) \
              + " -P " + str(self.arguments.val("sport"))
        pw_src = self.arguments.val("spw")
        if pw_src is not None and pw_src is not "":
            cmd += " -p" + str(pw_src)
        cc = CommandChecker(context_src, namespace_src, pod_src, "gzip")
        has_gzip = cc.run()

        remote_path = self.arguments.val("slocation")
        remote_dir_exists = RemoteDirExists(context_src, namespace_src, pod_src, remote_path)
        if not remote_dir_exists:
            raise SystemExit("Remote directory %s does not exist." % remote_path)

        src_dump_file = str(remote_path) + "/dump.sql"
        if has_gzip:
            src_dump_file += ".gz"
            cmd += " | gzip > %s" % src_dump_file
        else:
            cmd += " > %s" % src_dump_file
        return cmd, has_gzip, src_dump_file


class PostgreSQLMigration(Migrator):

    def __init__(self, context_src, arguments):
        super().__init__(context_src, arguments, "PostgreSQL")

    def generate_restore_cmd(self, dest_file, has_gzip) -> str:
        pw_arg = "-w"
        target_pw = self.arguments.val("tpw")
        if target_pw is not None or target_pw is not "":
            pw_arg = "-W " + target_pw
        if has_gzip:
            psql_import_cmd = ("gunzip -c %s | " % dest_file) + "psql -U %s %s -p %s postgres" \
                              % (self.arguments.val("tuser"), pw_arg, self.arguments.val("tport"))
        else:
            psql_import_cmd = "psql -U %s %s -p %s -f %s postgres" % (
                self.arguments.val("tuser"), pw_arg, self.arguments.val(
                    "tport"), dest_file)
        return psql_import_cmd

    def generate_backup_cmd(self):
        """
        This method is used to generate the backup cmd with pg_dumpall

        :param arguments:
        :param context:
        :return:
        """
        namespace_src = self.arguments.val("snamespace")
        pod_src = self.arguments.val("spod")

        cmd = "pg_dumpall --clean -U " + str(self.arguments.val("suser")) \
              + " -p " + str(self.arguments.val("sport"))
        pw_src = self.arguments.val("spw")
        if pw_src is None or pw_src is "":
            cmd += " -w "
        else:
            cmd += " -W " + str(pw_src)
        cc = CommandChecker(self.context_src, namespace_src, pod_src, "gzip")
        has_gzip = cc.run()

        remote_path = self.arguments.val("slocation")
        remote_dir_exists = RemoteDirExists(self.context_src, namespace_src, pod_src, remote_path)
        if not remote_dir_exists:
            raise SystemExit("Remote dir %s does not exist." % remote_path)

        src_dump_file = str(remote_path) + "/dump.sql"
        if has_gzip:
            src_dump_file += ".gz"
            cmd += " | gzip > %s" % src_dump_file
        else:
            cmd += " > %s" % src_dump_file
        return cmd, has_gzip, src_dump_file
