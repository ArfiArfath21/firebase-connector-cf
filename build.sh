destination_folder=fc-deployment_dir

rm -rf ../$destination_folder
rm -rf ../$destination_folder.zip
mkdir ../$destination_folder

rsync -av --progress . ../$destination_folder \
--exclude .venv \
--exclude __pycache__ \
--exclude *env

cd ../$destination_folder
zip -r ../$destination_folder-zipped.zip *
cd ..

gcs_destination=gs://test-bucket-aas/events/$destination_folder.zip
echo gsutil -m cp $destination_folder-zipped.zip $gcs_destination
gsutil -m cp $destination_folder-zipped.zip $gcs_destination
gcloud functions deploy firebase-connector --trigger-http \
    --gen2 --region us-central1 \
    --memory 1GiB --runtime python310 \
    --entry-point firebase_connector \
    --source $gcs_destination \
    --min-instances 1 --max-instances 100 \
    --run-service-account api-serving@burner-arfsyed.iam.gserviceaccount.com

echo run this to create new api config:
echo gcloud api-gateway api-configs create api-config-v4   --api=ps-events-api --openapi-spec=openapi2-functions-v4.yaml   --project=burner-arfsyed --backend-auth-service-account=api-serving@burner-arfsyed.iam.gserviceaccount.com

echo run this to update api gateway:
echo gcloud api-gateway gateways update ps-serving   --api=ps-events-api --api-config=api-config-v4   --location=us-central1 --project=burner-arfsyed