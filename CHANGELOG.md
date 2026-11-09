# CNCF deep dive: 10 to 25 minutes (9 Nov 2026)

The CNCF Landscape video grew from 26 to 45 scenes: maturity levels with real counts, which popular tools are not CNCF projects, what graduated since 2025, versions of the core projects, Helm in practice, Gateway API with cert-manager, Cilium, Argo CD vs Flux, KEDA, the observability picture, Kyverno, OPA, cosign, Gatekeeper vs Kyverno, Crossplane v2, Backstage, an adoption order, a due-diligence checklist and a final checklist. Reference files are in `examples/cncf/`.

**Facts come from the live cncf/landscape `landscape.yml` (last commit 9 Nov 2026):** 41 graduated, 38 incubating, 154 sandbox, 28 archived, and the exact accepted, incubating and graduated dates of every project named. Latest releases come from the GitHub API on 9 Nov 2026. **Recent graduations now reflected:** in-toto (Feb 2025), Knative (Sep 2025), Crossplane (Oct 2025), Kyverno (16 Mar 2026), OpenTelemetry (11 May 2026), Buildpacks (17 Jul 2026), KubeVirt (4 Nov 2026). **Checked against the landscape and corrected:** CRI-O graduated in July 2023 (I had first written the 2019 acceptance date); Sigstore/cosign, Trivy, Flagger and Grafana are not CNCF projects.

**Executed locally:** 13 manifests validated with kubeconform on Kubernetes 1.34 against the CRD catalog (12 valid, 1 skipped); OPA 1.22.2 (`opa check --strict`, `opa fmt`, 3 unit tests pass, a mutation makes 2 of 3 fail; older Gatekeeper-style Rego fails under OPA v1 defaults and needs `--v0-compatible`); Kyverno CLI 1.13.4 (`kyverno apply` on 3 pods: 1 pass, 2 fail with exact paths); cosign v2.5.0 (key pair, `sign-blob`, `verify-blob` OK, then a tamper makes it fail); helm 3.16.2 against the real charts (cert-manager renders **0 CRDs unless `crds.enabled=true`**; chart versions read; Cilium, KEDA and Kyverno chart values checked).

**Not executed:** nothing was installed into a cluster (none available; Docker has no daemon; kind is not installed), cosign keyless signing was not run (needs network and an OIDC login), and the Gatekeeper constraint could not be schema-validated without its template.

# ELK deep dive: 10 to 26 minutes (9 Nov 2026)

The ELK Stack from Scratch grew from 26 to 47 scenes: the data path and versions, a tested Filebeat configuration, what Filebeat refuses, Kubernetes autodiscover, the module list, grok on a real access log with its real output, the pipeline that produced it, structured JSON, config validation, Logstash tuning, data streams, the failure store, an ILM policy, search and ES|QL, Kibana, alerting on the pipeline itself, sizing, a security baseline, shipper choices, a 9.1 to 9.5 summary, and a checklist. Reference files and the real outputs are in `examples/elk/`.

**Executed with the official 9.5.6 binaries (downloaded from artifacts.elastic.co):** Logstash ran a grok pipeline on a 3-line access log (two parsed events with correct integer and float types and the event time taken from the log line, plus the junk line kept and tagged `_grokparsefailure`) and a JSON pipeline on 2 lines; a pipeline with a missing brace is rejected with a line and column. `filebeat test config` reports "Config OK" for a filestream + ndjson + multiline + processors config and a Kubernetes autodiscover config, and rejects a config with two outputs. The module count (55) was counted in the real package; the sizing example (50 GB/day x 1.2 x 2 x 7 days = 840 GB) was computed. **Corrections made while testing:** I first wrote 63 modules from memory, the real package has 55; Logstash needs an absolute path to `-f`.

**Not executed:** no live Elasticsearch or Kibana (a 634 MB download timed out on the first attempt and the sandbox blocks loopback connections), so templates, mappings, ILM, searches, ES|QL and alerts are documented behaviour, labelled as such in each scene. Version facts are from the official Elasticsearch release notes (9.1 to 9.5) and the GitHub releases (latest 9.5.6).

# Istio deep dive: 10 to 28 minutes (9 Nov 2026)

Istio Service Mesh from Scratch grew from 26 to 48 scenes: sidecar vs ambient and how to choose, what an ambient install contains, install options and the commands that changed, enrolling workloads, waypoints, the Gateway/DestinationRule/VirtualService set, canary and header routing with retries and mirroring, what `validate` and `analyze` do and do not catch, Gateway API vs Istio gateways, retries and circuit breaking, the 1.31 traffic additions, a four-resource zero-trust model, JWT claims, rolling out STRICT mTLS, security changes in 1.29 to 1.31, the Telemetry API, golden signals, debugging commands and typical failures, upgrades and version support, and a 1.29 to 1.31 summary. Reference manifests are in `examples/istio/`.

