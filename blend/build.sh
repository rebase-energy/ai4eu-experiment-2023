TAG=greenlytics/ai4eu-2023:blend-model-4
docker buildx build --platform=linux/amd64 -t $TAG .
docker push $TAG