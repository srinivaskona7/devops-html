package k8srequiredlabels

violation contains {"msg": msg} if {
	provided := {l | input.review.object.metadata.labels[l]}
	missing := {l | some l in input.parameters.labels} - provided
	count(missing) > 0
	msg := sprintf("missing labels: %v", [missing])
}
