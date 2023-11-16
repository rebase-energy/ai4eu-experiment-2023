TAG=greenlytics/ai4eu-2023:validation-1
docker buildx build --platform=linux/amd64 -t $TAG .
docker push $TAG