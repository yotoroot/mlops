---
layout: default
title: LLAMA
parent: Torchserve
nav_order: 1
---

# Llama 7B Chat HuggingFace Setup
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---
### Configuration

pytorch predictor inference service 
~~~yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: "llama7b"
  annotations:
    serving.kserve.io/enable-prometheus-scraping: "true"
    serving.kserve.io/enable-metric-aggregation: "true"
    prometheus.kserve.io/port: '8082'
    prometheus.kserve.io/path: "/metrics"
spec:
  predictor:
    pytorch:
      runtimeVersion: 0.8.0-gpu
      protocolVersion: v1
      storageUri: pvc://pv-claim
      resources:
        limits:
          memory: 32Gi
          cpu: 12
          nvidia.com/gpu: "1"
~~~
in the pvc config, pv/config/config.properties

~~~yaml
inference_address=http://0.0.0.0:8085
management_address=http://0.0.0.0:8085
metrics_address=http://0.0.0.0:8082
grpc_inference_port=7070
grpc_management_port=7071
enable_metrics_api=true
metrics_format=prometheus
number_of_netty_threads=4
job_queue_size=10
enable_envvars_config=true
install_py_dep_per_model=true
model_store=/mnt/models/model-store
model_snapshot={"name":"startup.cfg","modelCount":1,"models":{"llama7b":{"1.0":{"defaultVersion":true,"marName":"llama7b.mar","minWorkers":1,"maxWorkers":5,"batchSize":1,"maxBatchDelay":50,"responseTimeout":600}}}}
~~~


### Model Preparation

~~~bash
git clone https://github.com/pytorch/serve.git
cd serve/examples/large_models/Huggingface_accelerate
~~~

download llama7b model from Huggingface
~~~bash

~~~



~~~bash
torch-model-archiver --model-name ../llama7b --version 1.0  --handler custom_handler.py -r requirements.txt --extra-files "model-config.yaml"
~~~

~~~bash
kubectl cp config.properties model-store-pod:/pv/config/config.properties -c model-store -n kubeflow-user-example-com
kubectl cp llama7b.mar model-store-pod:/pv/llama7b.mar -c model-store -n kubeflow-user-example-com
~~~

### Query the service Host
Use hey to send multiple request to the model server
~~~bash
export MODEL_NAME=llama7b
export INPUT_PATH=input.json
export SERVICE_HOSTNAME=llama7b.kubeflow-user-example-com.example.com
export SESSION=MTcwMjA1NTU5OHxOd3dBTkRKWFNFSlBNbFJRVTA1WFJWQTFVRWhPV2tveVNsVkxWRWRGTWtwWk5GWXpUalJPU2s5WldWTlNSRWRHVmtOWVNVZEVXVkU9fKxaPDEDprEXnWA1eNKMa7sLXD7HPBMaEhO_shXV2Ajo
~~~

make sure single cURL command is working.
~~~bash
curl -v   -H "Host: ${SERVICE_HOSTNAME}"  -H "Content-Type: application/json" -H "Cookie: authservice_session=${SESSION}"   -d @./input.json   http://10.149.8.3:8008/v1/models/llama7b:predict
~~~

Multiple request using hey
~~~bash
hey -z 60s -c 5 -m POST -host ${SERVICE_HOSTNAME} -H "Content-Type: application/json" -H "Cookie: authservice_session=${SESSION}" -D $INPUT_PATH http://10.149.8.3:8008/v1/models/$MODEL_NAME:predict
~~~

### Performance
#### 1 QPS, BatchSize = 1, GPU=1
~~~bash
hey -z 60s -c 1 -m POST -host ${SERVICE_HOSTNAME} -H "Content-Type: application/json" -H "Cookie: authservice_session=${SESSION}" -D $INPUT_PATH http://10.149.8.3:8008/v1/models/$MODEL_NAME:predict
~~~

~~~bash
Summary:
  Total:        60.3194 secs
  Slowest:      2.2597 secs
  Fastest:      2.0957 secs
  Average:      2.1542 secs
  Requests/sec: 0.4642
  
  Total data:   2548 bytes
  Size/request: 91 bytes

