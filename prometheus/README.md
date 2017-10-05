# installation
From: https://github.com/coreos/prometheus-operator

rbac:
```
kubectl create -f rbac.yml
```

prometheus:
```
kubectl create -f prometheus.yml
kubectl create -f prometheus-resource.yml
```

Kubernetes monitoring:
```
kubectl create -f kubernetes-monitoring.yml
```

Example app:
```
kubectl create -f example-application.yml
```
