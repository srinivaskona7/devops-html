// vars/deployService.groovy in a shared library
def call(Map cfg = [:]) {
  def env = cfg.env ?: 'staging'
  pipeline {
    agent any
    stages {
      stage("Deploy ${cfg.name} to ${env}") {
        steps { sh "helm upgrade --install ${cfg.name} ./chart --namespace ${env} --atomic --timeout 5m" }
      }
    }
  }
}