Response time histogram:
  2.096 [1]     |■■■■■■■
  2.112 [1]     |■■■■■■■
  2.128 [5]     |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  2.145 [6]     |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  2.161 [5]     |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  2.178 [6]     |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  2.194 [0]     |
  2.210 [1]     |■■■■■■■
  2.227 [1]     |■■■■■■■
  2.243 [1]     |■■■■■■■
  2.260 [1]     |■■■■■■■


Latency distribution:
  10% in 2.1140 secs
  25% in 2.1298 secs
  50% in 2.1480 secs
  75% in 2.1714 secs
  90% in 2.2374 secs
  95% in 2.2597 secs
  0% in 0.0000 secs

Details (average, fastest, slowest):
  DNS+dialup:   0.0000 secs, 2.0957 secs, 2.2597 secs
  DNS-lookup:   0.0000 secs, 0.0000 secs, 0.0000 secs
  req write:    0.0000 secs, 0.0000 secs, 0.0001 secs
  resp wait:    2.1541 secs, 2.0955 secs, 2.2595 secs
  resp read:    0.0001 secs, 0.0000 secs, 0.0001 secs

Status code distribution:
  [200] 28 responses
~~~
nvtop result
~~~bash
Device 0 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  77 / 400 W
 GPU[                               0%] MEM[||||                  11.3G/85.9G]
 Device 1 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  74 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 2 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  37°C FAN N/A% POW  75 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 3 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  40°C FAN N/A% POW  75 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 4 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 2.000 MB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  42°C FAN N/A% POW  77 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 5 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  75 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 6 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  38°C FAN N/A% POW  76 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 7 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  72 / 400 W
 GPU[                               0%] MEM[|                      3.0G/85.9G]
   ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
100│                                                                                             MAX GPU│
   │                                                                                             MAX MEM│
75%│                                                                                                    │
   │                                                                                                    │
50%│                                                                                                    │
   │                      ┌───────────────────────────────────────────────┐                             │
25%│──────────────────────┼───────────────────────────────────────────────┼──────┐                      │
 0%│──────────────────────┘                                               └──────┴──────────────────────│
   └────────────────────────────────────────────────────────────────────────────────────────────────────┘
~~~

~~~bash
user8@bcm10-headnode:~/kfp/llama$ hey -z 60s -c 4 -m POST -host ${SERVICE_HOSTNAME} -H "Content-Type: applic
ation/json"   -H "Cookie: authservice_session=${SESSION}" -D $INPUT_PATH http://10.149.8.3:8008/v1/models/$M
ODEL_NAME:predict

Summary:
  Total:        67.1914 secs
  Slowest:      8.7074 secs
  Fastest:      2.1991 secs
  Average:      6.3210 secs
  Requests/sec: 0.5060
  
  Total data:   2821 bytes
  Size/request: 91 bytes

Response time histogram:
  2.199 [1]     |■■■■
  2.850 [0]     |
  3.501 [0]     |
  4.152 [0]     |
  4.802 [10]    |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  5.453 [0]     |
  6.104 [1]     |■■■■
  6.755 [6]     |■■■■■■■■■■■■■■■■■■■■■■■■
  7.406 [3]     |■■■■■■■■■■■■
  8.057 [1]     |■■■■
  8.707 [9]     |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


Latency distribution:
  10% in 4.2319 secs
  25% in 4.3148 secs
  50% in 6.6436 secs
  75% in 8.5374 secs
  90% in 8.6517 secs
  95% in 8.7074 secs
  0% in 0.0000 secs

Details (average, fastest, slowest):
  DNS+dialup:   0.0000 secs, 2.1991 secs, 8.7074 secs
  DNS-lookup:   0.0000 secs, 0.0000 secs, 0.0000 secs
  req write:    0.0000 secs, 0.0000 secs, 0.0002 secs
  resp wait:    6.3208 secs, 2.1982 secs, 8.7073 secs
  resp read:    0.0001 secs, 0.0000 secs, 0.0001 secs

Status code distribution:
  [200] 31 responses

Error distribution:
  [3]   Post http://10.149.8.3:8008/v1/models/llama7b:predict: net/http: request canceled (Client.Timeout exceeded while awaiting headers)
~~~

~~~bash
Device 0 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  77 / 400 W
 GPU[                               0%] MEM[||||                  11.3G/85.9G]
 Device 1 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  74 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 2 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  37°C FAN N/A% POW  74 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 3 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  40°C FAN N/A% POW  75 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 4 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  41°C FAN N/A% POW  77 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 5 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  75 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 6 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  38°C FAN N/A% POW  76 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 7 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  72 / 400 W
 GPU[                               0%] MEM[|                      3.0G/85.9G]
   ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
