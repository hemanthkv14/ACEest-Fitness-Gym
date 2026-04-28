# ACEest Fitness & Gym - DevOps Assignment 2 Report

**Student repository:** `hemanthkv14/ACEest-Fitness-Gym`
**Application:** Flask + SQLite gym management system
**Pipeline deliverables:** Jenkins + GitHub Actions, SonarQube, Docker Hub,
Kubernetes with five progressive deployment strategies.

---

## 1. CI/CD Architecture Overview

```
 Developer  ──git push──▶  GitHub (main / feature/*)
                                   │
           ┌───────────────────────┼───────────────────────┐
           ▼                       ▼                       ▼
   GitHub Actions           Jenkins (pollSCM 2m)    SonarQube Server
 (build-and-lint → test →  (Checkout → Lint → Test   (quality gate,
  sonar → docker push)      + cov → Sonar → Build    coverage + xunit)
                            → Smoke → Push Hub →
                            Deploy k8s → Rollback
                            on failure)
                                   │
                                   ▼
                         Docker Hub registry
                         hemanthkv14/aceest-fitness-gym
                         tags: :latest :vN :sha-XXXX
                                   │
                                   ▼
                         Minikube / Kubernetes cluster
                         namespace: aceest
                         ├── Rolling Update  (aceest-rolling)
                         ├── Blue-Green      (aceest-blue / -green)
                         ├── Canary          (aceest-stable / -canary)
                         ├── A/B Testing     (NGINX Ingress header route)
                         └── Shadow          (Istio VirtualService mirror)
```

### Component responsibilities

| Layer           | Tool                     | Responsibility                                       |
| --------------- | ------------------------ | ---------------------------------------------------- |
| Version Control | Git + GitHub             | Branching (`main`, `feature/*`), tags (`vN`)         |
| CI (cloud)      | GitHub Actions           | Lint, unit tests, coverage, Docker build/push        |
| CI (on-prem)    | Jenkins (`Jenkinsfile`)  | Full pipeline including k8s deploy + rollback        |
| Testing         | Pytest + pytest-cov      | 37 test cases, JUnit XML + Cobertura coverage        |
| Code Quality    | SonarQube                | Static analysis, quality gate, coverage import       |
| Containers      | Docker                   | Non-root `python:3.12-slim` image, healthcheck       |
| Registry        | Docker Hub               | Tagged per build (`:BUILD_NUMBER`, `:v1`, `:latest`) |
| Orchestration   | Kubernetes (Minikube)    | 5 deployment strategies under namespace `aceest`     |
| Traffic mgmt    | NGINX Ingress / Istio    | A/B header routing, shadow mirroring                 |

### Pipeline stages (Jenkinsfile)

1. **Checkout** – SCM polling every 2 minutes.
2. **Lint** – `flake8` critical rules (fail) + style (exit-zero).
3. **Test + Coverage** – `pytest --cov=app --cov-report=xml`.
4. **SonarQube Analysis** – publishes `coverage.xml` + `test-results.xml`.
5. **Quality Gate** – `waitForQualityGate` with 5-minute timeout.
6. **Docker Build** – three tags: `:BUILD_NUMBER`, `:vN`, `:latest`.
7. **Container Smoke Test** – runs pytest inside the freshly built image.
8. **Push to Docker Hub** – credentials via `dockerhub-creds`.
9. **Deploy to Kubernetes** – `kubectl set image` rolling update + wait for
   `rollout status`. On failure, `post { failure }` automatically executes
   `kubectl rollout undo` – satisfying the mandatory rollback requirement.
10. **Export Artifact** – `docker save` tarball archived in Jenkins.

---

## 2. Deployment Strategies (Task 6)

All five strategies live under `k8s/` with dedicated sub-folders. Each one
is independently deployable and documented in `k8s/README.md`.

