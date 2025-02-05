# eidf106ns

### Connecting to the server
Either from the web browser or from terminal. If from terminal, the command will be like:

    ssh -J frahman@eidf-gateway.epcc.ed.ac.uk frahman@10.24.2.61

### Setting up kubectl
If kubectl has not been installed before (or if there's some errors later), run the following commands:

    cd ~/.local/bin
    rm -rf kubectl
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    export PATH=$HOME/.local/bin:$HOME/bin:$PATH
    export KUBECONFIG=/kubernetes/config
    chmod +x ~/.local/bin/kubectl
To check if the setting is ready, run the command below:

    kubectl --namespace eidf106ns get jobs

### Create alias
To save the typing `kubectl --namespace eidf106ns`, a new command alias can be made following these steps:

    vim ~/.bashrc
    alias <new_command>='kubectl -n eidf106ns'

Save the file and reload by running this command: `source ~/.bashrc`.
Try the alias: `<new_command> get jobs`

## 1. Creating a storage PVC

To have an external storage that is accessible outside the main container (the one that runs the experiment), we need to create a storage container by providing a yaml file.

Assuming that the storage container is defined in [`01_pvc.yml`](https://github.com/rah-man/kube01/blob/main/01_pvc.yml).

Start the storage container by running these commands:

    kubectl -n eidf106ns create -f 01_pvc.yml

Check if the storage is created and runnning:

    kubectl -n eidf106ns get pvc 

If it's running, there should be a PVC with the specified name in the yaml file. This storage container needs to run first to be accessible by the main container (the experiment one).

## 2. Creating a small PVC access

This step is only needed if the main container terminates automatically when its process finishes. The reason why this is an option is because in a shared environment, if the main container keeps running even if its job is done, it will still hold the resources. If we choose not to do that, once it terminates, it will release the storage that it binds to, hence we can't access it through the main container (because it has terminated). This step is to bridge that scenario, i.e., we create a small container to open a connection to the storage, run and stop this small container whenever needed, and access the storage through this container (copy any outputs, models, etc.)

Assuming that the small container is defined in [`02_pvc_access.yml`](https://github.com/rah-man/kube01/blob/main/02_pvc_access.yml). Note that the mount path is named as `mnt/app` in the yml file.

Start the container by running:

    kubectl -n eidf106ns create -f 02_pvc_access.yml

Check if pods is running:

    kubectl -n eidf106ns get pods

Once it's running, the storage is accessible through this container pod's name, not the storage's name. To list the contents of the storage, run this command:

    kubectl -n eidf106ns exec -it <pod_name> -- ls /mnt/app

Try copy a local file (`xyz.txt`) to the storage (to copy a file from the storage, we need to have the file there first, either from the experiment output or after we copy this file and copy back to local directory). 

    kubectl -n eidf106ns cp xyz.txt <pod_name>:mnt/app/xyz.txt

To kill this container from running (when done copy/paste etc., as an option), run this command:

    kubectl -n eidf106ns delete job <job_name>

 
## 3. Running an experiment and storing some outputs

Once we have the access to the storage container, we can use it to store the experiment's outputs. We can also put the training script to the container and make a yaml file to run that particular script for training. Another way is to put the script on github and refer it in the yaml file. This section is using the github approach.

Assuming that the experiment yaml file is defined in [`03_hugface.yml`](https://github.com/rah-man/kube01/blob/main/03_hugface.yml). This is a simple sentiment classification using DistilBERT from Huggingface library on IMDB review. The training script itself is in [`train.py`](https://github.com/rah-man/kube01/blob/main/train.py).

Run this command to start the container:

    kubectl -n eidf106ns -f 03_hugface.yml

Check the logs from the pod name (need to get pods first)

    kubectl -n logs <pod_name>

When the experiment has terminated, we can run the small container to access the storage (step 2 above), check the contents of the directory, and copy the files that we want.

As usual, to kill the experiment and the small containers, run these commands:

    kubectl -n eidf106ns delete job <training_job>
    kubectl -n eidf106ns delete job <container_access_job>