100│                                                                                             MAX GPU│
   │                                                                                             MAX MEM│
75%│                                                                                                    │
   │                                                                                                    │
50%│                                                                                                    │
   │    ┌─────────────────────────────────────────────────────┐                                         │
25%│────┼─────────────────────────────────────────────────────┼─────────────────────────────────────────│
 0%│────┘                                                     └─────────────────────────────────────────│
   └────────────────────────────────────────────────────────────────────────────────────────────────────┘
~~~

### Turn on Batch Inference
since the latency is ~2.0+sec. maxLatency set to 5000ms
maxBatchSize:64

~~~yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: "llama7b"
  annotations:
    serving.kserve.io/enable-prometheus-scraping: "true"
    serving.kserve.io/enable-metric-aggregation: "true"
    prometheus.kserve.io/port: '8082'
    prometheus.kserve.io/path: "/metrics"
spec:
  predictor:
    minReplicas: 1
    timeout: 60
    batcher:
      maxBatchSize: 64
      maxLatency: 5000
    pytorch:
      runtimeVersion: 0.8.0-gpu
      protocolVersion: v1
      storageUri: pvc://pv-claim
      resources:
        limits:
          memory: 32Gi
          cpu: 12
          nvidia.com/gpu: "1"
~~~

~~~bash
user8@bcm10-headnode:~/kfp/llama$ hey -z 60s -c 64 -m POST -host ${SERVICE_HOSTNAME} -H "Content-Type: appli
cation/json"   -H "Cookie: authservice_session=${SESSION}" -D $INPUT_PATH http://10.149.8.3:8008/v1/models/$
MODEL_NAME:predict

Summary:
  Total:        61.1059 secs
  Slowest:      4.0736 secs
  Fastest:      1.8944 secs
  Average:      2.1069 secs
  Requests/sec: 30.3735
  
  Total data:   283968 bytes
  Size/request: 153 bytes

Response time histogram:
  1.894 [1]     |
  2.112 [1531]  |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  2.330 [260]   |■■■■■■■
  2.548 [0]     |
  2.766 [0]     |
  2.984 [0]     |
  3.202 [0]     |
  3.420 [0]     |
  3.638 [0]     |
  3.856 [0]     |
  4.074 [64]    |■■


Latency distribution:
  10% in 1.9795 secs
  25% in 1.9961 secs
  50% in 2.0185 secs
  75% in 2.0769 secs
  90% in 2.1871 secs
  95% in 2.2117 secs
  99% in 3.9758 secs

Details (average, fastest, slowest):
  DNS+dialup:   0.0001 secs, 1.8944 secs, 4.0736 secs
  DNS-lookup:   0.0000 secs, 0.0000 secs, 0.0000 secs
  req write:    0.0000 secs, 0.0000 secs, 0.0006 secs
  resp wait:    2.1067 secs, 1.8944 secs, 4.0699 secs
  resp read:    0.0000 secs, 0.0000 secs, 0.0004 secs

Status code distribution:
  [200] 1856 responses
~~~

~~~bash
Device 0 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  77 / 400 W
 GPU[                               0%] MEM[|                      2.6G/85.9G]
 Device 1 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  40°C FAN N/A% POW  74 / 400 W
 GPU[                               0%] MEM[|||||                 12.5G/85.9G]
 Device 2 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  37°C FAN N/A% POW  75 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 3 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  40°C FAN N/A% POW  75 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 4 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  41°C FAN N/A% POW  77 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 5 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  75 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 6 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  38°C FAN N/A% POW  76 / 400 W
 GPU[                               0%] MEM[|                      2.3G/85.9G]
 Device 7 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 kB/s
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  73 / 400 W
 GPU[                               0%] MEM[|                      3.0G/85.9G]
   ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
100│                                                                                             MAX GPU│
   │                                                                                             MAX MEM│
75%│                                                                                                    │
   │                                                                                                    │
50%│                ┌───────────────────┐   ┌─────┐ ┌───────┐ ┌─┐ ┌───┐                                 │
   │                │                   └───┘     └─┘       └─┘ └─┘   │                                 │