| # | Strategy       | Implementation mechanism                                      | Rollback                           |
|---|----------------|---------------------------------------------------------------|------------------------------------|
| 1 | Rolling Update | Native `Deployment.strategy.RollingUpdate` (surge 1, unavail 0) | `kubectl rollout undo`            |
| 2 | Blue-Green     | Two Deployments, Service selector flip (`version: blue↔green`) | Re-patch selector to `blue`       |
| 3 | Canary         | Replica-weighted (9 stable + 1 canary → 10% traffic)           | Scale canary replicas to `0`      |
| 4 | A/B Testing    | NGINX Ingress `canary-by-header: X-Experiment=variant-b`       | Delete experiment ingress         |
| 5 | Shadow         | Istio `VirtualService` with `mirror` + `mirrorPercentage:100`  | Delete the VirtualService         |

Readiness and liveness probes hit `/health` (provided by `app.py`), enabling
the Kubernetes scheduler to gate every rollout on actual application health.

---

## 3. Challenges Faced & Mitigation Strategies

| Challenge                                                      | Mitigation                                                                                      |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| **Tests importing `app.py` triggered `init_db()` on real DB.** | Fixture in `tests/test_app.py` swaps `app_module.DB_NAME` to a `tempfile.mkstemp` DB per test. |
| **SonarQube coverage was empty.**                              | Added `pytest-cov` invocation (`--cov=app --cov-report=xml`) in both Jenkinsfile and GH Actions. |
| **Docker Hub secrets accidentally logged.**                    | Switched to `withCredentials` + `--password-stdin`; GH Actions uses encrypted `secrets.*`.      |
| **Blue-Green traffic cutover caused brief 502s.**              | Added readiness probes on the green Deployment so the Service selector patch only routes to healthy pods. |
| **Shadow traffic mirroring unsupported by vanilla NGINX.**     | Adopted Istio `VirtualService` with `mirror` + `mirrorPercentage` for true shadow traffic.      |
| **Jenkins agent did not have `kubectl`.**                      | Mounted a `kubeconfig` credential file; `kubectl` installed as agent prerequisite.             |
| **Image name placeholder in manifests.**                       | Pipeline runs a `sed` substitution (`DOCKERHUB_USER → ${DOCKERHUB_USER}`) before `kubectl apply`. |

---

## 4. Key Automation Outcomes

- **End-to-end automation** from `git push` to a rolled-out pod in Kubernetes
  with zero manual steps.
- **Two independent CI surfaces** (GitHub Actions for cloud, Jenkins for
  on-prem) with identical test + coverage contracts, reducing lock-in risk.
- **37 automated tests** (unit + integration + API) executed twice: on the
  runner host *and* inside the built container image before publishing.
- **Quality gate-enforced releases**: a failing SonarQube gate or pytest run
  blocks both image push and Kubernetes deploy.
- **Five production-grade deployment patterns** co-exist in one cluster,
  letting the team pick the right risk profile per release.
- **Deterministic rollback** on every strategy – documented and verified in
  `k8s/README.md` and wired into the Jenkins `post { failure }` block.
- **Image provenance**: every build publishes three immutable tags
  (`:BUILD_NUMBER`, `:vN`, `:latest`) to Docker Hub, enabling exact
  reproduction of any historical deployment.

---

## 5. Repository Layout

```
ACEest-Fitness-Gym/
├── app.py                    # Flask application (466 lines, 17 routes)
├── tests/test_app.py         # 37 Pytest cases (unit + integration + API)
├── requirements.txt          # Flask 3.1, pytest 8.3, pytest-cov 6, gunicorn
├── Dockerfile                # python:3.12-slim, non-root, gunicorn, HEALTHCHECK
├── Jenkinsfile               # 10-stage pipeline (build → deploy → rollback)
├── sonar-project.properties  # Sonar project key, coverage + xunit wiring
├── .github/workflows/main.yml# GH Actions: build → test → sonar → docker
├── k8s/
│   ├── base/                 # Namespace + ClusterIP & NodePort Services
│   ├── rolling-update/       # Strategy 1
│   ├── blue-green/           # Strategy 2
│   ├── canary/               # Strategy 3
│   ├── ab-testing/           # Strategy 4 (NGINX Ingress header routing)
│   ├── shadow/               # Strategy 5 (Istio VirtualService mirror)
│   └── README.md             # Deploy + rollback cheat-sheet
└── REPORT.md                 # This report
```
