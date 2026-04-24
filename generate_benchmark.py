import json
import os
import time
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

from src.agent.graph import MultiMemoryAgent
from src.agent.state import MemoryState

load_dotenv()

# Truly No-Memory Agent
class NoMemoryAgent:
    def __init__(self):
        from langchain_openai import ChatOpenAI
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.llm = ChatOpenAI(temperature=0, model=model_name)

    def invoke(self, message: str) -> str:
        resp = self.llm.invoke([HumanMessage(content=message)])
        return resp.content

def run_scenarios():
    print("Initializing Multi-Memory Agent...")
    memory_agent = MultiMemoryAgent()

    # Pre-populate some semantic knowledge
    memory_agent.router.semantic.save_knowledge("doc1", "The docker service name for Redis is 'redis'.", {"topic": "docker"})
    memory_agent.router.semantic.save_knowledge("doc2", "Lab 17 requires 4 types of memory: Short-term, Long-term, Episodic, and Semantic.", {"topic": "lab"})

    scenarios = [
        {
            "id": 1,
            "name": "Recall user name after 6 turns",
            "turns": [
                "Hi, my name is Linh.",
                "I like learning about AI.",
                "What's your favorite programming language?",
                "I also enjoy playing piano.",
                "How is the weather today?",
                "Do you remember my name?"
            ],
            "expected_contains": ["Linh"]
        },
        {
            "id": 2,
            "name": "Allergy conflict update",
            "turns": [
                "I am allergic to cow's milk.",
                "Oh wait, my mistake, I am allergic to soy, not cow's milk.",
                "What am I allergic to?"
            ],
            "expected_contains": ["soy", "đậu nành"]
        },
        {
            "id": 3,
            "name": "Recall previous debug lesson (Episodic)",
            "turns": [
                "I had a bug with connection refused yesterday. I fixed it by using the docker service name.",
                "I need to fix that connection refused bug again. What was the solution?"
            ],
            "expected_contains": ["docker service name", "service name"]
        },
        {
            "id": 4,
            "name": "Retrieve FAQ chunk (Semantic)",
            "turns": [
                "What are the 4 types of memory required for Lab 17?"
            ],
            "expected_contains": ["Short-term", "Long-term", "Episodic", "Semantic"]
        },
        {
            "id": 5,
            "name": "Profile update - Favorite language",
            "turns": [
                "My favorite programming language is Python.",
                "Could you write a simple hello world program for me?",
                "What is my favorite programming language?"
            ],
            "expected_contains": ["Python"]
        },
        {
            "id": 6,
            "name": "Trim/Token budget test",
            "turns": [
                "Here is a long text to fill context: " + "context " * 300,
                "Who are you and what is your purpose?"
            ],
            "expected_contains": ["AI", "assistant"]
        },
        {
            "id": 7,
            "name": "Episodic - Project details",
            "turns": [
                "We finished setting up the Redis database successfully.",
                "What database did we setup?"
            ],
            "expected_contains": ["Redis"]
        },
        {
            "id": 8,
            "name": "Semantic - Redis Docker",
            "turns": [
                "What is the docker service name for Redis?"
            ],
            "expected_contains": ["redis"]
        },
        {
            "id": 9,
            "name": "Multi-turn context (Short-term)",
            "turns": [
                "I have two dogs.",
                "One is black and one is white.",
                "How many dogs do I have?"
            ],
            "expected_contains": ["two", "2"]
        },
        {
            "id": 10,
            "name": "Complex identity update",
            "turns": [
                "I work as a software engineer.",
                "Actually, I just got promoted to AI Architect.",
                "What is my current job title?"
            ],
            "expected_contains": ["AI Architect", "Architect"]
        }
    ]

    results = []
    detailed_logs = []

    for s in scenarios:
        print(f"Running Scenario {s['id']}: {s['name']}")
        
        # No-Memory Agent result (only the last turn of the scenario)
        no_mem = NoMemoryAgent()
        no_mem_ans = no_mem.invoke(s["turns"][-1])
            
        # Agent with Memory
        state = {"messages": [], "user_profile": "", "episodes": [], "semantic_hits": [], "memory_budget": 1500}
        scenario_turns = []
        
        for turn in s["turns"]:
            state["messages"].append(HumanMessage(content=turn))
            state = memory_agent.invoke(state)
            mem_ans = state["messages"][-1].content
            
            # Log turn details
            scenario_turns.append({
                "user": turn,
                "agent_response": mem_ans,
                "current_profile": state.get("user_profile"),
                "retrieved_episodes": [str(ep) for ep in state.get("episodes", [])],
                "semantic_hits": state.get("semantic_hits", [])
            })
            
            # Let the router update memory backends
            memory_agent.router.update_memory(state)

        passed = any(keyword.lower() in mem_ans.lower() for keyword in s["expected_contains"])
        
        results.append({
            "id": s["id"],
            "name": s["name"],
            "no_mem_result": no_mem_ans.replace("\n", " "),
            "mem_result": mem_ans.replace("\n", " "),
            "passed": passed
        })
        
        detailed_logs.append({
            "scenario_id": s["id"],
            "scenario_name": s["name"],
            "turns": scenario_turns,
            "final_status": "Pass" if passed else "Fail"
        })
        time.sleep(1)

    # Save detailed logs
    os.makedirs("logs", exist_ok=True)
    with open("logs/benchmark_details.json", "w", encoding="utf-8") as f:
        json.dump(detailed_logs, f, indent=4, ensure_ascii=False)

    with open("BENCHMARK.md", "w") as f:
        f.write("# Benchmark Report: Multi-Memory Agent vs No-Memory Agent\n\n")
        f.write("| # | Scenario | No-memory result | With-memory result | Pass? |\n")
        f.write("|---|----------|------------------|---------------------|-------|\n")
        for r in results:
            pass_str = "**Pass**" if r['passed'] else "Fail"
            f.write(f"| {r['id']} | {r['name']} | {r['no_mem_result'][:60]}... | {r['mem_result'][:60]}... | {pass_str} |\n")

            
        f.write("\n## Reflection & Limitations\n")
        f.write("1. **Privacy/PII Risk:** Bộ nhớ Profile (Redis) có rủi ro lớn nhất vì lưu trữ thông tin cá nhân (tên, sở thích, bệnh lý/dị ứng). Nếu truy xuất sai, AI có thể rò rỉ thông tin cho phiên làm việc khác hoặc đưa ra lời khuyên nguy hiểm.\n")
        f.write("2. **Deletion & Consent:** Khi User yêu cầu xóa, ta phải xóa ở Profile (Redis), Episodic logs (JSON) và có thể là Conversation buffer. Hiện tại hệ thống hỗ trợ ghi đè (conflict handling) nhưng chưa có cơ chế TLL (Time-To-Live) tự động.\n")
        f.write("3. **Limitation:** Vector search (ChromaDB) có thể mang lại context không liên quan (Hallucination retrieval) nếu CSDL quá lớn và chunking không tốt. Ngoài ra, việc dùng LLM để trích xuất Intent & Profile facts sau mỗi lượt chat làm tăng đáng kể token usage & latency.\n")

    print("Benchmark complete. Report saved to BENCHMARK.md")

if __name__ == "__main__":
    run_scenarios()
