from langgraph_agent_lab.graph import build_graph

def export():
    # 1. Khởi tạo graph
    graph = build_graph()
    
    # 2. Lấy mã Mermaid
    mermaid_code = graph.get_graph().draw_mermaid()
    
    # 3. Lưu ra file .mmd
    with open("reports/graph_diagram.mmd", "w", encoding="utf-8") as f:
        f.write(mermaid_code)
    
    print("--- MERMAID CODE ---")
    print(mermaid_code)
    print("\n--- Đã lưu mã sơ đồ vào: reports/graph_diagram.mmd ---")
    print("Bạn có thể copy mã trên và dán vào https://mermaid.live/ để lấy ảnh.")

if __name__ == "__main__":
    export()
