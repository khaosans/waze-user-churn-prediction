import subprocess
import os
import logging
from google.cloud import aiplatform
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set your variables
PROJECT_ID = 'qwiklabs-gcp-02-b36454f25ce2'
KEY_FILE = 'keyfile.json'
REGION = 'us-central1'
IMPORT_FILE_PATH = "cloud-training/mlongcp/v3.0_MLonGC/toy_data/hmdb_split1_5classes_all_toy.csv"
DATASET_NAME = "video_classification_dataset"
MODEL_NAME = "video_classification_model"

SERVICE_ACCOUNT_EMAIL = f"{PROJECT_ID}@{PROJECT_ID}.iam.gserviceaccount.com"

def create_service_account_key(key_file_path, service_account_email):
    """
    Create a service account key and save it to a specified file.

    Args:
    key_file_path (str): Path where the key file will be saved.
    service_account_email (str): Email of the service account for which the key will be created.
    """
    # Construct the gcloud command
    gcloud_command = [
        "gcloud", "iam", "service-accounts", "keys", "create", key_file_path,
        "--iam-account", service_account_email
    ]

    # Execute the gcloud command
    try:
        subprocess.run(gcloud_command, check=True)
        print(f"Service account key created and saved to {key_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

    # Verify the key file
    if os.path.exists(key_file_path):
        print(f"Key file {key_file_path} is present.")
    else:
        print(f"Failed to create key file {key_file_path}.")

def enable_apis(project_id):
    """Enable the necessary Google Cloud APIs for the project."""
    logging.info('Enabling necessary APIs...')
    credentials = service_account.Credentials.from_service_account_file(KEY_FILE)
    service = build('serviceusage', 'v1', credentials=credentials)

    apis = [
        'aiplatform.googleapis.com',
        'storage.googleapis.com',
        'iam.googleapis.com',
        'bigquery.googleapis.com',
        'compute.googleapis.com'
    ]

    for api in apis:
        request = service.services().enable(
            name=f'projects/{project_id}/services/{api}'
        )
        response = request.execute()
        logging.info(f'Enabled API {api}: {response}')

def use_service_account_key(key_file_path):
    """Authenticate with the service account key and interact with Google Cloud services."""
    logging.info(f'Authenticating with service account key from {key_file_path}...')
    credentials = service_account.Credentials.from_service_account_file(key_file_path)
    aiplatform.init(credentials=credentials, project=PROJECT_ID, location=REGION)
    logging.info('Authenticated with Vertex AI using service account key.')

def grant_roles(project_id, service_account_email):
    """Grant necessary roles to the service account."""
    logging.info(f'Granting roles to service account: {service_account_email}...')
    roles = [
        'roles/aiplatform.admin',
        'roles/storage.admin',
        'roles/iam.serviceAccountUser',
        'roles/bigquery.admin',
        'roles/compute.admin'
    ]

    credentials = service_account.Credentials.from_service_account_file(KEY_FILE)
    service = build('cloudresourcemanager', 'v1', credentials=credentials)

    policy_request = service.projects().getIamPolicy(resource=project_id, body={}).execute()
    policy_bindings = policy_request.get('bindings', [])

    for role in roles:
        role_binding = next((binding for binding in policy_bindings if binding['role'] == role), None)
        if role_binding:
            role_binding['members'].append(f"serviceAccount:{service_account_email}")
        else:
            policy_bindings.append({
                'role': role,
                'members': [f"serviceAccount:{service_account_email}"]
            })

    policy_request['bindings'] = policy_bindings
    policy_body = {'policy': policy_request}

    response = service.projects().setIamPolicy(resource=project_id, body=policy_body).execute()
    logging.info(f'Granted roles to {service_account_email}: {response}')

def find_service_account(project_id, service_account_id):
    """Find a service account by its ID."""
    logging.info(f'Finding service account with ID: {service_account_id}...')
    credentials = service_account.Credentials.from_service_account_file(KEY_FILE)
    service = build('iam', 'v1', credentials=credentials)

    request = service.projects().serviceAccounts().list(name=f'projects/{project_id}')
    response = request.execute()

    for account in response.get('accounts', []):
        if account['email'].startswith(service_account_id):
            logging.info(f'Found service account: {account["email"]}')
            return account["email"]

    logging.warning(f'Service account with ID "{service_account_id}" not found.')
    return None

def create_video_classification_dataset():
    """Create a video classification dataset and import data."""
    logging.info("Creating video classification dataset...")

    # Initialize the AI Platform
    aiplatform.init(credentials=service_account.Credentials.from_service_account_file(KEY_FILE),
                    project=PROJECT_ID, location=REGION)

    # Create the dataset
    dataset = aiplatform.VideoDataset.create(
        display_name=DATASET_NAME,
        gcs_source=[f"gs://{IMPORT_FILE_PATH}"],
        import_schema_uri=aiplatform.schema.dataset.ioformat.video.classification,
        sync=True
    )

    logging.info(f"Dataset created: {dataset.resource_name}")
    return dataset

def train_automl_video_classification_model(dataset):
    """Train an AutoML video classification model."""
    logging.info("Starting AutoML video classification model training...")

    # Initialize the AI Platform
    aiplatform.init(credentials=service_account.Credentials.from_service_account_file(KEY_FILE),
                    project=PROJECT_ID, location=REGION)

    # Train the model
    model = aiplatform.AutoMLVideoTrainingJob(
        display_name=MODEL_NAME,
        prediction_type="classification"
    )

    model_response = model.run(
        dataset=dataset,
        model_display_name=MODEL_NAME,
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        sync=True
    )

    logging.info(f"Model training started: {model_response.resource_name}")

def main():
    # Create service account key
    create_service_account_key(KEY_FILE, SERVICE_ACCOUNT_EMAIL)

    # Enable APIs
    enable_apis(PROJECT_ID)

    # Authenticate with service account
    use_service_account_key(KEY_FILE)

    # Find service account (if needed for role assignment)
    service_account_email = find_service_account(PROJECT_ID, 'your-service-account-id')  # replace 'your-service-account-id'

    # Grant roles to service account
    if service_account_email:
        grant_roles(PROJECT_ID, service_account_email)

    # Create the video classification dataset
    dataset = create_video_classification_dataset()

    # Train the AutoML video classification model
    train_automl_video_classification_model(dataset)

if __name__ == "__main__":
    main()
