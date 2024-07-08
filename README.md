# Authors
- Francisco Jesús Díaz Pellejero
- Javier Villar Asensio
  
# PlanTic-final-project
Final project for Plan TIC subject. Kubeadm baremeteal cluster provisioned with ansible and 2 microservices

# Structure
The following proejct is structured as follows:
- ansible: Contains all infrastructure provisioning for configuring and setting up a kubernetes cluster with kubeadm and for uploading all manifests to it. There's an inventory and a configuration file too.
- kubernetes: Containes microservices manifests, as well as Horizontal Pod Autoscaling along a metrics server.
- microservices: Contain the flask code and Dockerfiles to deploy the conteneraized application as well as 2 scripts to upload those containers to a public container registry (docker hub) that will be used later by the pods in the cluster.
- ssh_keys: Contains ssh keys necessary to connect to EC2 instances.

# Setup
## Infrastructure
![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/5f679c35-f3b6-41d2-ba86-10c57418ad94)
The Sandbox environment was the one used to work in this project due to lighter permissions on resource creation. When activiating this environment. The terminal provided must be used to retrieve the access key, secret key, session id and default zone. All this information is under .aws/credentials and .aws/config. The value of these credentials must be pasted into the environment variables of the Dockerfile of the Image Uploader microservice in order to have IAM permissions to connect to a S3 instance.
![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/ea541008-4c6a-46dd-a651-bd75acd7effa)

An S3 bucket has to be created and its name must be pasted in the correspoding environment variable.

3 EC2 instances must be created:
- The master instance must have a master.key that will be pasted into the ssh_keys directory.
- Worker instances must have a master.key that will be pasted into the ssh_keys directory.
- The specs necessary are t3.medium instance type, Ubuntu 20_02 operating system and a security group that allows traffic on the following ports:
    - `6443/tcp` for Kubernetes API Server
    - `2379-2380` for etcd server client API
    - `10248-10260` for Kubelet API, Kube-scheduler, Kube-controller-manager, Read-Only Kubelet API, Kubelet health
    - `80,8080,443` Generic Ports
    - `30000-32767` for NodePort Services
    - `10248-10260` for Kubelet API etc
    - `30000-32767` for NodePort Services

# Ansible playbooks:
- Execute setup.yml with -i hosts.yaml to provide inventory.
- Execute kubeadm-setup.yml.
- Execute kubeadm token create --print-join-command on the master node and get the output.
- Paste the output on kubeadm-join.yaml
- ![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/0cd03937-eec2-469c-84a2-62d613eebef3)
- Execute k8s.yaml
