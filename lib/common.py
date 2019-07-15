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
from abc import abstractmethod, ABC
from enum import Enum
from typing import Iterable

from jinja2 import Environment, FileSystemLoader, select_autoescape, meta
from kubernetes import client, config

from lib.input import get_current_input_adapter

current_context = None


def load_kube(context):
    global current_context
    if current_context is not context:
        print("Loading context: ", context)
    config.load_kube_config(context=context)
    current_context = context


def choose_context_and_namespace(given_context=None, given_namespace=None) -> (str, str):
    context = choose_context(given_context)

    # namespace
    if given_namespace is None:
        print("get namespace from user input")
        from lib.confirmer import confirm_namespace
        ns = confirm_namespace(context, show_warning=False)
    else:
        ns = given_namespace

    if ns is None:
        raise SystemExit("No namespace found! Probably not connected to Kubernetes Cluster...")

    print("Using namespace:", ns)
    return context, ns


def choose_context(given_context=None) -> str:
    # use context from args or user has to choose
    if given_context is None:
        from lib.confirmer import confirm_context
        context = confirm_context()
    else:
        context = given_context
    print("Using context", context)

    if context is None:
        raise SystemExit("No context found! Probably invalid configuration...")

    # TODO basic (network) connection check before this step happens
    # load context
    load_kube(context)
    return context


class SetType(Enum):
    replica_set = 'ReplicaSet'
    stateful_Set = 'StatefulSet'
    daemon_set = 'DaemonSet'

    def __str__(self):
        return self.value


def detect_set_type(namespaced_set) -> SetType:
    if isinstance(namespaced_set, client.models.v1_replica_set.V1ReplicaSet):
        return SetType.replica_set
    if isinstance(namespaced_set, client.models.v1_stateful_set.V1StatefulSet):
        return SetType.stateful_Set
    if isinstance(namespaced_set, client.models.v1_daemon_set.V1DaemonSet):
        return SetType.daemon_set
    raise SystemExit("Invalid type for set", namespaced_set)


def get_sets(context, namespace) -> list:
    if namespace is None:
        raise BaseException("null namespace")

    load_kube(context)
    api = client.AppsV1Api()
    set_list = list()
    # replica
    replica_sets = api.list_namespaced_replica_set(namespace=namespace)
    if replica_sets:
        for i in replica_sets.items:
            set_list.append(i)

    # stateful
    stateful_sets = api.list_namespaced_stateful_set(namespace=namespace)
    if stateful_sets:
        for i in stateful_sets.items:
            set_list.append(i)

    # daemon
    daemon_sets = api.list_namespaced_daemon_set(namespace=namespace)
    if daemon_sets:
        for i in daemon_sets.items:
            set_list.append(i)
    return set_list


# this class represents an abstraction of command line arguments
# if you add a property, also modify this method: build_args
# TODO automate these two steps per new k8s resource object
class ArgumentConfig:
    context = False
    namespace = False
    pod = False
    deployment = False
    service = False
    service_account = False
    resource_quota = False
    replication_controllers = False
    endpoints = False
    pod_template = False
    pod_security_policy = False
    persistent_volume = False
    persistent_volume_claim = False
    ingress = False
    network_policy = False
    job = False
    config_map = False
    secret = False
    set_type = False
    set_name = False
    no_wait = False
    role_binding = False
    role = False
    pod_disruption_budget = False
    event = False
    lease = False
    horizontal_pod_autoscaler = False
    controller_revision = False
    limit_range = False
    cluster_role = False
    cluster_role_binding = False
    volume_attachment = False
    storage_class = False
    priority_class = False
    node = False
    custom_resource_definition = False
    certificate_signing_request = False


class CustomParameter:
    name = ""
    help = ""
    input_type = ""

    def __init__(self, name, help, input_type, required=True, dependency=None, prompt=False, default=None, multi=False):
        self.name = name
        self.help = help
        self.input_type = input_type
        self.required = required
        self.dependency = dependency
        self.prompt = prompt
        self.default = default
        self.multi = multi


