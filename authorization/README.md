# kube authorization with auth0

Add oidc setup to kops cluster:

```
spec:
  kubeAPIServer:
    oidcIssuerURL: https://account.eu.auth0.com/
    oidcClientID: clientid
    oidcUsernameClaim: name
    oidcGroupsClaim: http://authserver.kubernetes.newtech.academy/claims/groups
  authorization:
    rbac: {}

```

Auth0 rule for groups

```
function (user, context, callback) {
  var namespace = 'http://authserver.kubernetes.newtech.academy/claims/'; // You can set your own namespace, but do not use an Auth0 domain

  // Add the namespaced tokens. Remove any which is not necessary for your scenario
  context.idToken[namespace + "permissions"] = user.permissions;
  context.idToken[namespace + "groups"] = user.groups;
  context.idToken[namespace + "roles"] = user.roles;
  
  callback(null, user, context);
}
```