**Checked offline with istioctl 1.31.4 and kubeconform (no cluster):** `istioctl validate` accepts all nine Istio resources and `kubeconform` validates them against the Istio CRD schemas (9 of 9, plus the generated waypoint). `istioctl analyze --use-kube=false -A` is clean on the good set and reports IST0101 and IST0132 on a copy with a missing gateway and subset. `istioctl manifest generate` for the default and ambient profiles, `waypoint generate`, and every flag used in the video were checked against the real binary. **Findings that changed the video:** `istioctl profile` no longer exists in 1.31.4; `precheck` is `istioctl x precheck`; `validate` accepts weights that add up to 90 and `analyze` does not flag the total; `analyze` without `-A` reports no issues on broken files in other namespaces; and an unquoted `request.auth.claims[groups]` broke the YAML. Release facts come from the istio.io announcements for 1.27 to 1.31 and the GitHub releases (latest 1.31.4; 1.32.0-rc.2 is a pre-release).

**Not verified:** no Kubernetes cluster was available (kind and minikube are not installed and Docker has no daemon), so no real traffic, mTLS, canary split, retry, circuit-breaker, tracing or Kiali behaviour was observed. Sample command output in those scenes is representative.

# Jenkins deep dive: 10 to 29 minutes (9 Nov 2026)

Jenkins CI/CD from Scratch grew from 26 to 55 scenes: what happens when a build runs, versions and Java support, a production Jenkinsfile, catching syntax errors, declarative vs scripted, daily steps, parallel stages with fail-fast, `when` conditions, deployments that cannot collide (`lock`, `milestone`, `helm --atomic`), Kubernetes pod agents, agent hygiene, building images without handing over the host, credentials, short-lived access, scan/sign/provenance, webhooks, shared libraries and how to test them, results and artifacts, a full JCasC file, installing with Helm, pinned plugins, a hardening checklist, exposure and fork PRs, backup and upgrades, scaling and metrics, how to choose between Jenkins and alternatives, and a checklist. Reference files are in `examples/jenkins/`.

**Checked locally:** five pipelines (declarative, parallel, Kubernetes agent, shared-library step, scripted) parse with the Groovy 4.0.27 compiler, and a deliberately broken Jenkinsfile is rejected with a line and column. The JCasC file, agent pod spec and Helm values parse as YAML; the pod spec is valid on Kubernetes 1.34 (kubeconform); the Helm values were compared with the real defaults of chart `jenkins/jenkins` 5.11.0 and `helm template` renders a StatefulSet, Services, ConfigMaps, a Secret, a PVC and RBAC. Plugin versions and required core versions were read from the live stable update centre (core 2.580.2). The real 2.580.2 WAR was run: on this Mac's Java 23 it refuses to start, which is shown in the video. The 2.580.2 changelog reports testing on JDK 21 and 25.

**Not verified:** no live Jenkins could run (Java 23 is unsupported, and the sandbox blocks loopback connections). Groovy parsing checks syntax only, so Declarative directives, plugin steps, JCasC loading, webhooks, agents and credentials behaviour are from documentation, not execution.

# Python deep dive: 20 to 40 minutes (9 Nov 2026)

Python Scripting for DevOps grew from 46 to 73 scenes: uv projects, lockfiles and PEP 723 inline dependencies, the 2026 toolchain, f-strings, pattern matching, dataclasses, exception chaining and groups, pathlib and timezone-aware datetimes, safe YAML/JSON/CSV, pydantic validation, regex, safe `subprocess` (with a live injection demo), logging and argparse, threads vs processes vs asyncio, retries, HTTP hygiene, testing AWS code with moto, pagination, cloud client patterns, and a complete project (`examples/python/shopctl`) with Typer, pytest, ruff, mypy and a built wheel.

**Executed locally:** Python 3.14.7, uv 0.11.8, pytest 9.2, ruff 0.17.4, mypy 2.4.1 (strict), Typer 0.28, httpx 0.28, pydantic 2.14, moto 5. `shopctl`: **22 tests pass at 98% coverage**; `ruff check` and `ruff format` clean; `mypy --strict` clean; the wheel builds and the installed command runs (a health check against pypi.org returned 200). About 40 language snippets were run for the exact output shown. **Testing found real issues, all fixed before they went into the video:** S3 bucket names need at least 3 characters; `httpx.MockTransport` responses have no `.elapsed`; ruff flagged B008 and long lines (B008 fixed with `Annotated`, not a `noqa`); mypy needed `types-PyYAML` and `boto3-stubs`. A mutation check (making `prune()` delete the newest archives) fails exactly `test_prune_keeps_newest`.

**Not executed:** real AWS, Azure, Google Cloud, Kubernetes, Docker and SSH calls (no credentials, cluster or daemon); those scenes are labelled representative. The local uv (0.11.8) is older than the latest release (0.13.7), so no scene claims it is current. The CI workflow is representative; its commands were run locally.

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
