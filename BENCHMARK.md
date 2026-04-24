# Benchmark Report: Multi-Memory Agent vs No-Memory Agent

| # | Scenario | No-memory result | With-memory result | Pass? |
|---|----------|------------------|---------------------|-------|
| 1 | Recall user name after 6 turns | I don’t have the ability to remember personal information or... | Yes, your name is Linh! How can I assist you today?... | **Pass** |
| 2 | Allergy conflict update | I'm not a doctor, but I can suggest some common steps to hel... | You are allergic to soy. If there’s anything else you’d like... | **Pass** |
| 3 | Recall previous debug lesson (Episodic) | To help you effectively, I need a bit more context about the... | The solution to the connection refused issue you faced was t... | **Pass** |
| 4 | Retrieve FAQ chunk (Semantic) | It seems like you're referring to a specific lab or experime... | The four types of memory required for Lab 17 are Short-term,... | **Pass** |
| 5 | Profile update - Favorite language | I don't have access to personal data about you unless you've... | Your favorite programming language is Python. If you have mo... | **Pass** |
| 6 | Trim/Token budget test | I am an AI language model created by OpenAI, designed to ass... | I am an AI assistant designed to help you with a variety of ... | **Pass** |
| 7 | Episodic - Project details | I'm sorry, but I don't have access to your previous interact... | You set up a Redis database successfully. If you have any sp... | **Pass** |
| 8 | Semantic - Redis Docker | The Docker service name for Redis is typically just `redis`.... | The docker service name for Redis is 'redis'.... | **Pass** |
| 9 | Multi-turn context (Short-term) | I'm sorry, but I don't have access to personal information a... | You have two dogs: one black and one white. If you'd like to... | **Pass** |
| 10 | Complex identity update | I'm sorry, but I don't have access to personal information a... | Your current job title is AI Architect. If you have any othe... | **Pass** |

## Reflection & Limitations
1. **Privacy/PII Risk:** Bộ nhớ Profile (Redis) có rủi ro lớn nhất vì lưu trữ thông tin cá nhân (tên, sở thích, bệnh lý/dị ứng). Nếu truy xuất sai, AI có thể rò rỉ thông tin cho phiên làm việc khác hoặc đưa ra lời khuyên nguy hiểm.
2. **Deletion & Consent:** Khi User yêu cầu xóa, ta phải xóa ở Profile (Redis), Episodic logs (JSON) và có thể là Conversation buffer. Hiện tại hệ thống hỗ trợ ghi đè (conflict handling) nhưng chưa có cơ chế TLL (Time-To-Live) tự động.
3. **Limitation:** Vector search (ChromaDB) có thể mang lại context không liên quan (Hallucination retrieval) nếu CSDL quá lớn và chunking không tốt. Ngoài ra, việc dùng LLM để trích xuất Intent & Profile facts sau mỗi lượt chat làm tăng đáng kể token usage & latency.
