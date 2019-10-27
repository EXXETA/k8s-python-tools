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
import time

from kubernetes import stream, client
from kubernetes.client.apis import core_v1_api
from kubernetes.client.rest import ApiException

from lib.common import load_kube

JOB_COMPLETION_WAIT_LIMIT = 3600

init_exec_command = ['/bin/sh']


def run_command_in_pod(context, namespace, pod, command):
    """
    returns string or None on failure

    :param context:
    :param namespace:
    :param pod:
    :param command:
    :return:
    """
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


def apply_kube_yaml(context, abs_file_location):
    if context is None:
        raise SystemExit('Null context given')
    load_kube(context)
    apply_cmd = "kubectl apply -f {0} --context {1}".format(abs_file_location, context)
    print('Executing cmd: %s' % apply_cmd)
    output = subprocess.check_output(apply_cmd, shell=True)
    print(str(bytes(output), 'utf-8'))


def get_pod_logs(context, namespace, pod) -> str:
    if context is None:
        raise SystemExit('Null context given')
    if namespace is None:
        raise SystemExit('Null namespace given')
    if pod is None:
        raise SystemExit('Null pod given')

    load_kube(context)
    try:
        api_instance = client.CoreV1Api()
        api_response = api_instance.read_namespaced_pod_log(name=pod, namespace=namespace)
        return api_response
    except ApiException as e:
        print('Found exception in reading the logs')


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


def verify_container_image(context, namespace, pod, valid_image_names):
    cmd = "kubectl get pod -n {0} {1} --context {2}".format(namespace, pod, context) \
          + " -o jsonpath='{$.spec.containers[].image}'"
    print("executing: ", cmd)
    process = subprocess.check_output(cmd, shell=True)

    container_image_name = process.decode('utf-8')
    print('received image name: "%s"' % container_image_name)

    if len(container_image_name) == 0:
        print('INVALID empty container image found!')
        return False

    for allowed_version in valid_image_names:
        if allowed_version in container_image_name:
            print('found VALID container image: "%s"' % container_image_name)
            return True

    print('INVALID image name "%s"' % container_image_name)
    return False


def check_file_for_regex_content(context, namespace, pod, abs_file_name, checked_content_re):
    import re
    cmd = "kubectl exec --context {0} -n {1} {2} cat \"{3}\"".format(context, namespace, pod, abs_file_name)
    print('executing cmd: %s' % cmd)
    print('looking for regex: %s in file %s' % (checked_content_re, abs_file_name))
    output = subprocess.check_output(cmd, shell=True)
    matches = re.search(checked_content_re, str(output, 'utf-8'), re.MULTILINE)
    return matches is not None


def get_pvc_size(context, namespace, pvc):
    cmd = "kubectl get pvc {0} -n {1} --context {2} " \
              .format(pvc, namespace, context) + "-o jsonpath='{$.status.capacity.storage}'"
    print("executing cmd: %s" % cmd)
    output = subprocess.check_output(cmd, shell=True)
    return str(bytes(output), "utf-8")


def get_configmap_content(context, namespace, cm, filename) -> str:
    cmd = 'kubectl get cm -n {0} {1} --context {2}'.format(namespace, cm, context) + (
            ' -o jsonpath="{$.data.%s}"' % filename)
    print('executing cmd: %s' % cmd)
    output = subprocess.check_output(cmd, shell=True)

    if output is None or output == "":
        raise SystemExit('Could not fetch content of configmap %s in namespace %s' % (cm, namespace))
    return str(bytes(output), 'utf-8')


def is_helm_release_live(release_name) -> bool:
    cmd = 'helm ls --deployed {0} --tiller-namespace default'.format(release_name)
    print('executing cmd: %s' % cmd)
    output = subprocess.check_output(cmd, shell=True)
    out = str(bytes(output), 'utf-8').strip()
    if output is None or len(out) == 0:
        # ensure its really removed
        cmd2 = 'helm del --purge {0} --tiller-namespace default'.format(release_name)
        try:
            output2 = subprocess.check_output(cmd2, shell=True)
        except subprocess.CalledProcessError:
            pass
        return False
    print(out)
    return True


