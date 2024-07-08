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


# Implementation
## Cluster architecture
The cluster architecture can be found in the following image:
![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/3e0e9f35-107d-4f11-8c99-bb631664bab6)

Kubelet and a container runtime (in this case CRI-O was installed) has to be configured in every node.

## Microservices overview
### Doc conversion microservice
![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/90ba5407-81da-4cb1-afc8-6dd4c2c78cda)
### Image upload microservice
![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/0f0fe561-b5ca-4694-8486-dd5a7da8015f)

## Infrastructure considerations
The type of instance has to be a t2.medium so kubernetes can run smoothly without any performance issues for the control plane node. The operating system has to be Ubuntu because kubeadm, kubectl and crio does not have a yum repository as it was deprecated at the beggining of this year: https://kubernetes.io/blog/2023/08/31/legacy-package-repository-deprecation/

There are only deb repositories available. Without a registry, the installation of the cluster components should be done by compiling binaries and tinkering with systemd processes and iptables configurations.

## Interal load balancing
In Kubernetes, a ClusterIP service type creates an internal load balancer that exposes the service to pods within the same cluster. ClusterIP services do not have a public IP address and can only be accessed by pods within the cluster.
![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/8ff53624-dc62-408a-9419-632b5a95a630)

## Expose service
### Nodeport ❌
![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/47bbb198-079e-4ca2-b2f0-9e1ba06b5eea)
A Nodeport service opens the same port in all worker instances.
This approach works but it does not scale well because there is the need of using one port per service.

### Load balancer ❌
![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/32a7ac66-b26a-42a0-9652-145fa0cd4715)
A Load balancer service type creates an exernal load balancer with the necessary network configurations to connect it to all the worker nodes in the cluster
This solution does not scale well because there is the need to create one load balancer per service and the implementation can be very costly.

### Ingress ✅
![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/c8bc006f-b230-4886-a7de-c0a492398404)
An ingress type acts as a routing entry point to map different routes to services in the cluster. An ingress has to be implemented via an ingress controller: https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/
The controller can be of load balancer type because we can't create it due to lack of iam permissions. An alternative approach is to create this controller via a Nodeport service. The controller used in this case is a nginx ingress controller installed via a helm chart that can be found here: https://artifacthub.io/packages/helm/ingress-nginx/ingress-nginx

## Metric server and HPA
Only hardware metrics were included (CPU and Memory), the metric server installed can be found here: https://github.com/kubernetes-sigs/metrics-server/blob/master/README.md
![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/34b91a25-6d4d-4301-a2d4-629ea69b7677)

Each microservice deployment has the following resource requests and limits:
![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/0a7638a6-0dd5-437e-9513-1b8d375072ff)

The paradigm of no CPU limits plus Memory requests = Memory limits is a widely used one and it can avoid problems like OOMErrors and peaks of CPU usage. More info here: 
- CPU limits: https://home.robusta.dev/blog/stop-using-cpu-limits
- Memory requests = limits: https://home.robusta.dev/blog/kubernetes-memory-limit

## DNS resolution in Ubuntu instances with kubeadm
There is a pending issue with how Ubuntu resolves nameservers in order to reach external DNS names: https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/#known-issues

![imagen](https://github.com/FcoJesusDiaz/PlanTic-final-project/assets/72586746/57b82a2a-dd45-4219-a785-1b7636e55c8d)

A workaround to this issue is to add up to 3 namservers in the kuberentes configmap used to configure the coredns service (the one that has to resolve external traffic).
