from app.config import Settings
from app.services.providers.base import ResearchProvider
from app.services.providers.mock import MockResearchProvider
from app.services.providers.real import RealResearchProvider


def create_provider(provider_name: str, settings: Settings) -> ResearchProvider:
    if provider_name == "real":
        return RealResearchProvider(settings)
    return MockResearchProvider()