class AbstractCommand(ABC):

    def __init__(self):
        split = self.get_command().split(" ")
        if len(split) < 2:
            raise SystemExit("invalid command given")
        self.subcommand = split[0]
        self.subsubcommand = split[1]

    @abstractmethod
    def get_command(self) -> str:
        ...

    @abstractmethod
    def get_attr_config(self) -> ArgumentConfig:
        ...

    @abstractmethod
    def run(self, args):
        ...

    def get_additional_attr_config(self) -> Iterable[CustomParameter]:
        pass

    def check_args(self, args) -> bool:
        config = self.get_additional_attr_config()
        if config is None:
            return False

        for i in config:
            if i.required and vars(args)[i.name] is None:
                return False
        return True

    def print_args(self, args):
        config = self.get_additional_attr_config()
        if config is None:
            return False

        str = ""
        for i in config:
            arg_key = vars(args)[i.name]
            if arg_key is not None:
                str += i.name + ": " + arg_key + "\n"
        print(str)

    # the following method does the "magic" of adding the defined arguments to a cmd
    # TODO consistent definition + docs of shortcuts
    def build_args(self, argument_config: ArgumentConfig, parser):
        group = parser.add_argument_group("optional")

        if argument_config.context:
            group.add_argument("--context", "-c", type=str, help="a name of the cluster to work on")
        if argument_config.namespace:
            group.add_argument("--namespace", "-n", type=str, help="a namespace name")
        if argument_config.pod:
            group.add_argument("--pod", "-p", type=str, help="a name of a pod")
        if argument_config.deployment:
            group.add_argument("--deployment", "-d", help="a name of a deployment", type=str)
        if argument_config.service:
            group.add_argument("--service", "-s", help="a name of a Service", type=str)
        if argument_config.replication_controllers:
            group.add_argument("--replication-controller", "-rc", help="a name of a ReplicationController", type=str)
        if argument_config.set_type:
            group.add_argument("--set-type", "-st", type=SetType, help="a SetType", choices=list(SetType))
        if argument_config.set_name:
            group.add_argument("--set-name", "-sn", help="a name of a Set", type=str)
        if argument_config.no_wait:
            group.add_argument("--no-wait", "-nw", type=bool, help="true, false")
        if argument_config.persistent_volume_claim:
            group.add_argument("--persistent-volume-claim", "-pvc", help="a name of a PersistentVolumeClaim", type=str)
        if argument_config.persistent_volume:
            group.add_argument("--persistent-volume", help="a name of a PersistentVolume", type=str)
        if argument_config.ingress:
            group.add_argument("--ingress", help="a name of a Ingress", type=str)
        if argument_config.network_policy:
            group.add_argument("--network-policy", help="a name of a NetworkPolicy", type=str)
        if argument_config.job:
            group.add_argument("--job", help="a name of a Job", type=str)
        if argument_config.config_map:
            group.add_argument("--config-map", help="a name of a ConfigMap", type=str)
        if argument_config.secret:
            group.add_argument("--secret", help="a name of a Secret", type=str)
        if argument_config.service_account:
            group.add_argument("--service-account", help="a name of a ServiceAccount", type=str)
        if argument_config.resource_quota:
            group.add_argument("--resource-quota", help="a name of a ResourceQuota", type=str)
        if argument_config.endpoints:
            group.add_argument("--endpoints", help="a name of an Endpoint", type=str)
        if argument_config.pod_template:
            group.add_argument("--pod-template", help="a name of a PodTemplate", type=str)
        if argument_config.pod_security_policy:
            group.add_argument("--pod-security-policy", help="a name of a PodSecurityPolicy", type=str)
        if argument_config.role_binding:
            group.add_argument("--role-binding", help="a name of a RoleBinding", type=str)
        if argument_config.role_binding:
            group.add_argument("--role", help="a name of a Role", type=str)
        if argument_config.pod_disruption_budget:
            group.add_argument("--pod-disruption-budget", help="a name of a PodDisruptionBudget", type=str)
        if argument_config.event:
            group.add_argument("--event", help="a name of an Event", type=str)
        if argument_config.lease:
            group.add_argument("--lease", help="a name of a Lease", type=str)
        if argument_config.horizontal_pod_autoscaler:
            group.add_argument("--horizontal-pod-autoscaler", help="a name of a HorizontalPodAutoscaler", type=str)
        if argument_config.controller_revision:
            group.add_argument("--controller-revision", help="a name of a ControllerRevision", type=str)
        if argument_config.limit_range:
            group.add_argument("--limit-range", help="a name of a LimitRange", type=str)
        if argument_config.cluster_role:
            group.add_argument("--cluster-role", help="a name of a ClusterRole", type=str)
        if argument_config.cluster_role_binding:
            group.add_argument("--cluster-role-binding", help="a name of a ClusterRoleBinding", type=str)
        if argument_config.volume_attachment:
            group.add_argument("--volume-attachment", help="a name of a VolumeAttachment", type=str)
        if argument_config.storage_class:
            group.add_argument("--storage-class", help="a name of a StorageClass", type=str)
        if argument_config.priority_class:
            group.add_argument("--priority-class", help="a name of a PriorityClass", type=str)
        if argument_config.node:
            group.add_argument("--node", help="a name of a Node", type=str)
        if argument_config.certificate_signing_request:
            group.add_argument("--certificate-signing-request", "-csr", help="a name of a CertificateSigningRequest", type=str)


