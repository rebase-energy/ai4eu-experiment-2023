TAG=greenlytics/ai4eu:autoregressive-0.2
docker buildx build --platform=linux/amd64 -t $TAG .
docker push $TAG