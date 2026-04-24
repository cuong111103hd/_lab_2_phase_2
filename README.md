# Lab #17: Build Multi-Memory Agent với LangGraph

Dự án này triển khai một AI Agent có khả năng quản lý bộ nhớ đa tầng (Multi-Memory Stack) sử dụng framework LangGraph. Hệ thống được thiết kế để cá nhân hóa phản hồi dựa trên lịch sử hội thoại, sở thích và kinh nghiệm của người dùng.

## 🎓 Thông tin sinh viên
- **Họ và tên:** Đậu Văn Nam
- **MSSV:** 2A202600033
- **Khóa học:** Track 3 - Advanced Agentic Coding

## 🚀 Tính năng chính
- **Short-term Memory:** Quản lý context hội thoại tức thời qua buffer list.
- **Long-term Profile (Redis):** Lưu trữ thông tin cá nhân bền vững (Sở thích, dị ứng, kỹ năng) với cơ chế tự động xử lý mâu thuẫn (Conflict Handling).
- **Episodic Memory (JSON):** Lưu trữ các sự kiện quan trọng và kinh nghiệm quá khứ để Agent rút kinh nghiệm.
- **Semantic Memory (ChromaDB):** Tìm kiếm ngữ nghĩa dựa trên Vector Embeddings (OpenAI API) để truy xuất các đoạn kiến thức liên quan.
- **Memory Router:** Tự động quyết định loại bộ nhớ cần truy xuất dựa trên ý định (intent) của người dùng.
- **Auto-trimming:** Cơ chế cắt bớt context theo thứ tự ưu tiên.

## 🛠 Hướng dẫn cài đặt & Chạy
### 1. Khởi tạo môi trường
```bash
# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 2. Chạy hạ tầng (Docker)
```bash
docker compose up -d
```

### 3. Cấu hình biến môi trường
Tạo file `.env` (xem `.env.example`) và điền `OPENAI_API_KEY` của bạn:
```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
REDIS_URL=redis://localhost:6379/0
CHROMA_URL=http://localhost:8000
```

### 4. Chạy ứng dụng
- **Chạy Demo tương tác:** `python main.py`
- **Chạy Benchmark:** `python generate_benchmark.py`

## 📊 Hệ thống Benchmark
Sau khi chạy `generate_benchmark.py`, hệ thống sẽ xuất ra 2 tệp quan trọng:
1. **`BENCHMARK.md`**: Bảng so sánh hiệu quả giữa Agent có Memory và No-Memory trên 10 kịch bản hội thoại đa tầng (multi-turn). Bao gồm phần phân tích rủi ro bảo mật và giới hạn kỹ thuật.
2. **`logs/benchmark_details.json`**: Nhật ký chi tiết từng lượt hội thoại, bao gồm cả dữ liệu bộ nhớ được truy xuất để đối chiếu kết quả.
