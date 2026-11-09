# Jenkins examples from the Jenkins video

Checked locally (not run on a live Jenkins):
- Jenkinsfiles and the shared-library step parse with the Groovy 4.0.27 compiler (syntax only; Declarative directives and plugin
  steps are validated only by a running controller, e.g. via `pipeline-model-converter/validate`).
- `jenkins.casc.yaml` and `helm-values.yaml` parse as YAML. The Helm values were compared with the defaults of chart
  `jenkins/jenkins` 5.11.0 (Jenkins 2.580.2) and render with `helm template`.
- The pod spec inside `Jenkinsfile.k8s` is valid on Kubernetes 1.34 (kubeconform).

Jenkins 2.580.2 LTS needs Java 21 or 25 (it refuses to start on Java 23).
