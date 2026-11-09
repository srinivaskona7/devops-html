# Istio manifests from the Istio video

Checked offline with `istioctl` 1.31.4 and `kubeconform`; **not applied to a cluster** (none was available).

```bash
istioctl validate -f traffic.yaml            # schema + semantic check: "is valid"
kubeconform -strict -ignore-missing-schemas \
  -schema-location default \
  -schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json' \
  traffic.yaml security.yaml telemetry.yaml waypoint.yaml     # 10 resources valid
istioctl analyze --use-kube=false -A traffic.yaml security.yaml telemetry.yaml
```

Limits worth knowing: `validate` accepts a VirtualService whose weights add up to 90, and `analyze` does not flag the total;
always run `analyze` with `-A`, otherwise it only checks the `default` namespace.
