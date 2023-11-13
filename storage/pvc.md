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

~~~bash
kubectl exec -it model-store-pod -n kubeflow-user-example-com -- bash
~~~

### Test the inference outside the k8s Cluster

~~~bash
export MODEL_NAME=sklearn-pvc
export SERVICE_HOSTNAME=sklearn-pvc.kubeflow-user-example-com.example.com
~~~
Obtain the kubeflow auth session from the browser. 
~~~bash
export SESSION=MTY5OTkyOTQzM3xOd3dBTkVOTFRqSXlXazgyTXpSV1NVazFTREpTVmpOUk5rVk5Ra3hVVUZKVFRFazBXVFJNU1ZOWlJVdFNWVlZQVWxwU1NGZFZSMUU9fJAKn3yn3PDcOZrEcRpNlIMZhFNpB2pjt2NACg0Qt_uL
~~~
List the model supported
~~~bash
curl -v -H "Content-Type: application/json" -H "Cookie: authservice_session=${SESSION}" -H "Host: ${SERVICE_HOSTNAME}" http://10.149.8.3:8008/v1/models
~~~
you should observe this:    
~~~bash
*   Trying 10.149.8.3:8008...
* Connected to 10.149.8.3 (10.149.8.3) port 8008 (#0)
> GET /v1/models HTTP/1.1
> Host: sklearn-pvc.kubeflow-user-example-com.example.com
> User-Agent: curl/7.81.0
> Accept: */*
> Content-Type: application/json
> Cookie: authservice_session=MTY5OTkyOTQzM3xOd3dBTkVOTFRqSXlXazgyTXpSV1NVazFTREpTVmpOUk5rVk5Ra3hVVUZKVFRFazBXVFJNU1ZOWlJVdFNWVlZQVWxwU1NGZFZSMUU9fJAKn3yn3PDcOZrEcRpNlIMZhFNpB2pjt2NACg0Qt_uL
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< content-length: 26
< content-type: application/json
< date: Tue, 14 Nov 2023 20:10:16 GMT
< server: istio-envoy
< x-envoy-upstream-service-time: 45
< 
* Connection #0 to host 10.149.8.3 left intact
{"models":["sklearn-pvc"]}
~~~

Start the prediction with the following:
~~~bash
curl -v -H "Content-Type: application/json" -H "Cookie: authservice_session=${SESSION}" -H "Host: ${SERVICE_HOSTNAME}" -H "Content-Type: application/json" -d @./iris-input.json  http://10.149.8.3:8008/v1/models/sklearn-pvc:predict
~~~
and you should get the following response:
~~~bash
*   Trying 10.149.8.3:8008...
* Connected to 10.149.8.3 (10.149.8.3) port 8008 (#0)
> POST /v1/models/sklearn-pvc:predict HTTP/1.1
> Host: sklearn-pvc.kubeflow-user-example-com.example.com
> User-Agent: curl/7.81.0
> Accept: */*
> Content-Type: application/json
> Cookie: authservice_session=MTY5OTkyOTQzM3xOd3dBTkVOTFRqSXlXazgyTXpSV1NVazFTREpTVmpOUk5rVk5Ra3hVVUZKVFRFazBXVFJNU1ZOWlJVdFNWVlZQVWxwU1NGZFZSMUU9fJAKn3yn3PDcOZrEcRpNlIMZhFNpB2pjt2NACg0Qt_uL
> Content-Type: application/json
> Content-Length: 76
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< content-length: 21
< content-type: application/json
< date: Tue, 14 Nov 2023 20:13:08 GMT
< server: istio-envoy
< x-envoy-upstream-service-time: 19
< 
* Connection #0 to host 10.149.8.3 left intact
{"predictions":[1,1]}
~~~