RESOURCE_GROUP="agentsdcpp"
ENVIRONMENT="gpuwp"
STORAGE_ACCOUNT_NAME="fluxstorageaca"
QUEUE_NAME="fluxjob"
NAMESPACE="agentvideo-namespace"
LOCATION="westus3"
APP_NAME="chainlitdaprapp"
CONTAINER_REGISTRY_NAME="zecloud"
CONTAINER_IMAGE_NAME="distsdcpp:latest"
DAPR_STORE_NAME="fluxstatestore"

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
--workload-profile-name "Consumption" 
--registry-identity 'system' 
--registry-server "$CONTAINER_REGISTRY_NAME.azurecr.io" 
--system-assigned 
--min-replicas 0  
--max-replicas 1  
--cpu 0.5 
--memory "1Gi" 

--scale-rule-name "sbqueue" 
--scale-rule-type "azure-servicebus" 
--scale-rule-metadata "queueName=$QUEUE_NAME" "namespace=$NAMESPACE"  "messageCount=5" 
--scale-rule-identity System 
--env-vars "DAPR_STORE_NAME=$DAPR_STORE_NAME"