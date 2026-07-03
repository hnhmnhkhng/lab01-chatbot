# Chatbot

Chatbot web dùng Anthropic API, lưu lịch sử hội thoại vào MongoDB, hỗ trợ nhiều cuộc hội thoại.

## Cài đặt

1. Cài MongoDB local (nếu chưa có): https://www.mongodb.com/try/download/community, sau đó chạy `mongod` để MongoDB server hoạt động.

2. Cài Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Điền API key vào file `.env`:
   ```
   ANTHROPIC_API_KEY=your_real_key_here
   MONGO_URI=mongodb://localhost:27017
   ```

## Chạy

```
python app.py
```

Mở trình duyệt tại http://localhost:5000
