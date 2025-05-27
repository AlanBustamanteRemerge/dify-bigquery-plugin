# BigQuery Plugin for Dify

This plugin enables integration between Dify and Google BigQuery, allowing you to run SQL queries against your BigQuery datasets directly from your Dify applications.

## Features

- Execute SQL queries against Google BigQuery datasets
- Return results as structured data for use in your workflows
- Support for query parameters and configuration options
- Secure credential management

## Installation

### Via GitHub

1. Go to the Dify plugin management page
2. Click "Install Plugin" and select "GitHub"
3. Enter the repository URL: `https://github.com/AlanBustamanteRemerge/bigqueryPluginDify`
4. Select the version and follow the installation instructions

### Via Local Upload

1. Download the latest release of the plugin
2. Go to the Dify plugin management page
3. Click "Install Plugin" and select "Local File"
4. Upload the `.difypkg` file

## Configuration

After installation, you need to configure the plugin with your Google Cloud credentials:

1. Project ID - Your Google Cloud project ID
2. Service Account Key - JSON format service account key with BigQuery permissions

## Usage

See the [User Guide](GUIDE.md) for detailed usage instructions and examples.

## Privacy

This plugin handles sensitive data. Please review our [Privacy Policy](PRIVACY.md) for details on how your data is handled.

## License

This plugin is released under the MIT License. See [LICENSE](LICENSE) for details. 