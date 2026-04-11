from app.config import Settings
from app.services.providers.base import ResearchProvider
from app.services.providers.extended_mock import ExtendedMockResearchProvider
from app.services.providers.extended_real import ExtendedRealResearchProvider


def create_provider(provider_name: str, settings: Settings) -> ResearchProvider:
    if provider_name == "real":
        return ExtendedRealResearchProvider(settings)
    return ExtendedMockResearchProvider()
