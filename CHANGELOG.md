# Shell scripting deep dive: 10 to 28 minutes (9 Nov 2026)

Shell Scripting for DevOps grew from 26 to 50 scenes: how the shell expands a command, which shell to use, strict mode and its traps, quoting, parameter expansion, arrays, `[[ ]]`, heredocs, a production script built step by step (skeleton, `getopts`, atomic lock, write-then-rename, pruning), Bats tests, a mutation check, ShellCheck, CI, debugging, portability between macOS and Linux, safe building blocks, and when to move to Python or Ansible.

**Executed locally:** bash 5.2.15 (a static macOS build, because macOS ships 3.2), ShellCheck 0.11.0, shfmt 3.14.1, Bats 1.14.0. `examples/shell/backup.sh` runs for real, including its error exit codes (2 usage, 1 missing source, 3 locked) and a SIGTERM mid-backup (exit 130, lock released, no partial file, no archive). `set -e`/`pipefail`/`-u`, quoting, parameter-expansion, array and `[[ ]]` snippets were all run. ShellCheck: the script has zero findings; a deliberately bad script produced SC2035, SC2086, SC2115, SC2154, SC2164, SC2046, SC2005, SC2006. 9 of 9 Bats tests pass.

**Testing found a real bug:** the first version's exit trap removed the lock directory even when another run owned it, so a refused run could delete the running instance's lock. Fixed with an ownership flag and a Bats test; removing the fix makes exactly that test fail. Two of my own tests were also wrong at first (a background job ignores SIGINT, and one test used the wrong lock path) and were corrected before anything went into the video. **Not executed:** cron and systemd timer examples; the CI workflow is representative.

# Ansible deep dive: 10 to 29 minutes (8 Nov 2026)

Ansible from Scratch grew from 26 to 54 scenes: how a task executes, idempotency, YAML inventory and merged host variables, variable precedence, project layout, `ansible.cfg` settings, dry runs, proving idempotency, a complete role, control flow, targeting and rolling updates, Jinja2, roles vs collections, role design and argument specs, import vs include, Vault, ansible-lint, auto-fix, a test pyramid, dynamic inventory, connections without public SSH, performance, execution environments, a CI pipeline, and what changed in ansible-core 2.19 to 2.22.

**Executed locally with ansible-core 2.19.15 on localhost:** inventory graph and host vars; ad hoc `ping` and `setup`; a role with template, handler, `validate` and `assert`; `--syntax-check`; `--check --diff`; a real run (4 changes per host), an immediate re-run (**0 changes**), and a one-variable edit (only the template and handler changed); `--limit`, `--list-hosts`, `--list-tasks`; an assert failure; Vault (`encrypt`, `view`, `encrypt_string`, and the error when no password is given); variable precedence (`-e` wins even over `set_fact`); `register`, `loop`, `when`, `block`/`rescue`/`always`; 2.19 templating strictness (undefined variable fails). **ansible-lint 26.11.0:** the role and playbook pass the `production` profile with 0 failures; a deliberately bad playbook gives 14 violations; `--fix` rewrote FQCNs, `shell` to `command` and name casing.

**From changelogs only, not executed:** ansible-core 2.20, 2.21 and 2.22 features (2.22 could not run modules in the sandbox because its local RPC server is blocked). Dynamic inventory, SSM and execution-environment snippets are representative; they need cloud credentials or containers.

# Grafana deep dive: 10 to 31 minutes (8 Nov 2026)

Grafana from Scratch grew from 26 to 59 scenes: architecture and the LGTM stack, running Grafana, the query model (queries, expressions, transformations), correlations, exemplars and derived fields, `$__rate_interval`, choosing panels, thresholds and overrides, transformations, panel performance, dashboard JSON, design rules, variables, dynamic dashboards, annotations, alerting architecture, alert rules as code, notification policies, alert quality, LogQL and TraceQL, drilldown apps, Grafana Alloy, provisioning, Git Sync, Terraform/Grizzly/jsonnet, CI checks, authentication and RBAC, high availability, monitoring Grafana, the Grafana 13 breaking-changes list, and a Grafana 12 to 13.3 summary.

**Verified locally:** provisioning YAML (data sources, dashboard providers, alert rules) parses; the dashboard JSON parses; both dashboard PromQL queries were parsed with promtool 3.16 after substituting variables. **From the official Grafana 12 and 13 "What's new" pages and release notes, not executed:** all version-specific features and the 13.0 breaking-changes titles. No Grafana server could be run in the sandbox. Grafana Alloy configuration is representative and was not run.

# Prometheus deep dive: 10 to 32 minutes (8 Nov 2026)