def wait_for_pod_is_running_and_ready(context, namespace, pod):
    print('Checking if pod is ready')
    running_cmd = 'kubectl get pod --context {0} -n {1} {2}'.format(context, namespace, pod) \
                  + ' -o jsonpath="{$.metadata.deletionTimestamp}"'
    print('executing cmd: %s' % running_cmd)
    _wait_for_output_or_fail(running_cmd, 90, b'', 'waiting for pod %s is not terminating' % pod,
                             'could not check for pod being terminating!')
    print('Pod is NOT (or no longer) terminating')

    running_cmd = 'kubectl get pod --context {0} -n {1} {2}'.format(context, namespace, pod) \
                  + ' -o jsonpath="{$.status.phase}"'
    print('executing cmd: %s' % running_cmd)
    _wait_for_output_or_fail(running_cmd, 180, b'Running', 'waiting for pod %s is running' % pod,
                             'could not check for pod being in phase running!')
    print('Pod is running')
    cmd = 'kubectl get pod --context {0} -n {1} {2}'.format(context, namespace, pod) \
          + ' -o jsonpath="{$.status.containerStatuses[].ready}"'
    print('executing cmd: %s' % cmd)
    _wait_for_output_or_fail(cmd, 180, b'true', 'waiting for pod %s is ready' % pod,
                             'could not check for pod being ready!')
    print('Pod is ready')


def wait_for_job_is_completed(context, namespace, job):
    print('Check for job %s is completed' % job)
    cmd = 'kubectl get job --context {0} -n {1} {2}'.format(context, namespace, job) \
          + ' -o jsonpath="{$.status.conditions[].type}"'
    print('executing cmd: %s' % cmd)
    _wait_for_output_or_fail(cmd, JOB_COMPLETION_WAIT_LIMIT, b'Complete', 'waiting for job %s is completed' % job,
                             'could not check for job being completed!')
    print('Job is completed')


def wait_for_pvc_is_bound(context, namespace, pvc):
    print('Check for pvc %s is bound' % pvc)
    cmd = 'kubectl get pvc --context {0} -n {1} {2}'.format(context, namespace, pvc) \
          + ' -o jsonpath="{$.status.phase}"'
    print('executing cmd: %s' % cmd)
    _wait_for_output_or_fail(cmd, 600, b'Bound', 'waiting for pvc %s is bound' % pvc,
                             'could not check for pvc being bound!')
    print('PVC is bound')


def get_nfs_path(context, pv_name) -> str:
    print('Detecting nfs path')
    cmd = 'kubectl get pv --context {0} {1}'.format(context, pv_name) \
          + ' -o jsonpath="{.spec.nfs.path}"'
    print('executing cmd: %s' % cmd)
    o = subprocess.check_output(cmd, shell=True)
    s = str(bytes(o), 'utf-8')
    print('Detected nfs path: %s' % s)
    if s is None or s == '':
        raise SystemExit('invalid nfs path')
    return s


def get_nfs_server(context, pv_name) -> str:
    print('Detecting nfs server')
    cmd = 'kubectl get pv --context {0} {1}'.format(context, pv_name) \
          + ' -o jsonpath="{.spec.nfs.server}"'
    print('executing cmd: %s' % cmd)
    o = subprocess.check_output(cmd, shell=True)
    s = str(bytes(o), 'utf-8')
    print('Detected nfs server: %s' % s)
    if s is None or s == '':
        raise SystemExit('invalid nfs server')
    return s


def _wait_for_output_or_fail(cmd, limit_seconds, search_string, wait_msg, err_msg):
    """
    Only internal use
    :param cmd:
    :param limit_seconds:
    :param search_string:
    :param wait_msg:
    :param err_msg:
    :return:
    """
    output = subprocess.check_output(cmd, shell=True)
    counter = 0
    while output != search_string:
        output = subprocess.check_output(cmd, shell=True)
        if counter % 5 == 0:
            print(wait_msg)
        time.sleep(1)
        if counter >= limit_seconds:
            raise SystemExit(err_msg)
        counter += 1


def main():
    pass


if __name__ == "__main__":
    main()
