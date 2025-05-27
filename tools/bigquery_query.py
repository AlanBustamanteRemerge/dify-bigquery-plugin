import json
import logging
import datetime
from collections.abc import Generator
from typing import Any, Dict, Optional

from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core.exceptions import BadRequest

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# Configure logging
logger = logging.getLogger(__name__)

# Constants for query limitations
MAX_BYTES_PROCESSED = 5 * 1024 * 1024 * 1024  # 5 GB limit
BYTES_PER_DOLLAR = 5 * 1024 * 1024 * 1024  # Approximate cost of $1 per 5 GB
COST_THRESHOLD_WARNING = 1.0  # Warn if cost estimate exceeds $1

class BigQueryQueryTool(Tool):
    def _estimate_query_cost(self, client: bigquery.Client, query: str) -> Dict[str, Any]:
        """
        Estimate the cost of a query by performing a dry run.
        
        Args:
            client: BigQuery client
            query: SQL query to estimate
            
        Returns:
            Dictionary with cost estimation details
        """
        job_config = bigquery.QueryJobConfig(dry_run=True)
        query_job = client.query(query, job_config=job_config)
        
        # Calculate estimated cost
        bytes_processed = query_job.total_bytes_processed or 0
        estimated_cost = bytes_processed / BYTES_PER_DOLLAR if bytes_processed else 0
        
        return {
            "bytes_processed": bytes_processed,
            "estimated_cost_usd": estimated_cost,
            "exceeds_limit": bytes_processed > MAX_BYTES_PROCESSED,
            "estimated_cost_warning": estimated_cost > COST_THRESHOLD_WARNING
        }
    
    def _log_query(self, query: str, estimation: Dict[str, Any], success: bool, error: Optional[str] = None):
        """
        Log details about the query execution.
        
        Args:
            query: The SQL query
            estimation: Cost estimation details
            success: Whether the query executed successfully
            error: Error message if the query failed
        """
        log_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "query": query,
            "bytes_processed": estimation["bytes_processed"],
            "estimated_cost_usd": estimation["estimated_cost_usd"],
            "success": success
        }
        
        if error:
            log_data["error"] = error
            
        logger.info(f"BigQuery Query Execution: {json.dumps(log_data)}")
        
        # In a production environment, you might want to log to a file or database
        try:
            # Ensure logs directory exists
            import os
            os.makedirs("logs", exist_ok=True)
            
            with open("logs/query_logs.jsonl", "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception as e:
            logger.warning(f"Failed to write to query log file: {e}")

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Execute a SQL query against BigQuery and return the results.
        
        Args:
            tool_parameters: Dictionary containing query parameters
                - query: SQL query to execute
                - max_results: Maximum number of results to return
        
        Yields:
            ToolInvokeMessage: Query results or error message
        """
        # Extract parameters
        query = tool_parameters.get("query")
        max_results = tool_parameters.get("max_results", 100)
        
        if not query:
            yield self.create_text_message("Error: No SQL query provided")
            return
        
        try:
            # Extract credentials from runtime
            project_id = self.runtime.credentials.get("project_id")
            service_account_key_json = self.runtime.credentials.get("service_account_key")
            
            # Parse service account key
            service_account_info = json.loads(service_account_key_json)
            
            # Create credentials
            credentials_obj = service_account.Credentials.from_service_account_info(
                service_account_info
            )
            
            # Initialize BigQuery client
            client = bigquery.Client(
                project=project_id,
                credentials=credentials_obj
            )
            
            # Perform cost estimation (dry run)
            logger.info(f"Estimating cost for query: {query}")
            cost_estimation = self._estimate_query_cost(client, query)
            
            # Log the query and estimation
            logger.info(
                f"Query cost estimate: {cost_estimation['bytes_processed']} bytes "
                f"(~${cost_estimation['estimated_cost_usd']:.2f})"
            )
            
            # Check if query exceeds byte limit
            if cost_estimation["exceeds_limit"]:
                error_message = (
                    f"Query would process {cost_estimation['bytes_processed']} bytes, "
                    f"which exceeds the maximum limit of {MAX_BYTES_PROCESSED} bytes (5 GB). "
                    f"Please refine your query to process less data."
                )
                self._log_query(query, cost_estimation, False, error_message)
                yield self.create_text_message(error_message)
                return
            
            # Warn about expensive queries
            if cost_estimation["estimated_cost_warning"]:
                warning_message = (
                    f"⚠️ This query is estimated to process {cost_estimation['bytes_processed']} bytes "
                    f"(~${cost_estimation['estimated_cost_usd']:.2f}), which is relatively expensive. "
                    f"Consider refining your query to process less data."
                )
                yield self.create_text_message(warning_message)
            
            # Execute query
            logger.info(f"Executing BigQuery query: {query}")
            query_job = client.query(query)
            
            # Get results
            results = query_job.result(max_results=max_results)
            
            # Convert to list of dictionaries
            rows = []
            for row in results:
                # Convert row to dict
                row_dict = dict(row.items())
                
                # Handle non-serializable types
                for key, value in row_dict.items():
                    if not self._is_json_serializable(value):
                        row_dict[key] = str(value)
                        
                rows.append(row_dict)
            
            # Add metadata
            metadata = {
                "total_rows": results.total_rows,
                "schema": [field.name for field in results.schema],
                "query_job_id": query_job.job_id,
                "bytes_processed": query_job.total_bytes_processed,
                "estimated_cost_usd": cost_estimation["estimated_cost_usd"]
            }
            
            response = {
                "results": rows,
                "metadata": metadata
            }
            
            # Log successful query
            self._log_query(query, cost_estimation, True)
            
            # Return results
            yield self.create_json_message(response)
            
        except BadRequest as e:
            error_message = f"BigQuery syntax error: {str(e)}"
            logger.exception(error_message)
            
            # Create a cost estimation object with zeros for logging
            empty_estimation = {
                "bytes_processed": 0,
                "estimated_cost_usd": 0,
                "exceeds_limit": False,
                "estimated_cost_warning": False
            }
            self._log_query(query, empty_estimation, False, error_message)
            
            yield self.create_text_message(error_message)
            
        except Exception as e:
            error_message = f"Error executing query: {str(e)}"
            logger.exception(f"Error executing BigQuery query: {e}")
            
            # Create a cost estimation object with zeros for logging
            empty_estimation = {
                "bytes_processed": 0,
                "estimated_cost_usd": 0,
                "exceeds_limit": False,
                "estimated_cost_warning": False
            }
            self._log_query(query, empty_estimation, False, error_message)
            
            yield self.create_text_message(error_message)
    
    def _is_json_serializable(self, value: Any) -> bool:
        """Check if a value is JSON serializable."""
        try:
            json.dumps(value)
            return True
        except (TypeError, OverflowError):
            return False 