25%│────────────────┼─────────────────────────────────────────────────┼─────────────────────────────────│
 0%│────────────────┘                                                 └─────────────────────────────────│
   └────────────────────────────────────────────────────────────────────────────────────────────────────┘

### Manual Scaling
Enable replicas=13
~~~
~~~bash
user8@bcm10-headnode:~/kfp/llama$ hey -z 160s -c 800 -m POST -host ${SERVICE_HOSTN
AME} -H "Content-Type: application/json"   -H "Cookie: authservice_session=${SESSI
ON}" -D $INPUT_PATH http://10.149.8.3:8008/v1/models/$MODEL_NAME:predict

Summary:
  Total:        172.7178 secs
  Slowest:      19.9561 secs
  Fastest:      0.1990 secs
  Average:      4.4735 secs
  Requests/sec: 167.0528
  
  Total data:   4359659 bytes
  Size/request: 152 bytes

Response time histogram:
  0.199 [1]     |
  2.175 [2754]  |■■■■■■■
  4.150 [14776] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  6.126 [6924]  |■■■■■■■■■■■■■■■■■■■
  8.102 [1947]  |■■■■■
  10.078 [462]  |■
  12.053 [147]  |
  14.029 [780]  |■■
  16.005 [221]  |■
  17.980 [313]  |■
  19.956 [206]  |■


Latency distribution:
  10% in 2.1806 secs
  25% in 2.4227 secs
  50% in 3.9856 secs
  75% in 4.6178 secs
  90% in 6.4068 secs
  95% in 12.1263 secs
  99% in 17.5599 secs

Details (average, fastest, slowest):
  DNS+dialup:   0.0010 secs, 0.1990 secs, 19.9561 secs
  DNS-lookup:   0.0000 secs, 0.0000 secs, 0.0000 secs
  req write:    0.0002 secs, 0.0000 secs, 0.0877 secs
  resp wait:    4.4713 secs, 0.1990 secs, 19.9560 secs
  resp read:    0.0000 secs, 0.0000 secs, 0.0033 secs

Status code distribution:
  [200] 28531 responses

Error distribution:
  [322] Post http://10.149.8.3:8008/v1/models/llama7b:predict: net/http: request canceled (Client.Timeout exceeded while awaiting headers)
~~~

