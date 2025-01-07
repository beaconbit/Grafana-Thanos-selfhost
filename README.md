
"# Grafana-Thanos-selfhost" 

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




##### linux
    cd backend

##### linux
    docker-compose up

