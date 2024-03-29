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
from kubernetes import client
from lib.common import SetType, load_kube

# DO NOT EDIT this file manually, use "python codegen.py" in root folder to generate and change file in "templates" folder
# Use templates/def_remove.py.j2



def remove_namespace(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for Namespace given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for Namespace given")
    if name is None:
        raise SystemExit("invalid empty name for Namespace given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespace_with_http_info(namespace)
    handle_status(ret, status, "Namespace", namespace, name)


def remove_deployment(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for Deployment given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for Deployment given")
    if name is None:
        raise SystemExit("invalid empty name for Deployment given")

    load_kube(context)
    api = client.ExtensionsV1beta1Api()
    ret, status, _ = api.delete_namespaced_deployment_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "Deployment", namespace, name)


def remove_pod(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for Pod given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for Pod given")
    if name is None:
        raise SystemExit("invalid empty name for Pod given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_pod_with_http_info(name=name, namespace=namespace)
    handle_status(ret, status, "Pod", namespace, name)


def remove_service(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for Service given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for Service given")
    if name is None:
        raise SystemExit("invalid empty name for Service given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_service_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "Service", namespace, name)


def remove_replication_controller(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for ReplicationController given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for ReplicationController given")
    if name is None:
        raise SystemExit("invalid empty name for ReplicationController given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_replication_controller_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "ReplicationController", namespace, name)


def remove_persistent_volume_claim(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for PersistentVolumeClaim given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for PersistentVolumeClaim given")
    if name is None:
        raise SystemExit("invalid empty name for PersistentVolumeClaim given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_persistent_volume_claim_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "PersistentVolumeClaim", namespace, name)


def remove_ingress(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for Ingress given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for Ingress given")
    if name is None:
        raise SystemExit("invalid empty name for Ingress given")

    load_kube(context)
    api = client.ExtensionsV1beta1Api()
    ret, status, _ = api.delete_namespaced_ingress_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "Ingress", namespace, name)


def remove_network_policy(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for NetworkPolicy given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for NetworkPolicy given")
    if name is None:
        raise SystemExit("invalid empty name for NetworkPolicy given")

    load_kube(context)
    api = client.ExtensionsV1beta1Api()
    ret, status, _ = api.delete_namespaced_network_policy_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "NetworkPolicy", namespace, name)


def remove_job(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for Job given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for Job given")
    if name is None:
        raise SystemExit("invalid empty name for Job given")

    load_kube(context)
    api = client.BatchV1Api()
    ret, status, _ = api.delete_namespaced_job_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "Job", namespace, name)


def remove_cron_job(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for CronJob given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for CronJob given")
    if name is None:
        raise SystemExit("invalid empty name for CronJob given")

    load_kube(context)
    api = client.BatchV1beta1Api()
    ret, status, _ = api.delete_namespaced_cron_job_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "CronJob", namespace, name)


def remove_config_map(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for ConfigMap given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for ConfigMap given")
    if name is None:
        raise SystemExit("invalid empty name for ConfigMap given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_config_map_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "ConfigMap", namespace, name)


def remove_secret(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for Secret given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for Secret given")
    if name is None:
        raise SystemExit("invalid empty name for Secret given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_secret_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "Secret", namespace, name)


def remove_service_account(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for ServiceAccount given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for ServiceAccount given")
    if name is None:
        raise SystemExit("invalid empty name for ServiceAccount given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_service_account_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "ServiceAccount", namespace, name)


def remove_resource_quota(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for ResourceQuota given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for ResourceQuota given")
    if name is None:
        raise SystemExit("invalid empty name for ResourceQuota given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_resource_quota_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "ResourceQuota", namespace, name)


def remove_endpoints(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for Endpoints given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for Endpoints given")
    if name is None:
        raise SystemExit("invalid empty name for Endpoints given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_endpoints_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "Endpoints", namespace, name)


def remove_pod_template(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for PodTemplate given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for PodTemplate given")
    if name is None:
        raise SystemExit("invalid empty name for PodTemplate given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_pod_template_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "PodTemplate", namespace, name)


def remove_role_binding(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for RoleBinding given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for RoleBinding given")
    if name is None:
        raise SystemExit("invalid empty name for RoleBinding given")

    load_kube(context)
    api = client.RbacAuthorizationV1Api()
    ret, status, _ = api.delete_namespaced_role_binding_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "RoleBinding", namespace, name)


def remove_role(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for Role given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for Role given")
    if name is None:
        raise SystemExit("invalid empty name for Role given")

    load_kube(context)
    api = client.RbacAuthorizationV1Api()
    ret, status, _ = api.delete_namespaced_role_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "Role", namespace, name)


def remove_pod_disruption_budget(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for PodDisruptionBudget given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for PodDisruptionBudget given")
    if name is None:
        raise SystemExit("invalid empty name for PodDisruptionBudget given")

    load_kube(context)
    api = client.PolicyV1beta1Api()
    ret, status, _ = api.delete_namespaced_pod_disruption_budget_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "PodDisruptionBudget", namespace, name)


def remove_event(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for Event given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for Event given")
    if name is None:
        raise SystemExit("invalid empty name for Event given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_event_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "Event", namespace, name)


def remove_lease(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for Lease given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for Lease given")
    if name is None:
        raise SystemExit("invalid empty name for Lease given")

    load_kube(context)
    api = client.CoordinationV1beta1Api()
    ret, status, _ = api.delete_namespaced_lease_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "Lease", namespace, name)


def remove_horizontal_pod_autoscaler(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for HorizontalPodAutoscaler given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for HorizontalPodAutoscaler given")
    if name is None:
        raise SystemExit("invalid empty name for HorizontalPodAutoscaler given")

    load_kube(context)
    api = client.AutoscalingV1Api()
    ret, status, _ = api.delete_namespaced_horizontal_pod_autoscaler_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "HorizontalPodAutoscaler", namespace, name)


def remove_controller_revision(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for ControllerRevision given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for ControllerRevision given")
    if name is None:
        raise SystemExit("invalid empty name for ControllerRevision given")

    load_kube(context)
    api = client.AppsV1Api()
    ret, status, _ = api.delete_namespaced_controller_revision_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "ControllerRevision", namespace, name)


def remove_limit_range(context, namespace, name):
    if context is None:
        raise SystemExit("invalid empty context for LimitRange given")
    if namespace is None:
        raise SystemExit("invalid empty namespace for LimitRange given")
    if name is None:
        raise SystemExit("invalid empty name for LimitRange given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_namespaced_limit_range_with_http_info(name, namespace=namespace)
    handle_status(ret, status, "LimitRange", namespace, name)


def remove_cluster_role(context, name):
    if context is None:
        raise SystemExit("invalid empty context for ClusterRole given")
    if name is None:
        raise SystemExit("invalid empty name for ClusterRole given")

    load_kube(context)
    api = client.RbacAuthorizationV1Api()
    ret, status, _ = api.delete_cluster_role_with_http_info(name)
    handle_status(ret, status, "ClusterRole", None, name)


def remove_cluster_role_binding(context, name):
    if context is None:
        raise SystemExit("invalid empty context for ClusterRoleBinding given")
    if name is None:
        raise SystemExit("invalid empty name for ClusterRoleBinding given")

    load_kube(context)
    api = client.RbacAuthorizationV1Api()
    ret, status, _ = api.delete_cluster_role_binding_with_http_info(name)
    handle_status(ret, status, "ClusterRoleBinding", None, name)


def remove_pod_security_policy(context, name):
    if context is None:
        raise SystemExit("invalid empty context for PodSecurityPolicy given")
    if name is None:
        raise SystemExit("invalid empty name for PodSecurityPolicy given")

    load_kube(context)
    api = client.PolicyV1beta1Api()
    ret, status, _ = api.delete_pod_security_policy_with_http_info(name)
    handle_status(ret, status, "PodSecurityPolicy", None, name)


def remove_persistent_volume(context, name):
    if context is None:
        raise SystemExit("invalid empty context for PersistentVolume given")
    if name is None:
        raise SystemExit("invalid empty name for PersistentVolume given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_persistent_volume_with_http_info(name)
    handle_status(ret, status, "PersistentVolume", None, name)


def remove_volume_attachment(context, name):
    if context is None:
        raise SystemExit("invalid empty context for VolumeAttachment given")
    if name is None:
        raise SystemExit("invalid empty name for VolumeAttachment given")

    load_kube(context)
    api = client.StorageV1Api()
    ret, status, _ = api.delete_volume_attachment_with_http_info(name)
    handle_status(ret, status, "VolumeAttachment", None, name)


def remove_storage_class(context, name):
    if context is None:
        raise SystemExit("invalid empty context for StorageClass given")
    if name is None:
        raise SystemExit("invalid empty name for StorageClass given")

    load_kube(context)
    api = client.StorageV1Api()
    ret, status, _ = api.delete_storage_class_with_http_info(name)
    handle_status(ret, status, "StorageClass", None, name)


def remove_priority_class(context, name):
    if context is None:
        raise SystemExit("invalid empty context for PriorityClass given")
    if name is None:
        raise SystemExit("invalid empty name for PriorityClass given")

    load_kube(context)
    api = client.SchedulingV1beta1Api()
    ret, status, _ = api.delete_priority_class_with_http_info(name)
    handle_status(ret, status, "PriorityClass", None, name)


def remove_node(context, name):
    if context is None:
        raise SystemExit("invalid empty context for Node given")
    if name is None:
        raise SystemExit("invalid empty name for Node given")

    load_kube(context)
    api = client.CoreV1Api()
    ret, status, _ = api.delete_node_with_http_info(name)
    handle_status(ret, status, "Node", None, name)


def remove_custom_resource_definition(context, name):
    if context is None:
        raise SystemExit("invalid empty context for CustomResourceDefinition given")
    if name is None:
        raise SystemExit("invalid empty name for CustomResourceDefinition given")

    load_kube(context)
    api = client.ApiextensionsV1beta1Api()
    ret, status, _ = api.delete_custom_resource_definition_with_http_info(name)
    handle_status(ret, status, "CustomResourceDefinition", None, name)


def remove_certificate_signing_request(context, name):
    if context is None:
        raise SystemExit("invalid empty context for CertificateSigningRequest given")
    if name is None:
        raise SystemExit("invalid empty name for CertificateSigningRequest given")

    load_kube(context)
    api = client.CertificatesV1beta1Api()
    ret, status, _ = api.delete_certificate_signing_request_with_http_info(name)
    handle_status(ret, status, "CertificateSigningRequest", None, name)


def remove_set(context, namespace, set_type: SetType, set_name: str):
    load_kube(context)
    api = client.AppsV1Api()
    print("remove set of type", set_type, "and name", set_name, "in namespace", namespace)

    if not isinstance(set_type, SetType):
        raise SystemExit("invalid set type", set_type, "given")

    if set_type == SetType.replica_set:
        ret, status, _ = api.delete_namespaced_replica_set_with_http_info(set_name, namespace=namespace)
    elif set_type == SetType.stateful_set:
        ret, status, _ = api.delete_namespaced_stateful_set_with_http_info(set_name, namespace=namespace)
    elif set_type == SetType.daemon_set:
        ret, status, _ = api.delete_namespaced_daemon_set_with_http_info(set_name, namespace=namespace)
    else:
        raise SystemExit("invalid type", set_type)

    handle_status(ret, status, set_type, namespace, set_name)
# internal method (used above)


def handle_status(ret, status, object_name, namespace, name):
    print("returned status code:", status)
    if status != None and status == 200:
        print("successfully removed", object_name, name, "in namespace", namespace)
        return
    else:
        print(ret)
    raise SystemExit("error killing", object_name, name, "in namespace", namespace)


def main():
    pass


if __name__ == "__main__":
    main()