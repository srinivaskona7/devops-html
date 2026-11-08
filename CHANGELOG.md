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
