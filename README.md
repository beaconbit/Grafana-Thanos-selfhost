
# Grafana-Thanos-selfhost" 
The python daemon is a simple webserver that scrapes data and exposes it on port 8000 in the format that prometheus expects
The storage layer is minio which is a S3 drop-in replacement
The Backend is Thanos/Prometheus, Prometheus scrapes port 8000 and passes it to the thanos instance which interfaces with the storage layer
The Frontend is Grafana which queries Thanos for data

##### start up sequence
The python daemon is stand alone
The minio instance is stand alone
The Grafana instance is stand alone

Once these three are up the backend can be launched, the backend scrapes from the python daemon and interfaces with long term storage on minio

Once the backend is running Grafana can be configured to pull data from it

# Run Python Daemon
### create a virtual environment
##### linux
    python -m venv myvirtualenvironment
    
### enter virtual environement
##### linux
    source myvirtualenvironment/bin/activate

##### windows
    myvirtualenvironment\Scripts\activate


# Run Granafa instance

# Run Minio instance
Minio is a drop in replacement for S3 object storage and is used in this case as a self hosted replacement for S3
> port 9000 needs to match the port defined in backend/objstore.yml because this is the port that the thanos instance will attempt to connect to and use as its long term storage layer
##### storage/docker-compose.yml
    services:
        minio-image:
            container_name: minio-storage-layer
            build:
                context: .
                dockerfile: Dockerfile
            restart: always
            working_dir: "/minio-image/storage"
            volumes:
                - ./Storage/minio/storage:/minio-image/storage
            ports:
                - "9000:9000"
                - "9001:9001"
            environment:
                MINIO_ROOT_USER: minio-image
                MINIO_ROOT_PASSWORD: minio-image-pass
            command: server /minio-image/storage --console-address :9001

# Run Thanos / Prometheus instance

> The host.docker.internal hostname tells docker to connect to the host network, this is windows specific - an equivalent generic solution is not available on linux and it is necessary to replace this with you machines actaul ip address.
> The port 9000 needs to match the API port expose by the minio instance defined in storage/docker-compose.yml
> the access key and secret key correspond to the MINIO_ROOT_USER and MINIO_ROOT_PASSWORD defined in storage/docker-compose.yml
##### backend/objstore.yml
    type: S3
    config:
      bucket: "thanos-bucket"
      endpoint: "host.docker.internal:9000"
      access_key: "minio-image"
      secret_key: "minio-image-pass"
      insecure: true




##### linux
    cd backend

##### linux
    docker-compose up

