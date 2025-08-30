---
runme:
  version: v3
---

# Démo - Gestion des Secrets dans Kubernetes avec ESO

```bash
kind create cluster
```

## Application Python de démo avec AWS Secret Manager

L'application Python lit 3 secrets depuis `/secrets` :

- DB URL
- DB username
- DB password

## Pré-requis

> Alternatives self-hosted : Vault, Openbao (fork de Vault)

### 1. Créer le secret dans AWS Secret Manager

```bash
aws secretsmanager create-secret \
    --name "mysql-credentials" \
    --description "Credentials pour la base de données MySQL" \
    --secret-string '{
        "url": "mysql.prod.example.com:3306",
        "username": "prod_user",
        "password": "super_secure_password"
    }'
```

### 2. Créer le secret pour donner les droits nécessaires à ESO

```bash
source .env
k create ns demo
kn demo
k create secret generic aws-creds \
  --from-literal=access-key-id=$ACCESS_KEY_ID \
  --from-literal=secret-access-key=$SECRET_ACCESS_KEY
```

> Sur un cluster cloud managé : Il faut gérer les permissions (AWS : IRSA ou EKS Pod Identity)

## Déploiement

1. Chart Helm Reloader

```bash {"terminalRows":"29"}
helm repo add stakater https://stakater.github.io/stakater-charts
helm repo update
helm install reloader stakater/reloader -n reloader --create-namespace --values ./app-example/manifests/reloader/values.yaml
```

> Permet la recharge automatique lorqu'on modifie un secret. (fonctionne aussi pour les configmaps)

2. Chart Helm ESO

```bash {"terminalRows":"29"}
helm repo add external-secrets https://charts.external-secrets.io
helm repo update
helm install external-secrets external-secrets/external-secrets -n external-secrets --create-namespace
```

3. Créations des CRDs

- ClusterSecretStore = Donne les accès + indication où sont les secrets

```bash {"terminalRows":"20"}
cat app-example/manifests/eso/secretstore.yml
k apply -f app-example/manifests/eso/secretstore.yml
```

- ExternalSecret = Comment on accède à un secret spécifique

```bash {"terminalRows":"35"}
cat app-example/manifests/eso/external-secret-db.yml
k apply -f app-example/manifests/eso/external-secret-db.yml
```

Vérification des secrets

```bash
k get externalsecret my-db-credentials
k view-secret mysql-credentials
```

4. Déploiement de l'application

```bash {"terminalRows":"49"}
cat app-example/manifests/app/deployment.yml
k apply -f app-example/manifests/app/
```

```bash
kubectl port-forward svc/demo 5000:5000 # http://localhost:5000
```

> Si on modifie un secret dans le store, un rollout est déclenché grâce à Reloader.

Delete Secret

```bash
aws secretsmanager delete-secret --secret-id mysql-credentials --force-delete-without-recovery --region eu-west-3
```
