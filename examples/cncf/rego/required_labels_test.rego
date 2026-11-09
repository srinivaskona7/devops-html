package k8srequiredlabels

test_allows_when_label_present if {
	count(violation) == 0 with input as {"review": {"object": {"metadata": {"labels": {"owner": "a"}}}}, "parameters": {"labels": ["owner"]}}
}

test_denies_when_label_missing if {
	count(violation) == 1 with input as {"review": {"object": {"metadata": {"labels": {}}}}, "parameters": {"labels": ["owner"]}}
}

test_reports_all_missing if {
	v := violation with input as {"review": {"object": {"metadata": {"labels": {}}}}, "parameters": {"labels": ["owner", "team"]}}
	some m in v
	contains(m.msg, "owner")
	contains(m.msg, "team")
}
