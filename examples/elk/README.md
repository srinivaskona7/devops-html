# ELK examples from the ELK video

**Executed with the official 9.5.6 binaries:**
- `logstash-grok.conf` and `logstash-json.conf` ran against `sample-access.log` and `sample-app.json`; the real output is in the `*.output.jsonl` files.
  Logstash needs absolute paths: edit `/path/to/examples/elk/` in the two `.conf` files first, then
  `logstash -f /abs/path/logstash-grok.conf` (add `--config.test_and_exit` to only validate).
- `filebeat.yml` and `filebeat-k8s.yml` pass `filebeat test config -c <file> -e` ("Config OK") with `ES_API_KEY` and `NODE_NAME` set.

**Not executed:** anything that needs a live Elasticsearch or Kibana (templates, ILM, searches, ES|QL, alerts). Those scenes show documented behaviour.
