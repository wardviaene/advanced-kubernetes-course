# install kubefed

## Linux
curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/kubernetes-client-linux-amd64.tar.gz
tar -xzvf kubernetes-client-linux-amd64.tar.gz

## OS X
curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/kubernetes-client-darwin-amd64.tar.gz
tar -xzvf kubernetes-client-darwin-amd64.tar.gz

## Windows
curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/kubernetes-client-windows-amd64.tar.gz
tar -xzvf kubernetes-client-windows-amd64.tar.gz

# setup the clusters

Replace newtech.academy with your domain

```
kops create cluster --name=kubernetes.newtech.academy --state=s3://kops-state-b429b --zones=eu-west-1a --node-count=2 --node-size=t2.small --master-size=t2.small --dns-zone=kubernetes.newtech.academy
kops create cluster --name=kubernetes-2.newtech.academy --state=s3://kops-state-b429b --zones=eu-west-1b --node-count=2 --node-size=t2.small --master-size=t2.small --dns-zone=kubernetes-2.newtech.academy
kops update cluster kubernetes.newtech.academy --state=s3://kops-state-b429b --yes
kops update cluster kubernetes-2.newtech.academy --state=s3://kops-state-b429b --yes
```

# initialize federation
kubefed init federated --host-cluster-context=kubernetes.newtech.academy --dns-provider="aws-route53" --dns-zone-name="federated.newtech.academy."

# join a cluster
kubectl config set-context federated # important, if you don't switch, the next command might fail with an API not found error
kubefed join kubernetes-2 --host-cluster-context=kubernetes.newtech.academy --cluster-context=kubernetes-2.newtech.academy
kubefed join kubernetes-1 --host-cluster-context=kubernetes.newtech.academy --cluster-context=kubernetes.newtech.academy
kubectl create namespace default --context=federated

