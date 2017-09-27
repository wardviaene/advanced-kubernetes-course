# helm mysql package

Download helm first from https://github.com/kubernetes/helm

Initialize helm:

helm init

To install mysql, enter:

helm install --name my-mysql --set mysqlRootPassword=secretpassword,mysqlUser=my-user,mysqlPassword=my-password,mysqlDatabase=my-database stable/mysql