Prometheus from Scratch grew from 26 to 59 scenes: scrape cycle and TSDB internals, staleness and `absent()`, metric design (RED/USE, naming, classic vs native histograms), relabelling and blackbox probing, PromQL in depth (rate/irate/increase, vector matching, aggregation, subqueries, alert-style queries, slow queries), SLO burn-rate alerting with unit tests, Alertmanager routing/inhibition/silences/HA, the Prometheus Operator and kube-prometheus-stack, cardinality control, remote write and long-term storage, OpenTelemetry, and a Prometheus 3.0 to 3.16 changelog summary.

**Verified by running the official tools** (promtool 3.16.0 and amtool 0.34.2, downloaded from the release pages): `promtool check config` and `check rules`; `promtool test rules` with the burn-rate alert (passes), the same test against a deliberately wrong threshold (fails, as it should), and a rule with a bad function call (rejected); `amtool check-config`; `amtool config routes test` (3 routing results shown on screen are real output); 53 PromQL expressions all parse; duration expressions, native-histogram scrape config, and `fill()` (needs `--enable-feature=promql-binop-fill-modifiers`). Five Prometheus Operator manifests validate against their CRD schemas with kubeconform. Two examples I first wrote were wrong and were corrected by promtool: duration syntax and `fill()` placement. **Not verified:** a live Prometheus server could not be reached from the sandbox, so query results shown on screen are representative.

# Linux deep dive: 20 to 49 minutes (8 Nov 2026)

Linux Commands grew from 50 to 87 scenes: boot and filesystem layout, systemd in depth (service units, sandboxing, timers, dependencies, journalctl), storage (GPT, LVM, ext4 vs XFS, finding what fills a disk, RAID, SMART, restic backups), networking (ip, nftables, DNS, a debugging ladder, tcpdump, sysctl tuning), performance (USE method, CPU/memory/disk analysis, strace, perf, eBPF), hardening (SSH, sudo, SELinux/AppArmor, audit, patching, kernel settings), containers from the kernel (namespaces, cgroups v2, capabilities, seccomp), and a troubleshooting playbook.

**Not executed:** this Mac cannot run Linux userland tools, so commands come from man pages and standard behaviour, and output shown is representative. Version-specific claims were avoided on purpose.

# Terraform deep dive: 10 to 29 minutes, plus a command verifier (8 Nov 2026)

Terraform from Scratch grew from 26 to 57 scenes. New sections: language deep dive (plan phases, validation, object types, expressions, preconditions and checks, lifecycle, for_each vs count, functions), state deep dive (inspection, S3 backend with `use_lockfile`, splitting state, `moved`, `import` and `removed` blocks, recovery), modules deep dive (interfaces, sources, layout, version pinning), testing and security (`terraform test`, mocks, policy, ephemeral values, credentials, role separation), delivery (PR pipeline, apply on merge, drift check, Terraform vs OpenTofu, actions and query, 1.10 to 1.17 summary).

**Verified by running Terraform 1.17.1 locally** (`terraform_data` resources, no cloud account): fmt, validate, plan, `terraform test` (3 of 3 pass), apply, state and output commands, import blocks with config generation, `-replace`, `-minimal-refresh`, ephemeral variables, `deprecated` variables, `convert()`. Testing against 1.17.1 corrected three claims: ephemeral outputs work in child modules only; the `terraform_data` `store` block has `input`, `output`, `replace`, `sensitive`, `sensitive_output` and `version`; `-policies` needs the `tfpolicy-plugin` binary. Not executed: Terraform Policy itself, actions, list/query against real providers, stacks.

**New tool: `tools/verify_commands.py`.** Reads every `$ command` shown in the videos and checks, against the real installed CLIs, that the subcommand exists and that every flag appears in its help page. Nothing is run against a cloud account. Results so far: kubectl 86 of 86, helm 9 of 9, aws 100 of 100, terraform 33 of 34 (the one flag, `-policies`, is real but not listed on every help page and is now allow-listed).

# Docker deep dive: 10 to 33 minutes (8 Nov 2026)

Docker from Scratch grew from 26 to 62 scenes (56 steps): container internals (namespaces, cgroups, runtime stack, PID 1), images in depth (manifests, containerd image store, tag strategy), cache-friendly and production Dockerfiles, BuildKit mounts, multi-platform builds and Bake, build checks, CI caching, network drivers and firewalls (including the experimental nftables backend), Compose profiles, Watch and CI use, security (least privilege, rootless, scan/SBOM/sign, base images, secrets, daemon hardening), health checks, logs, limits, debugging, and what changed in Engine 29. Facts come from the Docker Engine 29 release notes (29.0 to 29.9.3). `docker` and `hadolint` were not installed locally, so commands were not executed.

