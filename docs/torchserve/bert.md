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

### For Torchserve
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