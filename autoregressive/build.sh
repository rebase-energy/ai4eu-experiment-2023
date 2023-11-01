TAG=greenlytics/ai4eu:autoregressive-0.1
docker buildx build --platform=linux/amd64 -t $TAG .
docker push $TAG