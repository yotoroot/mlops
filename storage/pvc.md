---
layout: default
title: PVC and PV setup for Kubeflow
parent: Storage
nav_order: 1
---

# PVC Setup
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Persistent volume (PV) & Persistent volume claim (PVC)

### Crete PV and PVC in the kubeflow

Please refer to [Kserve's link] https://kserve.github.io/website/0.11/modelserving/storage/pvc/pvc/ 
Modification has been made to the environment setup different.
- use kubeflow-user-example-com as namespace, so that volume and model can be seen in the kubeflow's dashboard. 


```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: task-pv-volume
  labels:
    type: local
spec:
  storageClassName: longhorn
  capacity:
    storage: 64Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/home/ubuntu/mnt/data"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: task-pv-claim
spec:
  storageClassName: longhorn
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 60Gi
```

```bash
kubectl apply -f pv-and-pvc.yaml -n kubeflow-user-example-com
```

```yaml

```