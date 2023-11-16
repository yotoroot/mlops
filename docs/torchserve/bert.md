---
layout: default
title: BERT 
parent: Torchserve
nav_order: 1
---

# Bert Classification Setup
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

### BERT Sequence Classification
#### What is BERT sequence classification?

BERT sequence classification is a natural language processing (NLP) task that involves assigning a label or category to a piece of text. BERT (Bidirectional Encoder Representations from Transformers) is a state-of-the-art deep learning model that has been shown to be very effective for a variety of NLP tasks, including sequence classification.

How does BERT sequence classification work?

BERT sequence classification works by first representing the input text as a sequence of vectors. These vectors are then fed into a BERT model, which learns to represent the relationships between the words in the text. The output of the BERT model is then used to predict the label or category of the text.

#### Applications of BERT sequence classification

BERT sequence classification has a wide range of applications, including:

Sentiment analysis
Topic classification
Spam filtering
News classification
Customer service classification

### Prepare the Model
For PVC setup. [Kserve's PVC Link](https://kserve.github.io/website/0.11/modelserving/v1beta1/torchserve/model-archiver/#221-create-propertiesjson-file)

Setup torchserve .mar file

[torch serve's link](https://github.com/pytorch/serve/tree/master/examples/Huggingface_Transformers)
~~~bash
torch-model-archiver --model-name BERTSeqClassification --version 1.0 --serialized-file Transformer_model/pytorch_model.bin --handler ./Transformer_kserve_handler.py --extra-files "Transformer_model/config.json,./setup_config.json,./Seq_classification_artifacts/index_to_name.json,./Transformer_handler_generalized.py"
~~~

[KServe's Link ](https://github.com/kserve/kserve/tree/master/docs/samples/v1beta1/torchserve/v2/bert)
~~~bash
kubectl exec -it model-store-pod -c model-store -n kubeflow-user-example-com -- mkdir /pv/model-store/
kubectl cp BERTSeqClassification.mar model-store-pod:/pv/model-store/BERTSeqClassification.mar -c model-store -n kubeflow-user-example-com
~~~

Setup config file
in kserve/docs/samples/v1beta1/torchserve/v2/bert
~~~bash
kubectl exec -it model-store-pod -c model-store -n kubeflow-user-example-com -- mkdir /pv/config/
kubectl cp config.properties model-store-pod:/pv/config/config.properties -c model-store -n kubeflow-user-example-com
~~~

To verify all files are in place
~~~bash
kubectl exec -it model-store-pod -c model-store -n kubeflow-user-example-com -- find /pv
/pv
/pv/model-store
/pv/model-store/BERTSeqClassification.mar
/pv/config
/pv/config/config.properties
~~~

### Deploy the Inference Service
CRD for gpu inference service, gpu.yaml (verified working)

~~~yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: "torchserve-bert-v2"
spec:
  predictor:
    pytorch:
      protocolVersion: v2
      storageUri: pvc://task-pv-claim
      resources:
        limits:
          memory: 4Gi
          nvidia.com/gpu: "1"
~~~

CRD for gpu inference service, cpu.yaml (seeing timeout issue.)

~~~yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: "torchserve-bert-v2"
spec:
  predictor:
    pytorch:
      protocolVersion: v2
      storageUri: pvc://task-pv-claim
~~~

Deploy the following:
~~~bash
kubectl apply -f gpu.yaml -n kubeflow-user-example-com        
~~~

Make sure you observe the inference service in the list as below:
~~~bash
kubectl get isvc -n kubeflow-user-example-com
NAME                 URL                                                               READY   PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION                          AGE
bloom7b1             http://bloom7b1.kubeflow-user-example-com.example.com             True           100                              bloom7b1-predictor-default-00001             2d14h
sklearn-iris         http://sklearn-iris.kubeflow-user-example-com.example.com         True           100                              sklearn-iris-predictor-default-00001         2d14h
sklearn-pvc          http://sklearn-pvc.kubeflow-user-example-com.example.com          True           100                              sklearn-pvc-predictor-default-00003          46h
torchserve           http://torchserve.kubeflow-user-example-com.example.com           True           100                              torchserve-predictor-default-00001           23h
torchserve-bert      http://torchserve-bert.kubeflow-user-example-com.example.com      True           100                              torchserve-bert-predictor-default-00001      40h
torchserve-bert-v2   http://torchserve-bert-v2.kubeflow-user-example-com.example.com   True           100                              torchserve-bert-v2-predictor-default-00004   41h
~~~

### Initiate the Inference

Here we trigger the model supported by the Inference Service outside of the K8s cluster but within the corp network.
This is useful to test the networking, istio, authentication, PVC... Except the actual inference. 

~~~bash
export SERVICE_HOSTNAME=torchserve-bert-v2.kubeflow-user-example-com.example.com

curl -v \
  -H "Host: ${SERVICE_HOSTNAME}" \
  -H "Content-Type: application/json" \
  -H "Cookie: authservice_session=${SESSION}" \
  -d @./bert-input-v2.json \
  http://10.149.8.3:8008/v2/models/bert/infer
~~~
We should see the response as below:
~~~bash
*   Trying 10.149.8.3:8008...
* Connected to 10.149.8.3 (10.149.8.3) port 8008 (#0)
> GET /v2/models HTTP/1.1
> Host: torchserve-bert-v2.kubeflow-user-example-com.example.com
> User-Agent: curl/7.81.0
> Accept: */*
> Content-Type: application/json
> Cookie: authservice_session=MTcwMDAyMTU5N3xOd3dBTkRkU1F6UklOMDFDUkUxR1FWZ3pSVE5EV1ZrMFRqVk5XbGxSUmtORlZVdzFWRFJLUWxFMlRreExUbEJITlZGRE5VUk1NMEU9fJJE9ZeCR7j9rpSPZZqLyHmbMBG63jULv3fdwwL2vf46
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< content-length: 20
< content-type: application/json; charset=UTF-8
< date: Thu, 16 Nov 2023 01:02:15 GMT
< etag: "f476e6c12d909a72386a50a74a3568f263f31876"
< server: istio-envoy
< x-envoy-upstream-service-time: 29
< 
* Connection #0 to host 10.149.8.3 left intact
{"models": ["bert"]}
~~~

Below trigger the actual inference.

~~~bash
curl -v   -H "Host: ${SERVICE_HOSTNAME}"   -H "Content-Type: application/json"   -H "Cookie: authservice_session=${SESSION}"   -d @./bert-input-v2.json   http://10.149.8.3:8008/v2/models/bert/infer
*   Trying 10.149.8.3:8008...
* Connected to 10.149.8.3 (10.149.8.3) port 8008 (#0)
> POST /v2/models/bert/infer HTTP/1.1
> Host: torchserve-bert-v2.kubeflow-user-example-com.example.com
> User-Agent: curl/7.81.0
> Accept: */*
> Content-Type: application/json
> Cookie: authservice_session=MTcwMDAyMTU5N3xOd3dBTkRkU1F6UklOMDFDUkUxR1FWZ3pSVE5EV1ZrMFRqVk5XbGxSUmtORlZVdzFWRFJLUWxFMlRreExUbEJITlZGRE5VUk1NMEU9fJJE9ZeCR7j9rpSPZZqLyHmbMBG63jULv3fdwwL2vf46
> Content-Length: 271
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< content-length: 203
< content-type: application/json; charset=UTF-8
< date: Thu, 16 Nov 2023 01:02:20 GMT
< server: istio-envoy
< x-envoy-upstream-service-time: 1370
< 
* Connection #0 to host 10.149.8.3 left intact
{"id": "d3b15cad-50a2-4eaf-80ce-8b0a428bd298", "model_name": "BERTSeqClassification", "model_version": "1.0", "outputs": [{"name": "predict", "shape": [], "datatype": "BYTES", "data": ["Not Accepted"]}]}
~~~

this is bert-iput-v2.json, you can replace the body of the text string.
~~~json
{
  "id": "d3b15cad-50a2-4eaf-80ce-8b0a428bd298",
  "inputs": [{
    "name": "4b7c7d4a-51e4-43c8-af61-04639f6ef4bc",
    "shape": -1,
    "datatype": "BYTES",
    "data": "{\"text\":\"Bloomberg has decided to publish a new report on the global economy.\", \"target\":1}"
  }
  ]
}
~~~

