# PM templates | Mẫu PM — Vietnamese-English

Use the output language policy in `SKILL.md`. For bilingual deliverables, use bilingual headings and keep facts, assumptions, labels, event names, and owners consistent across languages.

## Discovery brief | Tóm tắt khám phá

```markdown
# [Problem / opportunity] | [Vấn đề / cơ hội]

## Decision needed | Quyết định cần đưa ra
- Decision / Quyết định:
- Owner and decision date / Người phụ trách và thời điểm quyết định:

## Problem and desired outcome | Vấn đề và kết quả mong muốn
- Target user / user segment | Người dùng / phân khúc:
- Context and JTBD | Bối cảnh và nhu cầu (JTBD):
- Current pain and impact | Pain và tác động hiện tại:
- Desired outcome | Outcome mong muốn:

## Available evidence | Bằng chứng hiện có
- Facts and data | Sự thật / dữ liệu:
- User feedback | Phản hồi người dùng:
- Unknowns and assumptions | Điều chưa biết / giả định:

## Options | Các lựa chọn
| Option / Lựa chọn | Expected value / Giá trị kỳ vọng | Risk or trade-off / Rủi ro hoặc đánh đổi | Evidence needed / Bằng chứng cần có |
| --- | --- | --- | --- |

## Next step | Bước tiếp theo
- Riskiest assumption / Giả định rủi ro nhất:
- Smallest research or experiment / Thử nghiệm hoặc nghiên cứu nhỏ nhất:
- Decision signal / Tín hiệu ra quyết định:
- Owner and due date / Người phụ trách và hạn:
```

## Lean PRD | PRD tinh gọn

```markdown
# PRD — [Feature name] | [Tên tính năng]

## Context and problem | Bối cảnh và vấn đề
## Goal, success metrics, and guardrails | Mục tiêu, chỉ số thành công và guardrail
## Out of scope | Không nằm trong phạm vi
## Users and use cases | Người dùng và tình huống sử dụng
## Release scope and rollout | Phạm vi phát hành và rollout
## Functional requirements | Yêu cầu chức năng
## Non-functional requirements and constraints | Yêu cầu phi chức năng và ràng buộc
## Analytics: events, properties, dashboard | Phân tích: events, properties, dashboard
## Risks, dependencies, and open questions | Rủi ro, phụ thuộc và câu hỏi mở
## Launch, support, and learning plan | Kế hoạch phát hành, hỗ trợ và học hỏi
```

## Backlog item | Hạng mục backlog

```markdown
### [Short item name] | [Tên ngắn]
**User story | User story:** As a [role], I want [capability] so that [value].
**Tiếng Việt:** Là [vai trò], tôi muốn [khả năng] để [giá trị].

**Value / rationale | Giá trị / lý do:**

**Acceptance criteria | Tiêu chí chấp nhận:**
1. Given [context], When [action], Then [observable result].
2. Với [bối cảnh], Khi [hành động], Thì [kết quả quan sát được].

**Edge states | Trạng thái biên:** loading, empty, error, permission, mobile/accessibility (when applicable / nếu áp dụng).
**Tracking | Theo dõi:** [event/properties] (when applicable / nếu áp dụng).
**Dependencies and open questions | Phụ thuộc và câu hỏi mở:**
```

## Prioritization memo | Ghi chú quyết định ưu tiên

```markdown
# Prioritization decision — [Goal] | Quyết định ưu tiên — [Mục tiêu]

## Context and constraints | Bối cảnh và ràng buộc
## Criteria and confidence | Tiêu chí và mức độ tin cậy
## Option comparison | So sánh lựa chọn
| Option / Lựa chọn | Reach | Impact | Confidence | Effort | Score or rationale / Điểm hoặc nhận định | Notes / Ghi chú |
| --- | ---: | ---: | ---: | ---: | --- | --- |

## Recommendation | Khuyến nghị
## Trade-offs and risks | Đánh đổi và rủi ro
## Next validation or delivery step | Bước xác thực hoặc thực thi tiếp theo
```

## Measurement plan | Kế hoạch đo lường

```markdown
# Measurement plan — [Product / feature] | Kế hoạch đo lường — [Sản phẩm / tính năng]

## Intended outcome | Outcome cần tạo ra
## North Star metric | Chỉ số North Star
## Input metrics and guardrails | Input metrics và guardrails
| Metric | Formula / Công thức | Event or source / Event hoặc nguồn | Segment / Phân khúc | Baseline | Target | Owner | Cadence |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Tracking plan | Kế hoạch tracking
| Event | When it fires / Khi ghi nhận | Required properties / Properties bắt buộc | Purpose / Mục đích |
| --- | --- | --- | --- |

## Decision rule | Quy tắc ra quyết định
## Data risks and validation needed | Rủi ro dữ liệu và việc cần xác minh
```

## Feedback synthesis | Tổng hợp phản hồi

```markdown
# Feedback synthesis — [Source / period] | Tổng hợp phản hồi — [Nguồn / khoảng thời gian]

## Scope and data limitations | Phạm vi và giới hạn dữ liệu
## Key themes | Chủ đề nổi bật
| Theme / Chủ đề | Signal or evidence / Tín hiệu hoặc bằng chứng | Affected segment / Phân khúc bị ảnh hưởng | Severity / Mức độ nghiêm trọng | Confidence / Độ tin cậy |
| --- | --- | --- | --- | --- |

## Insights and opportunities | Insight và cơ hội
## What the data cannot conclude | Điều dữ liệu chưa thể kết luận
## Recommendation and next validation step | Khuyến nghị và bước xác minh tiếp theo
```

## Decision record | Biên bản quyết định

```markdown
# [Meeting / decision name] — [dd/mm/yyyy] | [Tên cuộc họp / quyết định] — [dd/mm/yyyy]

## Context | Bối cảnh
## Decisions made | Quyết định đã chốt
## Action items | Việc cần làm
| Action / Việc | Owner / Người phụ trách | Due date / Hạn | Status / Trạng thái |
| --- | --- | --- | --- |

## Risks and dependencies | Rủi ro và phụ thuộc
## Open questions | Câu hỏi chưa giải quyết
```
