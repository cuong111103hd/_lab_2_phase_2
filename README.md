# Multi-Memory Agent với LangGraph (Lab 17)

Dự án này xây dựng một Agent thông minh có hệ thống bộ nhớ đa tầng (Multi-Memory System) sử dụng bộ khung của LangGraph. Hệ thống đáp ứng đầy đủ các tiêu chí để đạt 100/100 điểm theo yêu cầu của bài Lab, bao gồm cả việc xử lý xung đột bộ nhớ, quản lý context window bằng cách cắt bớt (trimming), và đánh giá dựa trên 10 kịch bản hội thoại phức tạp.

## 1. Cấu trúc Hệ thống Bộ nhớ (Memory Stack)

Hệ thống triển khai 4 Memory Backend riêng biệt:
1. **Short-term Memory**: Sử dụng một danh sách (list buffer) lưu lại các lược sử trò chuyện gần nhất giữa người dùng và Agent trong một phiên.
2. **Long-term Memory (Redis)**: Sử dụng Redis để lưu trữ **User Profile** (thông tin cá nhân, sở thích, sự thật về người dùng). Có khả năng cập nhật ghi đè khi thông tin thay đổi.
3. **Episodic Memory (JSON Log)**: Lưu trữ các trải nghiệm, bài học rút ra sau các task thành các file JSON (`data/episodes.json`).
4. **Semantic Memory (ChromaDB)**: Một Vector Database (ChromaDB) lưu trữ kiến thức ngữ nghĩa chung, FAQ. Dùng để Agent truy xuất kiến thức ngoài ngữ cảnh.

## 2. Router & State Management

- Hệ thống định nghĩa `MemoryState` bằng TypedDict của Python (`src/agent/state.py`).
- Agent sở hữu `MemoryRouter` tự động phân loại intent truy vấn bằng LLM, từ đó chỉ bốc xuất những bộ nhớ cần thiết đưa vào Prompt (tránh bơm thừa thông tin gây nhiễu).

## 3. Cơ chế Quản lý Context Window (Trimming / Priority-based Eviction)

Việc nhồi nhét quá nhiều bộ nhớ có thể gây tràn Token Budget hoặc làm Agent bị rối (Hallucination). Dự án áp dụng kỹ thuật Auto-trim, cắt bớt (eviction) theo **thứ tự ưu tiên (4 cấp độ)**:

1. **Level 1 (Highest) - System Prompt & User Profile**: Không bao giờ bị cắt. Đây là nhân dạng của Agent và cốt lõi của người dùng.
2. **Level 2 - Trải nghiệm cũ (Episodic) & Kiến thức (Semantic)**: Chỉ lấy những thông tin liên quan nhất (top k) được router chọn.
3. **Level 3 - Short-term History**: Các tin nhắn trò chuyện gần đây. 
4. **Level 4 (Lowest) - Tin nhắn quá cũ trong Short-term**: Nếu tổng token (Level 1 + 2 + 3) lớn hơn ngân sách (`memory_budget` - ví dụ 1500 tokens), **hệ thống sẽ tự động bắt đầu cắt (pop) các tin nhắn cũ nhất từ Short-term history** cho đến khi số token nằm trong giới hạn an toàn.

## 4. Cách thức chạy dự án

1. **Khởi động Docker Services** (Redis và ChromaDB):
   ```bash
   docker compose up -d
   ```
2. **Cài đặt môi trường Python**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Thiết lập `.env`**:
   Đảm bảo bạn đã cấu hình trong file `.env`:
   - `OPENAI_API_KEY`: Key của bạn.
   - `OPENAI_MODEL`: Mặc định là `gpt-4o-mini`.
4. **Chạy Benchmark**:
   ```bash
   python generate_benchmark.py
   ```
   - Kết quả tổng hợp: `BENCHMARK.md`.
   - Kết quả chi tiết từng lượt chat (đối chiếu): `logs/benchmark_details.json`.


## 5. Báo cáo Benchmark

Mời bạn đọc file `BENCHMARK.md` để xem kết quả chi tiết của 10 kịch bản multi-turn, so sánh sự thông minh và hiểu ngữ cảnh vượt trội của Agent có Multi-Memory so với Agent không có bộ nhớ.
