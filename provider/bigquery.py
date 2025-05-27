import json
import logging
from typing import Any

from google.cloud import bigquery
from google.oauth2 import service_account

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

logger = logging.getLogger(__name__)

class BigQueryProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate BigQuery credentials by attempting to list datasets.
        
        Args:
            credentials: Dict containing project_id and service_account_key
        
        Raises:
            ToolProviderCredentialValidationError: If validation fails
        """
        try:
            # Extract credentials
            project_id = credentials.get("project_id")
            service_account_key_json = credentials.get("service_account_key")
            
            if not project_id or not service_account_key_json:
                raise ToolProviderCredentialValidationError(
                    "Project ID and Service Account Key are required"
                )
            
            # Parse service account key
            try:
                service_account_info = json.loads(service_account_key_json)
            except json.JSONDecodeError:
                raise ToolProviderCredentialValidationError(
                    "Invalid service account key: Not valid JSON"
                )
                
            # Create credentials
            credentials_obj = service_account.Credentials.from_service_account_info(
                service_account_info
            )
            
            # Initialize BigQuery client
            client = bigquery.Client(
                project=project_id,
                credentials=credentials_obj
            )
            
            # Test connection by listing datasets (limited to 1 for efficiency)
            datasets = list(client.list_datasets(max_results=1))
            logger.info(f"Successfully validated BigQuery credentials for project: {project_id}")
            
        except Exception as e:
            logger.exception("BigQuery credentials validation failed")
            raise ToolProviderCredentialValidationError(str(e)) 