~~~bash
   Device 0 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.00
 GPU 1155MHz MEM 1593MHz TEMP  40°C FAN N/A% POW  77 / 400 W
 GPU[                               0%] MEM[|||||                 12.9G/

 Device 1 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 58.00 MB/s TX: 9.00
 GPU 1410MHz MEM 1593MHz TEMP  42°C FAN N/A% POW 123 / 400 W
 GPU[|||||||||||||                 38%] MEM[|||||                 12.5G/

 Device 2 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.00
 GPU 1155MHz MEM 1593MHz TEMP  38°C FAN N/A% POW  74 / 400 W
 GPU[                               0%] MEM[|||||                 12.5G/

 Device 3 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 56.00 MB/s TX: 12.0
 GPU 1410MHz MEM 1593MHz TEMP  43°C FAN N/A% POW 120 / 400 W
 GPU[||||||||||||                  35%] MEM[|||||                 12.5G/

 Device 4 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.00
 GPU 1155MHz MEM 1593MHz TEMP  41°C FAN N/A% POW  76 / 400 W
 GPU[                               0%] MEM[|                      2.3G/

 Device 5 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 49.00 MB/s TX: 10.0
 GPU 1305MHz MEM 1593MHz TEMP  41°C FAN N/A% POW 106 / 400 W
 GPU[||||||||||||                  36%] MEM[|||||                 12.5G/

 Device 6 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 51.00 MB/s TX: 10.0
 GPU 1410MHz MEM 1593MHz TEMP  40°C FAN N/A% POW 122 / 400 W
 GPU[||||||||||||                  36%] MEM[|||||                 12.5G/

 Device 7 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 56.00 MB/s TX: 5.00
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW 105 / 400 W
 GPU[                               0%] MEM[|||||                 13.2G/
   ┌──────────────────────────────────────────────────────────────────┐
100│                                                           MAX GPU│
75%│                                                           MAX MEM│
50%│──┐ ┌───────┐ ┌─┐ ┌─────┐ ┌───┐                                   │
25%│──┴─┴───────┴─┴─┴─┴─────┴─┴───┴─┬─────────────────────────────────│
 0%│                                └─────────────────────────────────│
   └──────────────────────────────────────────────────────────────────┘


 Device 0 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 56.00 MB/s TX: 11.00 M
 GPU 1410MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  86 / 400 W
 GPU[||||||||||||||||              49%] MEM[||||                  11.0G/85.

 Device 1 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 53.00 MB/s TX: 9.000 M
 GPU 1350MHz MEM 1593MHz TEMP  39°C FAN N/A% POW 108 / 400 W
 GPU[||||||||||||                  36%] MEM[||||                  11.0G/85.

 Device 2 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 65.00 MB/s TX: 12.00 M
 GPU 1410MHz MEM 1593MHz TEMP  41°C FAN N/A% POW 117 / 400 W
 GPU[||||||||||||                  36%] MEM[||||                  11.0G/85.

 Device 3 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 k
 GPU 210MHz  MEM 1593MHz TEMP  39°C FAN N/A% POW  64 / 400 W
 GPU[                               0%] MEM[                       0.7G/85.

 Device 4 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 53.00 MB/s TX: 10.00 M
 GPU 1410MHz MEM 1593MHz TEMP  43°C FAN N/A% POW 117 / 400 W
 GPU[||||||||||||                  36%] MEM[||||                  11.0G/85.

 Device 5 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 67.00 MB/s TX: 12.00 M
 GPU 1410MHz MEM 1593MHz TEMP  41°C FAN N/A% POW 121 / 400 W
 GPU[||||||||||||                  37%] MEM[||||                  11.0G/85.

 Device 6 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 k
 GPU 210MHz  MEM 1593MHz TEMP  36°C FAN N/A% POW  62 / 400 W
 GPU[                               0%] MEM[                       0.7G/85.

 Device 7 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 k
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  77 / 400 W
 GPU[                               0%] MEM[||||                  11.1G/85.
   ┌──────────────────────────────────────────────────────────────────────┐
100│                                                               MAX GPU│
75%│                                                               MAX MEM│
50%│──────┐ ┌───────┐ ┌─┐ ┌─┐ ┌─┐ ┌───┐ ┌─────┐ ┌─────┐                   │
25%│      └─┘       └─┘ └─┘ └─┘ │ │   └─┘     │ │     │                   │
 0%│────────────────────────────┴─┴───────────┴─┴─────┴───────────────────│
   └──────────────────────────────────────────────────────────────────────┘

Device 0 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 k
 GPU 1155MHz MEM 1593MHz TEMP  38°C FAN N/A% POW  73 / 400 W
 GPU[                               0%] MEM[||||                  11.0G/85.

 Device 1 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 62.00 MB/s TX: 12.00 M
 GPU 1410MHz MEM 1593MHz TEMP  40°C FAN N/A% POW 121 / 400 W
 GPU[||||||||||||                  35%] MEM[||||                  11.0G/85.

 Device 2 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 64.00 MB/s TX: 11.00 M
 GPU 1410MHz MEM 1593MHz TEMP  41°C FAN N/A% POW 118 / 400 W
 GPU[|||||||||||||                 38%] MEM[||||                  11.0G/85.

 Device 3 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 k
 GPU 210MHz  MEM 1593MHz TEMP  39°C FAN N/A% POW  63 / 400 W
 GPU[                               0%] MEM[                       0.7G/85.

 Device 4 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 57.00 MB/s TX: 11.00 M
 GPU 1320MHz MEM 1593MHz TEMP  43°C FAN N/A% POW 111 / 400 W
 GPU[|||||||||||||                 40%] MEM[||||                  11.0G/85.

 Device 5 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 55.00 MB/s TX: 12.00 M
 GPU 1410MHz MEM 1593MHz TEMP  41°C FAN N/A% POW 122 / 400 W
 GPU[|||||||||||||                 40%] MEM[||||                  11.0G/85.

 Device 6 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 k
 GPU 210MHz  MEM 1593MHz TEMP  36°C FAN N/A% POW  62 / 400 W
 GPU[                               0%] MEM[                       0.7G/85.

 Device 7 [NVIDIA A100-SXM4-80GB] PCIe GEN 4@16x RX: 0.000 kB/s TX: 0.000 k
 GPU 1155MHz MEM 1593MHz TEMP  39°C FAN N/A% POW  76 / 400 W
 GPU[                               0%] MEM[||||                  11.1G/85.
 ~~~