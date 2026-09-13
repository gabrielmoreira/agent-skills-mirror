---
name: implementing-container-network-policies-with-calico
description: Enforces Kubernetes network segmentation by creating and auditing Calico
  NetworkPolicy and GlobalNetworkPolicy resources via calicoctl and the Kubernetes
  API, controlling pod-to-pod traffic, namespace isolation, egress restrictions, and
  DNS-based rules. Use when implementing zero-trust microsegmentation in a Calico-CNI
  cluster or hardening pod-to-pod and egress traffic controls.
domain: cybersecurity
subdomain: container-security
tags:
- container-security
- kubernetes
- calico
- network-policy
- microsegmentation
- cni
version: '1.0'
author: mahipal
license: Apache-2.0
nist_csf:
- PR.PS-01
- PR.IR-01
- ID.AM-08
- DE.CM-01
mitre_attack:
- T1610
- T1611
- T1609
- T1525
---
# Implementing Container Network Policies with Calico

## Overview

Calico provides Kubernetes-native and extended network policy enforcement through its CNI plugin. This skill covers creating and auditing Calico NetworkPolicy and GlobalNetworkPolicy resources to implement pod-to-pod traffic control, namespace isolation, egress restrictions, and DNS-based policy rules using calicoctl and the Kubernetes API.


## When to Use

- When deploying or configuring implementing container network policies with calico capabilities in your environment
- When establishing security controls aligned to compliance requirements
- When building or improving security architecture for this domain
- When conducting security assessments that require this implementation

## Prerequisites

- Kubernetes cluster with Calico CNI installed
- Python 3.9+ with `kubernetes` client library
- calicoctl CLI tool installed and configured
- kubectl access with RBAC permissions for network policy management

## Steps

### Step 1: Audit Existing Network Policies
Use calicoctl and kubectl to inventory current network policies and identify unprotected namespaces.

### Step 2: Implement Default-Deny Policies
Create default-deny ingress and egress policies per namespace as a zero-trust baseline.

### Step 3: Create Workload-Specific Allow Rules
Define granular allow rules for legitimate pod-to-pod and pod-to-service communication.

### Step 4: Validate Policy Enforcement
Test connectivity between pods to verify policies are correctly enforced.

## Expected Output

JSON audit report listing all network policies, unprotected namespaces, policy rule counts, and connectivity test results.