class DynamicArgs(object):
    """
    This class enables a mechanism to work with CustomParameter classes and defines the auto-input of the missing
    values.
    """
    INPUT_TYPE_CONTEXT = "context"
    INPUT_TYPE_NAMESPACE = "namespace"
    INPUT_TYPE_POD = "pod"
    INPUT_TYPE_PATH = "path"

    def __init__(self, context, real_args, defined_args: Iterable[CustomParameter]):
        self.context = context
        self.all_args = self.merge(real_args, defined_args)
        self.validate_and_input(defined_args)
        self.print_cli_cmd(defined_args)

    def val(self, key):
        if key in self.all_args.keys():
            return self.all_args[key]
        else:
            return None

    def merge(self, real_args, defined_args):
        given_args = dict()
        arg_keys = vars(real_args)
        for cp in defined_args:
            if cp.name in arg_keys:
                given_args[cp.name] = arg_keys[cp.name]
        return given_args

    def validate_and_input(self, defined_args):
        """
        This method processes available CustomParameter instances

        :param defined_args:
        :return:
        """
        for cp in defined_args:
            if (cp.required is True or cp.prompt is True) and self.all_args[cp.name] is None:
                self.prompt_for_user_input(cp)
            else:
                self.handle_available_and_default(cp)
        for cp in defined_args:
            if cp.required is True and self.all_args[cp.name] is None:
                raise SystemExit("invalid arguments given in field " + cp.name)

    def handle_available_and_default(self, cp):
        value = self.all_args[cp.name]
        if value is not None:
            print(cp.name, "parameter is already available. Value:", value)

            if cp.input_type is self.INPUT_TYPE_PATH:
                # modify path input
                self.all_args[cp.name] = self.handle_path_input(value)
        else:
            # apply default value for not-prompted params
            if cp.default is not None:
                self.all_args[cp.name] = cp.default
            print(cp.name, "parameter is skipped")

    def prompt_for_user_input(self, cp):
        from lib.confirmer import confirm_namespace, confirm_pod

        # apply default values
        default_value = ""
        if cp.default is not None:
            self.all_args[cp.name] = cp.default
            default_value += "[default:" + cp.default + "]"
        print("Missing value:", cp.name, "-", cp.help)
        if cp.input_type == self.INPUT_TYPE_CONTEXT:
            from lib.confirmer import confirm_context
            self.all_args[cp.name] = confirm_context()
        elif cp.input_type == self.INPUT_TYPE_NAMESPACE:
            # no support for default value of namespaced parameter
            self.all_args[cp.name] = confirm_namespace(self.context)
        elif cp.input_type == self.INPUT_TYPE_POD:
            namespace = self.all_args[cp.dependency]
            if namespace is None or namespace is "":
                raise SystemExit("missing namespace value in field " + cp.dependency)
            returned_pod = confirm_pod(self.context, namespace)
            if cp.default is not None and (returned_pod is "" or returned_pod is None):
                returned_pod = cp.default
            self.all_args[cp.name] = returned_pod
        elif cp.input_type == self.INPUT_TYPE_PATH:
            self.ask_for_path_value(cp)
        elif cp.input_type is str:
            returned_str = prompt_string("Input " + cp.help + " " + default_value + ":")
            if cp.default is not None and (returned_str is None or returned_str is ""):
                returned_str = cp.default
            self.all_args[cp.name] = returned_str
        elif cp.input_type is int:
            returned_int = prompt_string("Input " + cp.help + "" + default_value + ":")
            if cp.default is not None and (returned_int is not None and returned_int is ""):
                returned_int = cp.default
            self.all_args[cp.name] = str(returned_int)
        else:
            raise SystemExit("invalid not implemented input_type", cp.input_type)

    def ask_for_path_value(self, cp):
        while True:
            path = prompt_string("input a valid ret_path:")
            ret_path = self.handle_path_input(path)
            if os.path.exists(os.path.join(ret_path)):
                print("using the following path value", ret_path)
                self.all_args[cp.name] = ret_path
                break
            else:
                print("invalid value for path", "'" + ret_path + "'")

    def handle_path_input(self, path):
        if path.startswith("./"):
            path = path.replace("./", os.getcwd(), count=1)

        if path.startswith("~"):
            from os.path import expanduser
            path = path.replace("~", expanduser("~"), count=1)
        ret_path = path
        return ret_path

    def print_cli_cmd(self, defined_args):
        out = ""
        for cp in defined_args:
            val = self.all_args[cp.name]
            if val is not None:
                out += " --" + cp.name
                if isinstance(val, list):
                    for i in val:
                        out += " " + i
                else:
                    out += " " + str(val)
                if str(val) is "":
                    out += "''"
        if out is not "":
            print("------")
            print("Command line arguments:")
            print(out)
            print("-----")


