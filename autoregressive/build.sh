TAG=greenlytics/ai4eu-2023:autoregressive-0.3
docker buildx build --platform=linux/amd64 -t $TAG .
docker push $TAG