JOB_NAME="fluxjobaca"
RESOURCE_GROUP="gpuaca"
ENVIRONMENT="gpuenvaca"
STORAGE_ACCOUNT_NAME="fluxstorageaca"
LOCATION="australiaeast"
QUEUE_NAME="fluxjob"
CONTAINER_REGISTRY_NAME="zecloud"
CONTAINER_IMAGE_NAME="sdjob:v2"
az storage account create --name "$STORAGE_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" --location "$LOCATION" --sku Standard_LRS --kind StorageV2
az storage queue create --name "$QUEUE_NAME" --account-name "$STORAGE_ACCOUNT_NAME" --connection-string "$QUEUE_CONNECTION_STRING"
az storage queue create --name "finished$QUEUE_NAME" --account-name "$STORAGE_ACCOUNT_NAME" --connection-string "$QUEUE_CONNECTION_STRING"
QUEUE_CONNECTION_STRING=$(az storage account show-connection-string -g $RESOURCE_GROUP --name $STORAGE_ACCOUNT_NAME --query connectionString --output tsv)
az containerapp job create --name "$JOB_NAME" 
--resource-group "$RESOURCE_GROUP" 
--environment "$ENVIRONMENT" 
--trigger-type "Event" 
--replica-timeout 1800 
--replica-retry-limit 2 
--min-executions 0 
--max-executions 1 
--polling-interval 60 
--scale-rule-name "queue" 
--scale-rule-type "azure-queue" 
--scale-rule-metadata "accountName=$STORAGE_ACCOUNT_NAME" "queueName=$QUEUE_NAME" "queueLength=1" 
--scale-rule-auth "connection=connection-string-secret" 
--image "$CONTAINER_REGISTRY_NAME.azurecr.io/$CONTAINER_IMAGE_NAME" 
--cpu 4 
--memory "15Gi" 
--secrets "connection-string-secret=$QUEUE_CONNECTION_STRING" 
--registry-server "$CONTAINER_REGISTRY_NAME.azurecr.io"  
--mi-system-assigned  
--registry-identity 'system' 
--workload-profile-name "NC8as-T4" 
--env-vars "INPUTQUEUENAME=$QUEUE_NAME" "BLOBCONTAINERNAME=$QUEUE_NAME" "FINISHEDQUEUENAME=finished$QUEUE_NAME" "azstorageconnstring=secretref:connection-string-secret" 