#!/bin/bash
set -e

ACR_NAME="youracrname"
AKS_RESOURCE_GROUP="your-rg"
AKS_CLUSTER_NAME="your-aks"
NAMESPACE="${NAMESPACE:-dev}"
TAG="${NAMESPACE}"

echo "🚀 Building Docker images..."
docker build -t $ACR_NAME.azurecr.io/db-proxy:$TAG ./db-proxy
docker build -t $ACR_NAME.azurecr.io/perspective-service:$TAG ./perspective-service
docker build -t $ACR_NAME.azurecr.io/columnstate-service:$TAG ./columnstate-service
docker build -t $ACR_NAME.azurecr.io/filtermodel-service:$TAG ./filtermodel-service

echo "📦 Pushing images to ACR..."
az acr login --name $ACR_NAME
docker push $ACR_NAME.azurecr.io/db-proxy:$TAG
docker push $ACR_NAME.azurecr.io/perspective-service:$TAG
docker push $ACR_NAME.azurecr.io/columnstate-service:$TAG
docker push $ACR_NAME.azurecr.io/filtermodel-service:$TAG

echo "🔑 Connecting to AKS cluster..."
az aks get-credentials --resource-group $AKS_RESOURCE_GROUP --name $AKS_CLUSTER_NAME

echo "☸️ Deploying manifests to $NAMESPACE..."
kubectl apply -f k8s/$NAMESPACE/

echo "✅ Deployment complete. Checking pods and services..."
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE
