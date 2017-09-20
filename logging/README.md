# Advanced Kubernetes course
## logging
* These files are modified from https://github.com/kubernetes/kubernetes/blob/master/cluster/addons/fluentd-elasticsearch to add persistent storage and kibana plugins

## Steps
* kubectl create -f logging/
* Run a cluster with sufficient resources (3x t2.medium at least on AWS)
* Make sure to label nodes with beta.kubernetes.io/fluentd-ds-ready=true
