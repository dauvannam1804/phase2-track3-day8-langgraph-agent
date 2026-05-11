# Day 08 Hidden Lab Report

## 1. Team / student

- Name: Student
- Repo/commit: phase2-track3-day8-langgraph-agent
- Date: 2026-05-11

## 2. Architecture

![Graph Diagram](graph.png)

Kiến trúc thống nhất với lab chính, đảm bảo tính bền bỉ và khả năng mở rộng. Đồ thị sử dụng các node chức năng để tách biệt logic xử lý, từ việc tiếp nhận yêu cầu đến thực thi và phê duyệt rủi ro.

## 3. State schema

| Field | Reducer | Why |
|---|---|---|
| messages | add | Audit conversation/events |
| route | overwrite | Current route only |
| events | add | Detailed audit trail |
| errors | add | Error tracking |

## 4. Scenario results

| Scenario | Expected route | Actual route | Success | Retries | Interrupts |
|---|---|---|---:|---:|---:|
| G01_simple | simple | simple | true | 0 | 0 |
| G02_simple2 | simple | simple | true | 0 | 0 |
| G03_tool | tool | tool | true | 0 | 0 |
| G04_tool2 | tool | tool | true | 0 | 0 |
| G05_tool3 | tool | tool | true | 0 | 0 |
| G06_missing | missing_info | missing_info | true | 0 | 0 |
| G07_missing2 | missing_info | missing_info | true | 0 | 0 |
| G08_risky | risky | risky | true | 0 | 2 |
| G09_risky2 | risky | risky | true | 0 | 2 |
| G10_risky3 | risky | risky | true | 0 | 2 |
| G11_risky4 | risky | risky | true | 0 | 2 |
| G12_error | error | error | true | 2 | 0 |
| G13_error2 | error | error | true | 2 | 0 |
| G14_dead | error | error | true | 2 | 0 |
| G15_mixed | risky | risky | true | 0 | 2 |

## 5. Failure analysis

1. **Dead Letter Recovery**: Scenario `G14_dead` minh chứng khả năng xử lý các lỗi không thể phục hồi bằng cách chuyển trạng thái sang `dead_letter` một cách có kiểm soát.
2. **Human Approval Gate**: Toàn bộ kịch bản từ `G08` đến `G11` đều được kiểm soát chặt chẽ qua bước ngắt để chờ phê duyệt, ngăn chặn các hành động rủi ro tự phát.

## 6. Persistence / recovery evidence

Mọi trạng thái hội thoại đều được lưu trữ qua `MemorySaver`. Việc resume các thread sau khi có hành động `approval` được thực hiện mượt mà dựa trên lịch sử trạng thái đã lưu.

## 7. Extension work

Triển khai đầy đủ Visualization, Persistent Checkpointer (interface), và tích hợp hệ thống đánh giá tự động (Evaluation Loop).

## 8. Improvement plan

Tăng cường độ chính xác của bước `evaluate` để giảm bớt các trường hợp retry nhầm khi kết quả công cụ thực chất đã đạt yêu cầu.
