import os

from strands.models.bedrock import BedrockModel

# Nova v1 models support on-demand Converse. Nova 2.x requires an inference profile ARN.
DEFAULT_MODEL_ID = "amazon.nova-lite-v1:0"


def load_model() -> BedrockModel:
    """Get Bedrock model client using IAM credentials."""
    model_id = os.environ.get("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)
    return BedrockModel(model_id=model_id)
