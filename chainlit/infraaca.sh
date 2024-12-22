RESOURCE_GROUP="gpuaca"
ENVIRONMENT="gpuenvp"
STORAGE_ACCOUNT_NAME="fluxstorageaca"
LOCATION="australiaeast"
APP_NAME="sdchatbot"
CONTAINER_REGISTRY_NAME="zecloud"
CONTAINER_IMAGE_NAME="sdcppchatbot:latest"
az containerapp create 
--name $APP_NAME 
--resource-group $RESOURCE_GROUP 
--environment $ENVIRONMENT 
--image "$CONTAINER_REGISTRY_NAME.azurecr.io/$CONTAINER_IMAGE_NAME" 
--target-port 80 
--ingress external 
--query properties.configuration.ingress.fqdn 
--workload-profile-name "NC8as-T4" 
--registry-identity 'system' 
--registry-server "$CONTAINER_REGISTRY_NAME.azurecr.io" 
--system-assigned 
--min-replicas 0  
--max-replicas 1  
--cpu 4 
--memory "15Gi" 