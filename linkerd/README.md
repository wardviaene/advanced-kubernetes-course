# install linkerd
helm install --name demo -f linkerd.yml stable/linkerd
export LINKERDLB=$(kubectl get svc --namespace default demo-linkerd -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo http://$LINKERDLB:9990


# examples
Examples are from https://github.com/linkerd/linkerd-examples/tree/master/k8s-daemonset/k8s/


