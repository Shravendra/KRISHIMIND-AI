from rag.pipelines.rag_pipeline import rag_answer

def test_rag_answer_returns_shape():
    result = rag_answer("What is blight?")
    assert "answer" in result
    assert "confidence" in result
