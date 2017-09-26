# kube authentication resources

Add oidc setup to kops cluster:

```
spec:
  kubeAPIServer:
    oidcIssuerURL: https://account.eu.auth0.com/
    oidcClientID: clientid
    oidcUsernameClaim: sub
```

Create UI:

```
kubectl create -f https://raw.githubusercontent.com/kubernetes/kops/master/addons/kubernetes-dashboard/v1.6.3.yaml
```

