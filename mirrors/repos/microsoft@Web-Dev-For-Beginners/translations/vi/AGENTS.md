# AGENTS.md

## Giới Thiệu Dự Án

Đây là kho tài liệu giáo dục dành cho việc giảng dạy các kiến thức cơ bản về phát triển web cho người mới bắt đầu. Chương trình học là một khóa học toàn diện kéo dài 12 tuần được phát triển bởi Microsoft Cloud Advocates, bao gồm 24 bài học thực hành về JavaScript, CSS và HTML.

### Thành Phần Chính

- **Nội dung giáo dục**: 24 bài học có cấu trúc, tổ chức thành các mô-đun dự án
- **Dự án thực hành**: Terrarium, Trò chơi gõ chữ, Tiện ích mở rộng trình duyệt, Trò chơi không gian, Ứng dụng ngân hàng, Trình soạn thảo mã, và Trợ lý trò chuyện AI
- **Bài kiểm tra tương tác**: 48 bài kiểm tra với 3 câu hỏi mỗi bài (đánh giá trước/sau bài học)
- **Hỗ trợ đa ngôn ngữ**: Dịch tự động sang hơn 50 ngôn ngữ qua GitHub Actions
- **Công nghệ**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (cho các dự án AI)

### Kiến Trúc

- Kho tài liệu giáo dục theo cấu trúc dựa trên bài học
- Mỗi thư mục bài học chứa README, ví dụ mã và giải pháp
- Các dự án độc lập trong các thư mục riêng (quiz-app, các dự án bài học khác)
- Hệ thống dịch thuật sử dụng GitHub Actions (co-op-translator)
- Tài liệu được phục vụ qua Docsify và có sẵn dưới dạng PDF

## Các Lệnh Thiết Lập

Kho này chủ yếu dùng để truy cập nội dung giáo dục. Để làm việc với các dự án cụ thể:

