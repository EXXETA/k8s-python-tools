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
import os
import subprocess

from kubernetes import stream
from kubernetes.client.apis import core_v1_api
from kubernetes.client.rest import ApiException

from lib.common import load_kube

init_exec_command = ['/bin/sh']


def run_command_in_pod(context, namespace, pod, command):
    if context is None:
        raise SystemExit("Null context given")
    load_kube(context)
    api = core_v1_api.CoreV1Api()
    try:
        command_ = init_exec_command + ["-c", command]
        resp = stream.stream(api.connect_get_namespaced_pod_exec, name=pod, namespace=namespace,
                             command=command_,
                             stderr=True, stdin=False,
                             stdout=True, tty=False)
        return resp
    except ApiException as err:
        print("Something went wrong while connecting to pod", pod, "in namespace", namespace)
        print(err)
        return None


class DownloadFile:
    """
    Helper class for file downloading via kubectl cp
    """

    def __init__(self, context, namespace, pod, source_file_in_pod, local_dest_file):
        self.context = context
        self.namespace = namespace
        self.pod = pod
        self.source_file = source_file_in_pod
        self.dest_file = local_dest_file

    def run(self):
        load_kube(self.context)

        cmd = "kubectl cp {0}/{1}:{2} {3}".format(self.namespace, self.pod, self.source_file, self.dest_file)
        print("executing:", cmd)
        process = subprocess.run(cmd, shell=True)
        print(process)


class UploadFile:
    """
    Helper class for file uploading via kubectl cp
    """

    def __init__(self, context, namespace, pod, local_source_file, dest_file_in_pod):
        self.context = context
        self.namespace = namespace
        self.pod = pod
        self.local_source_file = local_source_file
        self.dest_file_in_pod = dest_file_in_pod

    def run(self):
        load_kube(self.context)

        cmd = "kubectl cp {0} {1}/{2}:{3}".format(self.local_source_file, self.namespace, self.pod,
                                                  self.dest_file_in_pod)
        print("executing:", cmd)
        process = subprocess.run(cmd, shell=True)
        print(process)


class RemoteFileHash:
    """
    Helper class to detect sha256sum of a remote file in a pod
    """

    def __init__(self, context, namespace, pod, file_path):
        self.context = context
        self.namespace = namespace
        self.pod = pod
        self.file_path = file_path

    def run(self) -> str:
        output = run_command_in_pod(self.context, self.namespace, self.pod,
                                    "sha256sum " + self.file_path)
        if output is None or output is "":
            raise SystemExit("could not generate sha256 sum of remote file" + self.file_path + " in pod "
                             + self.pod + " and namespace " + self.namespace)
        hash = str(output).split(" ")[0]
        if hash is None or hash is "":
            raise SystemExit("could not get sha256 sum of remote file" + self.file_path + " in pod "
                             + self.pod + " and namespace " + self.namespace)
        print("detected remote hash:", hash)
        return str(bytes(hash, "utf-8"), "utf-8")


class CommandChecker:
    """
    Helper class to check if a given shell command is available in remote pod
    """

    def __init__(self, context, namespace, pod, cmd):
        self.context = context
        self.namespace = namespace
        self.pod = pod
        self.cmd = cmd

    def run(self) -> bool:
        output = run_command_in_pod(self.context, self.namespace, self.pod,
                                    "if [ -x '$(command -v " + self.cmd + ")' ]; then echo 'false';else echo 'true';fi")
        if output == "True":
            print("shell command", self.cmd, "is available")
        else:
            print("shell command", self.cmd, "is NOT available")
        return output == "True"


class LocalFileHash:
    """
    Helper class to generate local sha256sum of a local file
    """

    def __init__(self, local_file_path):
        self.local_file_path = local_file_path

    def run(self) -> str:
        cmd = "sha256sum {0}".format(self.local_file_path)
        proc = subprocess.check_output(cmd, shell=True)
        if proc is None or proc is "":
            raise SystemExit("could not get sha256 sum of local file" + self.local_file_path)
        output = os.fsdecode(proc)
        hash = str(output).split(" ")[0]
        if hash is None or hash is "":
            raise SystemExit("could not read sha256 sum of local file" + self.local_file_path)
        print("detected local hash:", hash)
        return hash


class EnoughSpaceCheck:
    """
    Helper class to check if the target pod has enough physical space
    :return:
    """

    def __init__(self, context, namespace, pod, space_in_mb):
        self.context = context
        self.namespace = namespace
        self.pod = pod
        self.space_in_mb = space_in_mb

    def run(self) -> bool:
        space_check_cmd = "if [ $(df '/tmp' | awk 'END{print $4}') -le %s ]; then echo 'false'; else echo 'true';fi" % (
                self.space_in_mb * 1024)
        output = run_command_in_pod(self.context, self.namespace, self.pod,
                                    space_check_cmd)
        if output == "True":
            print("enough space available in target pod", self.pod, ",", self.space_in_mb, "MB")
        else:
            print("NOT enough space available on target pod", self.pod, ",", self.space_in_mb, "MB")
        return output == "True"


class RemoteDirExists:
    """
    Helper class to check if a remote dir exists
    """

    def __init__(self, context, namespace, pod, path):
        self.context = context
        self.namespace = namespace
        self.pod = pod
        self.path = path

    def run(self) -> bool:
        dir_exists_cmd = "if [ -d '%s' ]; then echo 'true'; else echo 'false';fi" % self.path
        output = run_command_in_pod(self.context, self.namespace, self.pod, dir_exists_cmd)
        if output == "True":
            print("Remote dir %s exists" % self.path)
        else:
            print("Remote dir %s does NOT exist" % self.path)
        return output == "True"


def main():
    pass


if __name__ == "__main__":
    main()
