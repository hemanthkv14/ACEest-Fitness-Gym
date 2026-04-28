# Kubernetes Deployment Strategies - ACEest Fitness & Gym

This directory contains manifests for **all five** deployment strategies
required by Assignment 2: Rolling Update, Blue-Green, Canary, A/B Testing
and Shadow.

> Replace every occurrence of `DOCKERHUB_USER` with your Docker Hub
> account (e.g. `hemanthkv14`) before applying, **or** run:
>
> ```bash
> find k8s -type f -name '*.yaml' -exec \
>   sed -i 's|DOCKERHUB_USER|hemanthkv14|g' {} +
> ```

## 0. Prerequisites

```bash
minikube start --cpus=4 --memory=4g
minikube addons enable ingress
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/service.yaml
```

Build and push the two image tags used by all strategies:

```bash
docker build -t $DOCKERHUB_USER/aceest-fitness-gym:v1 .
docker tag  $DOCKERHUB_USER/aceest-fitness-gym:v1 \
            $DOCKERHUB_USER/aceest-fitness-gym:v2
docker push $DOCKERHUB_USER/aceest-fitness-gym:v1
docker push $DOCKERHUB_USER/aceest-fitness-gym:v2
```

---

## 1. Rolling Update (default)

```bash
kubectl apply -f k8s/rolling-update/deployment.yaml
# Promote v2:
kubectl -n aceest set image deployment/aceest-rolling \
    aceest=$DOCKERHUB_USER/aceest-fitness-gym:v2
kubectl -n aceest rollout status deployment/aceest-rolling
# Rollback:
kubectl -n aceest rollout undo deployment/aceest-rolling
```

## 2. Blue-Green

```bash
kubectl apply -f k8s/blue-green/
# Cut live traffic from blue -> green (zero-downtime switch):
kubectl -n aceest patch svc aceest-svc \
  -p '{"spec":{"selector":{"app":"aceest-fitness-gym","version":"green"}}}'
# Rollback (instant):
kubectl -n aceest patch svc aceest-svc \
  -p '{"spec":{"selector":{"app":"aceest-fitness-gym","version":"blue"}}}'
```

## 3. Canary (replica-weighted)

```bash
kubectl apply -f k8s/canary/
# Start: 9 stable + 1 canary  -> ~10% traffic on v2.
# Gradually promote:
kubectl -n aceest scale deployment/aceest-canary --replicas=3   # ~25%
kubectl -n aceest scale deployment/aceest-stable --replicas=7
# Full promotion or rollback = scale the losing side to 0.
```

## 4. A/B Testing (header-routed)

```bash
kubectl apply -f k8s/ab-testing/
echo "$(minikube ip) aceest.local" | sudo tee -a /etc/hosts
# Default audience hits variant A:
curl http://aceest.local/health
# Opt-in testers hit variant B:
curl -H "X-Experiment: variant-b" http://aceest.local/health
```

## 5. Shadow (traffic mirroring via Istio)

```bash
istioctl install --set profile=demo -y
kubectl label namespace aceest istio-injection=enabled --overwrite
kubectl apply -f k8s/shadow/shadow.yaml
# Clients only see responses from aceest-primary-svc;
# aceest-shadow-svc receives a mirrored copy of every request.
```

---

## Rollback cheat-sheet

| Strategy       | Rollback command                                                     |
| -------------- | -------------------------------------------------------------------- |
| Rolling Update | `kubectl -n aceest rollout undo deployment/aceest-rolling`           |
| Blue-Green     | Patch `aceest-svc` selector back to `version: blue`                  |
| Canary         | `kubectl -n aceest scale deployment/aceest-canary --replicas=0`      |
| A/B Testing    | `kubectl -n aceest delete ingress aceest-ab-experiment`              |
| Shadow         | `kubectl -n aceest delete virtualservice aceest-shadow-vs`           |