class YamlTemplateRunner:
    """
    Uses a template path and file name to detect the missing template variables and asks the user for input values.
    """

    def __init__(self, path, tpl_file_name, slug):
        self.path = path
        self.tpl_file_name = tpl_file_name
        self.slug = slug

        join = os.path.join(path, tpl_file_name)
        if not os.path.isfile(join):
            print("Invalid file name", tpl_file_name, "in path", path)
            self.tpl = None
            return

        env = Environment(
            loader=FileSystemLoader(path),
            autoescape=select_autoescape(['html', 'xml'])
        )
        ast = env.parse(self.read_raw_template())
        tpl_vars = dict()
        for i in meta.find_undeclared_variables(ast):
            print("missing value for template variable", "'" + i + "'")
            tpl_vars[i] = prompt_string("Input value for '" + i + "':")

        self.rendered_tpl = self.write_generated_template(env, tpl_vars)

    def write_generated_template(self, env, tpl_vars) -> str:
        self.tpl = env.get_template(self.tpl_file_name).render(tpl_vars)
        tpl_file_path = os.path.join(self.path, self.tpl_file_name)
        file_name = os.path.splitext(tpl_file_path)[0]
        dest_yml_file = os.path.join(self.path, file_name + "-" + self.slug + ".yml")
        with open(dest_yml_file, 'w') as file:
            file.write(self.tpl)
        return dest_yml_file

    def read_raw_template(self):
        with open(os.path.join(self.path, self.tpl_file_name), 'r') as file:
            data = file.read().replace('\n', '')
            return data

    def is_ready(self) -> bool:
        return self.tpl is not None


def confirm_string(title, message) -> str:
    input_adapter = get_current_input_adapter()
    return input_adapter.string(title, message)


def confirm_number(title, message) -> int:
    input_adapter = get_current_input_adapter()
    return input_adapter.number(title, message)


def prompt_string(title) -> str:
    input_adapter = get_current_input_adapter()
    return input_adapter.prompt(title)


def main():
    pass


if __name__ == "__main__":
    main()
