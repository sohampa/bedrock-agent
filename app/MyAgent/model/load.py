from strands.models.bedrock import BedrockModel


def load_model() -> BedrockModel:
    """Get Bedrock model client using IAM credentials (Amazon Nova)."""
    return BedrockModel(model_id="amazon.nova-pro-v1:0")