### Thiết Lập Kho Chính

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Thiết Lập Ứng Dụng Quiz (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Khởi động máy chủ phát triển
npm run build      # Xây dựng cho sản xuất
npm run lint       # Chạy ESLint
```

### API Dự Án Ngân Hàng (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Khởi động máy chủ API
npm run lint       # Chạy ESLint
npm run format     # Định dạng với Prettier
```

### Các Dự Án Tiện Ích Mở Rộng Trình Duyệt

```bash
cd 5-browser-extension/solution
npm install
# Làm theo hướng dẫn tải tiện ích mở rộng theo trình duyệt cụ thể
```

### Các Dự Án Trò Chơi Không Gian

```bash
cd 6-space-game/solution
npm install
# Mở index.html trong trình duyệt hoặc sử dụng Live Server
```

### Dự Án Trò Chuyện (Backend Python)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Đặt biến môi trường GITHUB_TOKEN
python api.py
```

## Quy Trình Phát Triển

### Dành Cho Người Đóng Góp Nội Dung

1. **Fork kho** về tài khoản GitHub của bạn
2. **Clone bản fork** về máy cục bộ
3. **Tạo nhánh mới** để thực hiện thay đổi
4. Thay đổi nội dung bài học hoặc ví dụ mã
5. Kiểm thử các thay đổi mã trong thư mục dự án liên quan
6. Gửi pull request theo hướng dẫn đóng góp

### Dành Cho Người Học

1. Fork hoặc clone kho về
2. Di chuyển tuần tự đến các thư mục bài học
3. Đọc các file README cho mỗi bài học
4. Hoàn thành bài kiểm tra trước bài học tại https://ff-quizzes.netlify.app/web/
5. Làm các ví dụ mã trong thư mục bài học
6. Hoàn thành các bài tập và thử thách
7. Tham gia bài kiểm tra sau bài học

### Phát Triển Trực Tiếp

- **Tài liệu**: Chạy `docsify serve` ở thư mục gốc (cổng 3000)
- **Ứng dụng Quiz**: Chạy `npm run dev` trong thư mục quiz-app
- **Dự án**: Dùng tiện ích VS Code Live Server cho các dự án HTML
- **Dự án API**: Chạy `npm start` trong các thư mục API tương ứng

## Hướng Dẫn Kiểm Thử

### Kiểm Thử Ứng Dụng Quiz

```bash
cd quiz-app
npm run lint       # Kiểm tra các vấn đề về phong cách mã
npm run build      # Xác minh xây dựng thành công
```

### Kiểm Thử API Ngân Hàng

```bash
cd 7-bank-project/api
npm run lint       # Kiểm tra các vấn đề về phong cách mã
node server.js     # Xác minh máy chủ khởi động không có lỗi
```

### Phương Pháp Kiểm Thử Chung

- Kho giáo dục này không có các bài kiểm thử tự động đầy đủ
- Kiểm thử thủ công tập trung vào:
  - Ví dụ mã chạy không lỗi
  - Các liên kết trong tài liệu hoạt động chính xác
  - Các dự án build thành công
  - Ví dụ theo đúng thực tiễn tốt nhất

### Kiểm Tra Trước Khi Gửi

- Chạy `npm run lint` trong các thư mục có package.json
- Xác minh các liên kết markdown hợp lệ
- Kiểm thử các ví dụ mã trong trình duyệt hoặc Node.js
- Kiểm tra dịch thuật duy trì cấu trúc chính xác

## Hướng Dẫn Phong Cách Mã

### JavaScript

- Dùng cú pháp ES6+ hiện đại
- Tuân thủ cấu hình ESLint tiêu chuẩn trong các dự án
- Đặt tên biến và hàm rõ nghĩa, dễ hiểu cho học viên
- Thêm chú thích giải thích khái niệm cho người học
- Định dạng mã bằng Prettier nếu được cấu hình

### HTML/CSS

- Các thành phần HTML5 có ngữ nghĩa
- Nguyên tắc thiết kế đáp ứng (responsive)
- Quy ước đặt tên class rõ ràng
- Chú thích kỹ thuật CSS giải thích cho học viên

### Python

- Tuân thủ hướng dẫn phong cách PEP 8
- Ví dụ mã rõ ràng, phù hợp giáo dục
- Thêm chỉ dẫn kiểu (type hints) nếu giúp người học

### Tài Liệu Markdown

- Cấp độ tiêu đề rõ ràng
- Khối mã khai báo ngôn ngữ lập trình
- Liên kết nguồn tài liệu bổ sung
- Ảnh chụp màn hình và hình ảnh trong thư mục `images/`
- Văn bản thay thế (alt text) cho hình ảnh để tăng khả năng tiếp cận

### Tổ Chức Tệp

- Bài học đánh số tuần tự (1-getting-started-lessons, 2-js-basics, vv)
- Mỗi dự án có thư mục `solution/` và thường có thư mục `start/` hoặc `your-work/`
- Hình ảnh lưu trong thư mục `images/` riêng từng bài học
- Bản dịch trong cấu trúc `translations/{language-code}/`

## Xây Dựng và Triển Khai

### Triển Khai Ứng Dụng Quiz (Azure Static Web Apps)

Ứng dụng quiz đã được cấu hình để triển khai với Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Tạo thư mục dist/
# Triển khai thông qua quy trình làm việc GitHub Actions khi đẩy lên nhánh main
```

Cấu hình Azure Static Web Apps:
- **Vị trí ứng dụng**: `/quiz-app`
- **Vị trí đầu ra**: `dist`
- **Quy trình làm việc**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Tạo PDF Tài Liệu

```bash
npm install                    # Cài đặt docsify-to-pdf
npm run convert               # Tạo PDF từ docs
```

### Tài Liệu Docsify

```bash
npm install -g docsify-cli    # Cài đặt Docsify toàn cục
docsify serve                 # Phục vụ trên localhost:3000
```

### Build Riêng Cho Dự Án

Mỗi thư mục dự án có thể có quy trình build riêng:
- Dự án Vue: chạy `npm run build` để tạo gói sản xuất
- Dự án tĩnh: không cần bước build, phục vụ file trực tiếp

## Hướng Dẫn Pull Request

### Định Dạng Tiêu Đề

Dùng tiêu đề rõ ràng, mô tả khu vực thay đổi:
- `[Quiz-app] Thêm bài kiểm tra mới cho bài học X`
- `[Lesson-3] Sửa lỗi chính tả trong dự án terrarium`
- `[Translation] Thêm bản dịch tiếng Tây Ban Nha cho bài học 5`
- `[Docs] Cập nhật hướng dẫn thiết lập`

### Kiểm Tra Bắt Buộc

Trước khi gửi PR:

1. **Chất lượng mã**:
   - Chạy `npm run lint` trong các thư mục dự án ảnh hưởng
   - Sửa tất cả lỗi và cảnh báo lint

2. **Xác minh build**:
   - Chạy `npm run build` nếu có
   - Đảm bảo không có lỗi build

3. **Kiểm tra liên kết**:
   - Thử tất cả các liên kết markdown
   - Xác nhận hình ảnh hiển thị đúng

4. **Kiểm duyệt nội dung**:
   - Đọc lại chính tả và ngữ pháp
   - Đảm bảo ví dụ mã chính xác và phù hợp học thuật
   - Xác nhận bản dịch giữ nguyên nghĩa

### Yêu Cầu Đóng Góp

- Đồng ý với Microsoft CLA (kiểm tra tự động khi PR đầu tiên)
- Tuân thủ [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Tham khảo [CONTRIBUTING.md](./CONTRIBUTING.md) để biết hướng dẫn chi tiết
- Tham chiếu số issue trong mô tả PR nếu có

### Quy Trình Đánh Giá

- PR được duyệt bởi người duy trì và cộng đồng
- Ưu tiên tính rõ ràng trong giáo dục
- Ví dụ mã tuân thủ thực tiễn tốt nhất hiện hành
- Kiểm tra độ chính xác và phù hợp văn hóa của bản dịch

## Hệ Thống Dịch Thuật

### Dịch Tự Động

- Dùng GitHub Actions với workflow co-op-translator
- Dịch tự động sang hơn 50 ngôn ngữ
- Tệp nguồn trong các thư mục chính
- Tệp được dịch lưu trong thư mục `translations/{language-code}/`

### Thêm Cải Tiến Dịch Thủ Công

1. Tìm tệp trong `translations/{language-code}/`
2. Cải tiến nội dung giữ nguyên cấu trúc
3. Đảm bảo các ví dụ mã hoạt động
4. Kiểm thử nội dung quiz đã dịch

### Siêu Dữ Liệu Dịch Thuật

Tệp dịch có bao gồm đầu mục metadata:
```markdown
<!--
CO_OP_TRANSLATOR_METADATA:
{
  "original_hash": "...",
  "translation_date": "...",
  "source_file": "...",
  "language_code": "..."
}
-->
```

## Gỡ Lỗi và Khắc Phục Sự Cố

### Vấn Đề Thường Gặp

**Ứng dụng quiz không khởi động**:
- Kiểm tra phiên bản Node.js (khuyến nghị v14+)
- Xóa thư mục `node_modules` và file `package-lock.json`, chạy lại `npm install`
- Kiểm tra xung đột cổng (mặc định Vite dùng cổng 5173)

**API server không khởi động**:
- Đảm bảo phiên bản Node.js >= 10
- Kiểm tra xem cổng có đang được sử dụng không
- Đảm bảo cài đặt tất cả phụ thuộc với `npm install`

**Tiện ích mở rộng trình duyệt không tải được**:
- Kiểm tra file manifest.json đúng định dạng
- Xem console trình duyệt để phát hiện lỗi
- Làm theo hướng dẫn cài đặt riêng của trình duyệt

**Vấn đề dự án chat Python**:
- Cài đặt gói OpenAI: `pip install openai`
- Xác nhận biến môi trường GITHUB_TOKEN đã được thiết lập
- Kiểm tra quyền truy cập Models GitHub

**Docsify không phục vụ tài liệu**:
- Cài docsify-cli toàn cục: `npm install -g docsify-cli`
- Chạy từ thư mục gốc của kho
- Kiểm tra file `docs/_sidebar.md` tồn tại

### Mẹo Phát Triển Môi Trường

- Dùng VS Code với tiện ích Live Server cho các dự án HTML
- Cài ESLint và Prettier để định dạng nhất quán
- Dùng DevTools trình duyệt để gỡ lỗi JavaScript
- Với dự án Vue, cài đặt tiện ích Vue DevTools cho trình duyệt

### Cân Nhắc Hiệu Suất

- Số lượng tệp dịch lớn (hơn 50 ngôn ngữ) làm cho clone đầy đủ nặng
- Dùng clone nông nếu chỉ làm việc nội dung: `git clone --depth 1`
- Loại trừ thư mục dịch khỏi tìm kiếm khi làm việc với nội dung tiếng Anh
- Quá trình build có thể chậm lần đầu (npm install, build Vite)

## Cân Nhắc Bảo Mật

### Biến Môi Trường

- Không được commit khóa API vào kho
- Dùng các file `.env` (đã có trong `.gitignore`)
- Ghi lại các biến môi trường cần thiết trong README dự án

### Dự Án Python

- Sử dụng môi trường ảo: `python -m venv venv`
- Giữ phụ thuộc luôn được cập nhật
- Token GitHub chỉ cần quyền tối thiểu cần thiết

### Quyền Truy Cập GitHub Models

- Cần Personal Access Tokens (PAT) cho GitHub Models
- Lưu tokens dưới dạng biến môi trường
- Không được commit tokens hoặc thông tin đăng nhập

## Ghi Chú Thêm

### Đối Tượng Hướng Đến

- Người mới bắt đầu hoàn toàn về phát triển web
- Học sinh và người tự học
- Giáo viên sử dụng chương trình trong lớp học
- Nội dung thiết kế để dễ tiếp cận và xây dựng kỹ năng dần dần

### Triết Lý Giáo Dục

- Học qua dự án
- Kiểm tra kiến thức thường xuyên (quiz)
- Thực hành viết mã trực tiếp
- Ví dụ ứng dụng thực tế
- Tập trung vào kiến thức nền tảng trước khi học framework

### Bảo Trì Kho

- Cộng đồng học viên và người đóng góp năng động
- Cập nhật thường xuyên các phụ thuộc và nội dung
- Người quản lý theo dõi các issue và thảo luận
- Cập nhật dịch tự động qua GitHub Actions

### Tài Nguyên Liên Quan

- [Microsoft Learn modules](https://docs.microsoft.com/learn/)
- [Student Hub resources](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) được khuyến nghị cho học viên
- Các khoá học bổ sung: AI tạo sinh, Khoa học dữ liệu, ML, IoT

### Làm Việc Với Các Dự Án Cụ Thể

Hướng dẫn chi tiết cho từng dự án xem trong các tệp README:
- `quiz-app/README.md` - Ứng dụng quiz Vue 3
- `7-bank-project/README.md` - Ứng dụng ngân hàng có xác thực
- `5-browser-extension/README.md` - Phát triển tiện ích mở rộng trình duyệt
- `6-space-game/README.md` - Phát triển trò chơi canvas
- `9-chat-project/README.md` - Dự án trợ lý chat AI

### Cấu Trúc Monorepo

Mặc dù không phải monorepo truyền thống, kho này chứa nhiều dự án độc lập:
- Mỗi bài học tự chứa
- Các dự án không chia sẻ phụ thuộc
- Làm việc riêng biệt từng dự án mà không ảnh hưởng lẫn nhau
- Clone toàn bộ kho để trải nghiệm đầy đủ chương trình học

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Tuyên bố từ chối trách nhiệm**:  
Tài liệu này đã được dịch bằng dịch vụ dịch thuật AI [Co-op Translator](https://github.com/Azure/co-op-translator). Mặc dù chúng tôi cố gắng đảm bảo độ chính xác, xin lưu ý rằng bản dịch tự động có thể chứa lỗi hoặc sai sót. Tài liệu gốc bằng ngôn ngữ bản địa nên được xem là nguồn thông tin chính thức. Đối với những thông tin quan trọng, nên sử dụng dịch vụ dịch thuật chuyên nghiệp do con người thực hiện. Chúng tôi không chịu trách nhiệm về bất kỳ sự hiểu lầm hay giải thích sai nào phát sinh từ việc sử dụng bản dịch này.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->