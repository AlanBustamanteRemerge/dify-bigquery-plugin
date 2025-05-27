# BigQuery Plugin Guide

## Overview

This plugin allows you to integrate Google BigQuery with Dify, enabling you to perform SQL queries on your BigQuery datasets directly from your Dify applications.

## Prerequisites

Before using this plugin, you need:

1. A Google Cloud Platform (GCP) account
2. A project in GCP with BigQuery API enabled
3. A service account with appropriate permissions for BigQuery
4. A service account key file (JSON)

## Configuration

After installing the plugin, you need to configure it with your Google Cloud credentials:

1. Navigate to the plugin settings in Dify
2. Enter your Google Cloud Project ID
3. Paste the contents of your service account key file (JSON format)
4. Save the configuration

## Usage

### Basic Query

You can use the BigQuery query tool to run SQL queries against your BigQuery datasets. For example:

```sql
SELECT * FROM `your-project.your_dataset.your_table` LIMIT 10
```

### Example Workflows

#### Example 1: Simple Data Retrieval

1. Add the BigQuery query tool to your workflow
2. Set the SQL query input parameter to retrieve specific data
3. Connect the output to a text generation node to analyze or format the results

#### Example 2: Analytical Reporting

1. Use multiple BigQuery query tools in sequence to gather different data points
2. Process and combine the results using other nodes in your workflow
3. Generate a comprehensive report based on the collected data

## Troubleshooting

### Common Issues

1. **Authentication Error**: Verify that your service account key is valid and has the necessary permissions.
2. **Query Timeout**: For complex queries, consider optimizing your SQL or increasing the timeout setting.
3. **Invalid SQL**: Ensure your SQL syntax is correct for BigQuery's SQL dialect.

### Support

If you encounter any issues or have questions, please:
1. Check the documentation
2. Contact support at [your-support-email@example.com] 