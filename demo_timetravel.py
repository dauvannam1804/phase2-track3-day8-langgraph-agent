import os
import json
from langgraph_agent_lab.graph import build_graph
from langgraph_agent_lab.persistence import build_checkpointer
from langgraph_agent_lab.state import Scenario, initial_state

def load_all_scenarios(file_path):
    scenarios = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                scenarios.append(Scenario(**data))
    return scenarios

def run_timetravel_demo():
    # 1. Khởi tạo
    scenarios_file = "data/sample/scenarios.jsonl"
    all_scenarios = load_all_scenarios(scenarios_file)
    
    # Chọn kịch bản S04 (Refund) để dễ thấy nhiều bước
    selected_scenario = next(s for s in all_scenarios if s.id == "S04_risky")
    
    checkpointer = build_checkpointer("sqlite", "checkpoints.db")
    graph = build_graph(checkpointer=checkpointer)
    
    thread_id = f"timetravel-{selected_scenario.id}"
    thread_config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n=== DEMO TIME TRAVEL (Kịch bản: {selected_scenario.id}) ===")
    
    # 2. Chạy Agent lần đầu cho đến khi dừng ở HITL
    print("\n[BƯỚC 1] Chạy Agent lần đầu cho đến khi chờ phê duyệt...")
    os.environ["LANGGRAPH_INTERRUPT"] = "true"
    state = initial_state(selected_scenario)
    
    try:
        graph.invoke(state, thread_config)
    except Exception:
        print("-> Agent đang dừng tại node 'approval'.")

    # 3. Liệt kê lịch sử (Time Travel)
    print("\n[BƯỚC 2] Truy xuất lịch sử các bước (State History):")
    history = list(graph.get_state_history(thread_config))
    
    for i, h_state in enumerate(history):
        # Lấy node cuối cùng thực thi trong checkpoint này
        # Metadata trong LangGraph thường lưu node vừa chạy xong
        metadata = h_state.metadata or {}
        source = metadata.get("source", "unknown")
        step = metadata.get("step", i)
        print(f"{i}. [Step {step}] Node: {source} | Checkpoint ID: {h_state.config['configurable'].get('checkpoint_id')[:8]}...")

    # 4. Thực hiện quay ngược thời gian
    print("\n[BƯỚC 3] Thực hiện Quay ngược thời gian (Time Travel)")
    try:
        choice = int(input(f"Chọn số thứ tự bước bạn muốn quay lại (0-{len(history)-1}): "))
        selected_checkpoint = history[choice]
    except (ValueError, IndexError):
        print("Lựa chọn không hợp lệ.")
        return

    print(f"\n-> Đang quay lại trạng thái tại node: {selected_checkpoint.metadata.get('source')}")
    
    # Chạy lại từ checkpoint đó
    print("[BƯỚC 4] Chạy lại Agent từ điểm đã chọn...")
    # Khi chạy lại từ checkpoint, chúng ta truyền config của checkpoint đó
    for event in graph.stream(None, selected_checkpoint.config, stream_mode="values"):
        if event.get("route"):
            print(f" -> Đang xử lý tại: {event.get('route')}")
        if event.get("final_answer"):
            print(f"\n[KẾT QUẢ CUỐI CÙNG]: {event.get('final_answer')}")

if __name__ == "__main__":
    run_timetravel_demo()
