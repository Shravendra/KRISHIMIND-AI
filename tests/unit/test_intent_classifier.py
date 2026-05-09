from apps.chatbot_orchestrator.router.intent_classifier import classify_intent

def test_detect_crop_disease_with_leaf_keywords():
    d = classify_intent("My tomato leaves have yellow spots", has_images=True)
    assert d.intent == "crop_disease"
    assert "image_analysis" in d.agents_to_call
