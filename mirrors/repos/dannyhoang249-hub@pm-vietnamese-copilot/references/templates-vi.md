# Mẫu PM — tiếng Việt là mặc định

Chỉ dùng các phần cần thiết để làm rõ quyết định hoặc bước thực thi kế tiếp. Mọi số liệu, insight và trích dẫn chưa được cung cấp phải được ghi là giả định hoặc câu hỏi cần xác minh.

## Discovery brief

```markdown
# [Tên vấn đề / cơ hội]

## Quyết định cần đưa ra
- Quyết định:
- Owner / thời điểm cần quyết định:

## Vấn đề và kết quả mong muốn
- Người dùng / phân khúc:
- Bối cảnh và nhu cầu (JTBD):
- Pain / tác động hiện tại:
- Outcome mong muốn:

## Bằng chứng hiện có
- Sự thật / dữ liệu:
- Phản hồi người dùng:
- Điều chưa biết / giả định:

## Cơ hội và lựa chọn
| Lựa chọn | Giá trị kỳ vọng | Rủi ro / đánh đổi | Bằng chứng cần có |
| --- | --- | --- | --- |

## Bước tiếp theo
- Giả định rủi ro nhất:
- Thử nghiệm / nghiên cứu nhỏ nhất:
- Tín hiệu ra quyết định:
- Chủ sở hữu / thời hạn:
```

## Lean PRD

```markdown
# PRD — [Tên tính năng]

## Bối cảnh và vấn đề
## Mục tiêu, chỉ số thành công và guardrail
## Không nằm trong phạm vi
## Người dùng và tình huống sử dụng
## Phạm vi phát hành / rollout
## Yêu cầu chức năng
## Yêu cầu phi chức năng / ràng buộc
## Analytics: events, properties, dashboard
## Rủi ro, phụ thuộc, câu hỏi mở
## Kế hoạch phát hành, hỗ trợ và học hỏi
```

## Backlog item

```markdown
### [Tên ngắn của hạng mục]
**User story:** Là [vai trò], tôi muốn [khả năng] để [giá trị].

**Giá trị / lý do:**

**Tiêu chí chấp nhận:**
1. Given [bối cảnh], When [hành động], Then [kết quả quan sát được].
2. ...

**Trạng thái biên:** loading, empty, error, permission, mobile/accessibility (nếu áp dụng).
**Theo dõi:** [event/properties] (nếu áp dụng).
**Phụ thuộc / câu hỏi mở:**
```

## Decision memo / ưu tiên

```markdown
# Quyết định ưu tiên — [Mục tiêu]

## Bối cảnh và ràng buộc
## Tiêu chí đánh giá và mức độ tin cậy
## So sánh lựa chọn
| Lựa chọn | Reach | Impact | Confidence | Effort | Điểm / nhận định | Ghi chú |
| --- | ---: | ---: | ---: | ---: | --- | --- |

## Khuyến nghị
## Đánh đổi và rủi ro
## Bước xác thực hoặc thực thi tiếp theo
```

## Measurement plan

```markdown
# Kế hoạch đo lường — [Sản phẩm / tính năng]

## Outcome cần tạo ra
## North Star metric
## Input metrics và guardrails
| Metric | Công thức | Event / nguồn | Segment | Baseline | Target | Owner | Cadence |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Tracking plan
| Event | Khi ghi nhận | Properties bắt buộc | Mục đích |
| --- | --- | --- | --- |

## Quy tắc ra quyết định
## Rủi ro về dữ liệu / việc cần xác minh
```

## Feedback synthesis

```markdown
# Tổng hợp phản hồi — [Nguồn / khoảng thời gian]

## Phạm vi và giới hạn dữ liệu
## Chủ đề nổi bật
| Chủ đề | Tín hiệu / bằng chứng | Phân khúc bị ảnh hưởng | Mức độ nghiêm trọng | Độ tin cậy |
| --- | --- | --- | --- | --- |

## Insight và cơ hội
## Điều không thể kết luận từ dữ liệu này
## Khuyến nghị và bước xác minh tiếp theo
```

## Decision record / meeting summary

```markdown
# [Tên cuộc họp / quyết định] — [dd/mm/yyyy]

## Bối cảnh
## Quyết định đã chốt
## Việc cần làm
| Việc | Người phụ trách | Hạn | Trạng thái |
| --- | --- | --- | --- |

## Rủi ro / phụ thuộc
## Câu hỏi chưa giải quyết
```
