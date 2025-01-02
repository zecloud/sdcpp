RESOURCE_GROUP="agentsdcpp"
ENVIRONMENT="gpuwp"
STORAGE_ACCOUNT_NAME="fluxstorageaca"
QUEUE_NAME="fluxjob"
NAMESPACE="agentvideo-namespace"
LOCATION="westus3"
APP_NAME="sdcppdaprapp"
CONTAINER_REGISTRY_NAME="zecloud"
CONTAINER_IMAGE_NAME="sdcppdaprapp:latest"
DAPR_STORE_NAME="fluxstatestore"
az storage account create --name "$STORAGE_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" --location "$LOCATION" --sku Standard_LRS --kind StorageV2
az servicebus namespace create --name "$NAMESPACE" --resource-group "$RESOURCE_GROUP" --location "$LOCATION" --sku  Basic 
az servicebus queue create --name "$QUEUE_NAME" --namespace-name "$NAMESPACE" --resource-group "$RESOURCE_GROUP"
az servicebus queue create --name "finished$QUEUE_NAME" --namespace-name "$NAMESPACE" --resource-group "$RESOURCE_GROUP"

az containerapp env dapr-component set --name "$ENVIRONMENT"  --dapr-component-name "$DAPR_STORE_NAME" --resource-group "$RESOURCE_GROUP" --yaml statestore.yaml
az containerapp env dapr-component set --name "$ENVIRONMENT"  --dapr-component-name "pubsubcomponent" --resource-group "$RESOURCE_GROUP" --yaml pubsub.yaml
            #ecad9095-ac7a-4662-bcb6-af6697e65570                           
az containerapp create 
--name $APP_NAME 
--resource-group $RESOURCE_GROUP 
--environment $ENVIRONMENT 
--image "$CONTAINER_REGISTRY_NAME.azurecr.io/$CONTAINER_IMAGE_NAME" 
--enable-dapr 
--dapr-app-protocol "grpc" 
--dapr-app-id "$APP_NAME" 
--dapr-app-port 50051 
--ingress internal 
--workload-profile-name "gpua100" 
--registry-identity 'system' 
--registry-server "$CONTAINER_REGISTRY_NAME.azurecr.io" 
--system-assigned 
--min-replicas 0  
--max-replicas 1  
--cpu 4 
--memory "15Gi" 
--scale-rule-name "sbqueue" 
--scale-rule-type "azure-servicebus" 
--scale-rule-metadata "queueName=$QUEUE_NAME" "namespace=$NAMESPACE"  "messageCount=5" 
--scale-rule-identity System 
--env-vars "DAPR_STORE_NAME=$DAPR_STORE_NAME"

#--scale-rule-auth "connection=connection-string-secret" 
#--query properties.configuration.ingress.fqdn 