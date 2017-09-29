# Spinnaker build
* Make changes to spinnaker.yml
* helm install --name demo -f spinnaker.yml stable/spinnaker

# Git and docker
* Setup git repository on github or bitbucket
* Setup docker hub account
* Link docker hub account with github or bitbucket
* Create new automated build

# Spinnaker configuration
* Create new application
* Create new loadbalancer
* Create new server group
* Create new pipeline

# Persistence
* Currently minio (an S3 compatible storage system) is providing persistence for Spinnaker
  * If you are on AWS, you might rather want to use S3 itself, but that doesn't seem to be possible yet with this chart
