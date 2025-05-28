from dify_plugin import ToolProvider

class MinimalBigqueryProvider(ToolProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        pass # No validation for minimal test 