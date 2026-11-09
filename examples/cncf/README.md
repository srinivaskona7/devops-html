# CNCF examples from the CNCF video

Run locally (no cluster):
```bash
kyverno apply kyverno-require-limits.yaml --resource kyverno-test-pods.yaml     # Kyverno CLI 1.13.4: pass 1, fail 2
opa check --strict rego/required_labels.rego && opa test rego -v                # OPA 1.22.2: PASS 3/3
kubeconform -strict -ignore-missing-schemas -kubernetes-version 1.34.0 \
  -schema-location default \
  -schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json' \
  manifests.yaml                                                                # 12 valid, 1 skipped (Gatekeeper constraint: no schema until its template is applied)
```
`manifests.yaml` contains 13 resources (Kyverno, Argo CD, Flux x2, KEDA, cert-manager x2, Gateway API x2, Cilium, Gatekeeper x2, Crossplane).
**Not applied to a cluster** (none was available). Rego uses OPA v1 syntax (`if`, `contains`); the Gatekeeper `ConstraintTemplate`
inside `manifests.yaml` keeps the older Rego syntax Gatekeeper templates commonly use, which needs `--v0-compatible` in OPA 1.x.
