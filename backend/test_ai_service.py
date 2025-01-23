
# test_ai_service.py
import pytest
from ai_services import AIService
from config import get_settings

@pytest.fixture
def ai_service():
    settings = get_settings()
    return AIService(settings.GEMINI_API_KEY)

async def test_analyze_content(ai_service):
    text = "Simple test content for analysis"
    analysis = await ai_service.analyze_content(text)
    assert "complexity" in analysis
    assert "key_concepts" in analysis
    assert "prerequisites" in analysis

async def test_generate_embeddings(ai_service):
    text = "Test content for embeddings"
    embeddings = await ai_service.generate_embeddings(text)
    assert len(embeddings) > 0
    assert all(isinstance(x, float) for x in embeddings)