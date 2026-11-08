# AWS deep-dive expansion (8 Nov 2026)

AWS for DevOps Engineers grew from 29 to about 97 minutes (56 to 181 scenes, 175 steps). Feature facts come from the AWS What's New feed (Dec 2025 to Nov 2026); CLI syntax checked against aws-cli 2.34 help pages.

| Section | Added |
|---|---|
| Account & identity | Multi-account structure, Identity Center, trust policies with OIDC `sub` pinning, policy evaluation order, SCPs, RCPs, declarative and tag policies |
| VPC deep dive (19 scenes) | CIDR planning and IPAM, route tables, NAT design, gateway vs interface endpoints, Flow Logs, Block Public Access, Encryption Controls, peering/TGW/Cloud WAN, VPC Lattice, hybrid DNS, troubleshooting, NACL rules, prefix lists, shared VPCs, inspection VPC, Network Firewall allow-lists, VPN/Direct Connect, IPv6, Traffic Mirroring |
| Route 53 deep dive (9 scenes, new) | Public/private zones and split-horizon, record types, all routing policies, health checks, multi-Region failover, DNSSEC, DNS Firewall, query logging, registrar lock, Profiles, ARC, Global Resolver |
| EC2 deep dive | Instance anatomy and naming (Graviton5 M9g), launch templates, user data, IMDSv2, Instance Connect Endpoint, EBS types, Image Builder + Inspector AMI scanning, placement groups, advanced Auto Scaling, Spot, capacity reservations, Nitro/ENIs/Elastic IPs |
| S3 deep dive (18 scenes) | Keys/prefixes, safe bucket policy, encryption options, versioning/Object Lock, lifecycle, replication, presigned URLs and conditional writes, performance, events, S3 Tables and S3 Vectors, governance, Object Ownership, VPC-only buckets, data perimeter, Access Grants, Multi-Region Access Points, secure static sites, auditing, Glacier restores |
| RDS & Aurora deep dive (15 scenes) | HA options, subnet/parameter/option groups, PITR, RDS Proxy, IAM auth, blue/green (under 5 s), Aurora architecture, Aurora DSQL, Database Insights, upgrades and Extended Support, choosing a database, layered security, encrypting an existing DB, cross-Region DR, Limitless |
| EKS deep dive (15 scenes) | Architecture, node options, Auto Mode, access entries, add-ons, VPC CNI features, Karpenter NodePool, ingress and Gateway API, storage drivers, observability, upgrades with insights and rollback, EKS Capabilities (Argo CD), security checklist, autoscaling layers, hybrid and multi-cluster |
| Serverless, messaging, IaC | ECS Express Mode, Lambda Managed Instances and durable functions, Lambda performance, API auth, SQS settings, safer CloudFormation/CDK changes |
| Security | SLOs, Security Hub exposures and SBOM, KMS key policies, edge protection, organization CloudTrail, Access Analyzer checks, Verified Access, incident response, security services map |
| Secure architectures (new) | Secure three-tier VPC, hub-and-spoke, controlled egress, fully private EKS, multi-Region active-passive, checklist |
| Putting it together | One architecture, security group chain, a request end to end, pod-to-S3 identity path, private endpoints, Terraform layout, delivery path, 3 a.m. incident |

Not verified against a live account: command outputs are representative; IDs, ARNs and timings will differ.

# Content refresh (8 Nov 2026)

Checked against GitHub releases on this date and updated in the scripts and on screen.

| Video | Change |
|---|---|
| Kubernetes | ingress-nginx retired and archived (24 Mar 2026), so the video teaches the Gateway API as the replacement. Helm 4 with an OCI chart install (`oci://ghcr.io/stefanprodan/charts/podinfo`). nginx 1.31 images. |
| CNCF | Helm 4 OCI install replaces the Bitnami repo example (Bitnami moved charts to OCI and to "Secure Images"). Crossplane v2 namespaced API (`s3.aws.m.upbound.io`). Kyverno example no longer hard-codes a version-specific enforce field. |
| Docker | Docker Engine 29.9.3 in sample output. `golang:1.27`, `python:3.14-slim`, `distroless/static-debian13`. `redis:8`, `postgres:18`. |
| Terraform | AWS provider `~> 6.0`, VPC module `~> 6.0`. S3 native locking (`use_lockfile`); DynamoDB locking described as deprecated. |
| Ansible | ansible-core 2.22.0; control node needs Python ≥ 3.13. |
| Prometheus | Prometheus 3.x noted. |
| Grafana | `grafana/grafana` image (`grafana/grafana-oss` no longer updated since 12.4.0). |
| ELK | Elastic 9.x noted. |
| Jenkins | `jenkins/jenkins:lts-jdk21`. |
| Istio | Current release 1.31 noted (ambient GA since 1.24). |
| AWS / Azure / GCP | GitHub Actions: `configure-aws-credentials@v6`, `azure/login@v3`, `google-github-actions/auth@v3`, `deploy-cloudrun@v3`. Kubernetes v1.37 in sample node output. |
| Python, App Service, Lambda | Python 3.14, Node 24 LTS runtimes. |

Not changed (still current): kind and minikube workflows, Argo CD stable manifest URL, kube-prometheus-stack chart, metrics-server flags, Bookinfo Gateway API sample path.

Not checked (this machine can reach only GitHub): cloud prices and discount percentages, certification names and codes, cloud CLI flags. Check these against vendor docs before publishing.
