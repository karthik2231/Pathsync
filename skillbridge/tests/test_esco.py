import pytest
from unittest.mock import patch
from app.utils.esco import search_esco_skill, normalize_skills

@pytest.mark.asyncio
async def test_search_esco_skill_api_call():
    """Verify standard schema unpacking from raw ESCO requests"""
    with patch("app.utils.esco.fetch_esco_api") as mock_fetch:
        mock_fetch.return_value = {
            "_embedded": {
                "results": [{"uri": "http://esco/123", "title": "Mock Skill"}]
            }
        }
        res = await search_esco_skill("Mock")
        assert res["uri"] == "http://esco/123"
        assert res["preferredLabel"] == "Mock Skill"

@pytest.mark.asyncio
async def test_normalize_skills_deduplication():
    """Verify that redundant raw skill inputs map to singular ESCO node output efficiently"""
    with patch("app.utils.esco.search_esco_skill") as mock_search:
        # Simulate different queries mapping to same ultimate URI
        async def mock_search_func(name):
            if name in ["JS", "JavaScript"]:
                return {"uri": "http://esco/js", "preferredLabel": "JavaScript", "altLabels": []}
            return None
            
        mock_search.side_effect = mock_search_func
        
        normalized = await normalize_skills(["JS", "JavaScript", "UnknownSkill"])
        
        # JS and JavaScript should merge gracefully
        assert len(normalized) == 2
        
        uris = [n.esco_uri for n in normalized]
        names = [n.name for n in normalized]
        
        # Target structure asserts
        assert "http://esco/js" in uris
        assert None in uris
        assert "UnknownSkill" in names
