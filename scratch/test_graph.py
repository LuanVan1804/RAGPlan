from app.graph import app_graph
import json

inputs = {"user_input": "Plan a 1-day trip to Da Lat"}
config = {"configurable": {"thread_id": "test_thread"}}

print("Invoking graph...")
try:
    result = app_graph.invoke(inputs, config=config)
    print("Result keys:", result.keys())
    print("Final Plan:", result.get("final_plan"))
except Exception as e:
    print("Error:", e)
