#!/bin/bash

# Export Variables
export PROJECT_ID="qwiklabs-gcp-02-056920"
export REGION="us-central1"
export DATASET_DISPLAY_NAME="Flower Classification Dataset"
export MODEL_DISPLAY_NAME="Flower_Classification_Model"
export CSV_URI="gs://cloud-training/mlongcp/v3.0_MLonGC/toy_data/flowers_toy.csv"
export TRAINING_BUDGET=8  # Maximum node hours
export SOURCE_MODEL_ID="your-source-model-id"  # Replace with your source model ID if needed

# Set project
gcloud config set project $PROJECT_ID

# Set the AI region
gcloud config set ai/region $REGION

# Enable necessary APIs
gcloud services enable \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com \
    storage.googleapis.com

# Grant necessary permissions to Vertex AI Service Agent
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:service-604463606520@gcp-sa-aiplatform.iam.gserviceaccount.com \
  --role=roles/storage.objectViewer

# Task 1: Create Dataset and Import Images

# Create the Dataset
export DATASET_ID=$(gcloud beta ai datasets create --region=$REGION \
    --display-name=$DATASET_DISPLAY_NAME \
    --metadata-schema-uri=gs://google-cloud-aiplatform/schema/dataset/metadata/image_1.0.0.yaml \
    --metadata='{"schema": "gs://google-cloud-aiplatform/schema/dataset/metadata/image_1.0.0.yaml"}' \
    --format="value(name)")

echo "Dataset created with ID: $DATASET_ID"

# Import Data
gcloud beta ai datasets import-data $DATASET_ID --region=$REGION \
    --import-schema-uri=gs://google-cloud-aiplatform/schema/dataset/ioformat/image_classification_io_format_1.0.0.yaml \
    --input-config='{
      "gcsSource": {
        "uris": ["'"$CSV_URI"'"]
      }
    }'

echo "Data import started from $CSV_URI"

# Wait for the import to complete (typically 15 minutes)
echo "Waiting for data import to complete..."
sleep 900 # Wait for 15 minutes

echo "Data import completed for dataset: $DATASET_ID"

# Optional: Copy an existing model if needed
# gcloud ai models copy $SOURCE_MODEL_ID \
#    --destination-model-display-name=$MODEL_DISPLAY_NAME \
#    --destination-region=$REGION

#echo "Model copied with ID: $SOURCE_MODEL_ID to region: $REGION"
