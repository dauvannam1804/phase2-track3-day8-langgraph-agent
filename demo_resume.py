import os
import json
from langgraph_agent_lab.graph import build_graph
from langgraph_agent_lab.persistence import build_checkpointer
from langgraph_agent_lab.state import AgentState, Scenario, Route, initial_state

def load_all_scenarios(file_path):
    scenarios = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                scenarios.append(Scenario(**data))
    return scenarios

def run_demo():
    # 1. Load scenarios
    scenarios_file = "data/sample/scenarios.jsonl"
    all_scenarios = load_all_scenarios(scenarios_file)
    
    print("--- CHỌN KỊCH BẢN DEMO ---")
    for i, s in enumerate(all_scenarios):
        print(f"{i+1}. [{s.id}] {s.query[:50]}...")
    
    try:
        choice = int(input("\nNhập số thứ tự kịch bản bạn muốn chọn: ")) - 1
        selected_scenario = all_scenarios[choice]
    except (ValueError, IndexError):
        print("Lựa chọn không hợp lệ, sử dụng kịch bản đầu tiên.")
        selected_scenario = all_scenarios[0]

    # 2. Khởi tạo Graph với bộ lưu trữ SQLite để hỗ trợ Crash Recovery
    checkpointer = build_checkpointer("sqlite", "checkpoints.db")
    graph = build_graph(checkpointer=checkpointer)
    
    state = initial_state(selected_scenario)
    thread_config = {"configurable": {"thread_id": f"thread-{selected_scenario.id}"}}
    
    # Bật chế độ ngắt thực tế nếu kịch bản yêu cầu duyệt
    os.environ["LANGGRAPH_INTERRUPT"] = "true"
    
    print(f"\n--- BẮT ĐẦU CHẠY: {selected_scenario.id} ---")
    print(f"Query: {selected_scenario.query}")
    
    # 3. Chạy luồng
    try:
        print("\n[Bước 1] Agent đang xử lý...")
        # Sử dụng stream để theo dõi các node
        for event in graph.stream(state, thread_config, stream_mode="values"):
            node_route = event.get("route")
            if node_route:
                print(f" -> Đang xử lý tại luồng: {node_route}")
            
            # Kiểm tra nếu đã có kết quả cuối cùng mà không cần duyệt
            if event.get("final_answer") and not selected_scenario.requires_approval:
                print(f"\n[KẾT QUẢ]: {event.get('final_answer')}")
                return

    except Exception as e:
        # Kiểm tra xem có phải là Interrupt không
        if "interrupt" in str(e).lower() or "checkpoint" in str(e).lower():
             print(f"\n[DỪNG] Agent đã tạm dừng tại node 'approval' để chờ phê duyệt (HITL).")
        else:
             print(f"\n[LỖI] Đã xảy ra lỗi ngoài dự kiến: {e}")
             return

    # 4. Xử lý Resume nếu là kịch bản Risky
    if selected_scenario.requires_approval:
        print(f"\n[CHỜ DUYỆT] Hành động: {selected_scenario.query}")
        confirm = input("Bạn có đồng ý phê duyệt hành động này không? (y/n): ")
        
        is_approved = confirm.lower() == 'y'
        graph.update_state(thread_config, {"approval": {"approved": is_approved, "comment": "Duyệt qua Demo CLI"}})
        
        print("\n[Bước 2] Đang Resume agent...")
        for event in graph.stream(None, thread_config, stream_mode="values"):
            if event.get("final_answer"):
                print(f"\n[KẾT QUẢ SAU KHI DUYỆT]: {event.get('final_answer')}")

if __name__ == "__main__":
    run_demo()
