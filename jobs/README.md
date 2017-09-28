# Runtime config

To run batch/v2alpha1 API resources you need to specify --runtime-config=batch/v2alpha1 when starting the API Server

For kops, add this spec when executing kops edit:
```
spec:
  kubeAPIServer:
    runtimeConfig:
      batch/v2alpha1: "true"
```