**Narration:** the original 26 recorded clips no longer match the longer script, so Docker now uses the browser voice. The old clips remain in `audio/docker/`; re-run `voice.py docker` to record the new script. `tools/test_site.py` now treats a video as narrated only when the build shipped its audio, so the recorded-voice playback tests are skipped until a video is re-recorded.

# Kubernetes deep dive: 10.9 to 61 minutes (8 Nov 2026)

Kubernetes from Scratch grew from 30 to 109 scenes (103 steps). Manifests shown on screen were validated with kubeconform (strict, Kubernetes 1.34 schemas plus the Gateway API CRD catalog) and `helm lint`; feature facts come from the Kubernetes 1.35, 1.36 and 1.37 changelogs. A live cluster was not available, so command output is representative.

| Section | Added |
|---|---|
| Control plane | Component roles and failure effects, the `kubectl apply` flow, the API request path (authn, authz, admission), node components, version skew, `kubectl explain` |
| Workloads deep | Pod phases, init containers and native sidecars, ephemeral containers, Deployment strategy knobs, rollout history, ReplicaSets, StatefulSets, DaemonSets, Jobs and CronJobs, indexed jobs, graceful shutdown with `preStop` sleep, QoS and OOMKilled, in-place pod resize (GA 1.35), image volumes and user namespaces (1.36) |
| Networking deep | Network model, Service types, EndpointSlices and `PreferSameZone`, CoreDNS and ndots, Gateway API roles, HTTPRoute canary, ReferenceGrant, ingress-nginx archival and migration, default-deny NetworkPolicy, CNI and mesh choices |
| Config and storage deep | ConfigMap update behaviour, Secret limits, bound service account tokens, downward API, pod certificates and ClusterTrustBundle (GA 1.37), namespace tenancy, PV/PVC/StorageClass, access modes, snapshots, ephemeral and local volumes |
| Scheduling | Filter/score/bind, placement tools, topology spread, taints, priority, PDBs and drains, autoscaling layers, gang scheduling and DRA |
| Security | Four Cs, authentication options, RBAC audit, Pod Security Standards, a hardened pod, CEL admission policy, Kyverno vs Gatekeeper, supply chain, runtime security, etcd protection |
| Operations | Debug order, Pending/ImagePull/CrashLoop/OOM, logs and events, empty endpoints, `top`, diff and server-side apply, upgrades, observability, backup and DR |
| Extending and architectures | CRDs with CEL validation, operators, Cluster API and Crossplane, Helm and Kustomize in practice, GitOps summary, production cluster, team namespace, request path, 1.35 to 1.37 what's new, checklist |

# GCP and Azure deep dives, new GitOps video (8 Nov 2026)

| Video | Before | Now | Added |
|---|---|---|---|
| Azure | 29.5 min, 56 scenes | 69.6 min, 129 scenes | Networking deep dive (UDRs, ASGs, private endpoints + DNS, Virtual WAN/AVNM, Firewall Premium, Bastion, ExpressRoute, DNS Private Resolver, VNet encryption, Network Watcher, Front Door/App Gateway, DDoS), DNS, storage, SQL/PostgreSQL/Cosmos/Managed Redis, AKS Automatic and secure Standard clusters, Key Vault, Defender, Sentinel, secure architectures |
| GCP | 29.5 min, 56 scenes | 58.5 min, 108 scenes | IAM role types, deny policies and PABs, impersonation, PAM, org policy constraints, global VPC, hierarchical firewall policies, Cloud NGFW, Cloud NAT, PSC, Shared VPC, NCC, HA VPN/Interconnect, VPC Service Controls, load balancers, Cloud Armor, IAP, Cloud DNS deep dive, Cloud Storage security, Cloud SQL/AlloyDB/Spanner, GKE security, Gateway API, KMS/Autokey, audit logs, SCC, secure architectures |
| GitOps (new) | — | 25.1 min, 45 scenes | Principles, push vs pull, source-of-truth repo design, Kustomize/Helm, PR validation, Argo CD (Applications, AppProjects, ApplicationSets, sync waves, drift, hardening), Flux (bootstrap, sources, Kustomization impersonation, OCI HelmRelease), secrets (ESO, CSI, SOPS+KMS, Sealed Secrets, in-cluster hardening), promotion (Kargo, Image Updater), Argo Rollouts, Kyverno, cosign, threats, break-glass |

Player fix: comparison tables whose rows include a label for every column now render with the header aligned to the label column (affected 80 tables across 7 videos).

Sources: Azure/AKS changelog and AKS docs; Azure CLI source for flags; Terraform Google provider docs and changelog (v8.10); Argo CD docs (v3 upgrade notes, secret management); Flux docs; GitHub releases for tool versions. `az` and `gcloud` were not installed locally, so Azure and GCP command outputs are representative.

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
