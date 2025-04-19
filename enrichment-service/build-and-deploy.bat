docker build -t enrichment-service .
aws lightsail push-container-image --region ap-northeast-1 --service-name enrichment-service --label container --image enrichment-service:latest
aws lightsail create-container-service-deployment --region ap-northeast-1 --cli-input-json file://lc.json