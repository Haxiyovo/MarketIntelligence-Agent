import os
import sys
from typing import TypedDict, List, Dict
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END

# 加载环境变量
load_dotenv()

# --- 1. 定义 Agent 状态 ---
class AgentState(TypedDict):
    target: str               # 调研目标（公司或产品）
    search_queries: List[str] # 拆解的搜索指令
    raw_data: str             # 搜集的原始信息
    report: str               # 最终生成的报告内容

# --- 2. 初始化模型与工具 ---
# 推荐使用 gpt-4o-mini 兼顾速度与成本
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
search_tool = TavilySearchResults(k=5)

# --- 3. 定义节点逻辑 ---

def planner_node(state: AgentState):
    """规划节点：将用户需求拆解为具体的搜索任务"""
    print(f"[*] 正在为目标 '{state['target']}' 制定调研计划...")
    prompt = f"你是一个投研专家。针对目标 '{state['target']}'，请列出3个最能体现其近期核心竞争力或竞品动态的搜索关键词（中文）。只需返回关键词，用逗号隔开。"
    response = llm.invoke(prompt)
    queries = [q.strip() for q in response.content.split(",")]
    return {"search_queries": queries}

def research_node(state: AgentState):
    """搜索节点：执行实时数据抓取"""
    all_results = []
    for query in state["search_queries"]:
        print(f"[*] 正在检索: {query}...")
        results = search_tool.invoke({"query": query})
        all_results.extend([r["content"] for r in results])
    
    return {"raw_data": "\n\n".join(all_results)}

def analyst_node(state: AgentState):
    """分析节点：基于实时数据生成专业投研报告内容"""
    print(f"[*] 正在生成深度投研报告...")
    prompt = f"""
    你是一个资深企业分析师。请基于以下搜集的实时数据，为 {state['target']} 生成一份投研级竞品监控报告。
    
    数据来源：
    {state['raw_data']}
    
    报告必须包含以下模块：
    1. 【核心业务综述】：基于最新动态总结。
    2. 【竞品格局分析】：识别直接竞争对手及其优势。
    3. 【关键风险/机遇】：从数据中洞察到的趋势。
    4. 【投研策略建议】：对该目标的投资或竞争策略建议。
    
    请使用 Markdown 格式撰写，语言要求专业、严谨。
    """
    response = llm.invoke(prompt)
    return {"report": response.content}

# --- 4. 构建工作流图 (Workflow Graph) ---
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("planner", planner_node)
workflow.add_node("researcher", research_node)
workflow.add_node("analyst", analyst_node)

# 设置逻辑连线
workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "analyst")
workflow.add_edge("analyst", END)

# 编译应用
app = workflow.compile()

# --- 5. 执行主程序 ---
if __name__ == "__main__":
    print("=== 企业级 AI 投研监控 Agent 系统 ===")
    user_input = input("请输入您要调研的公司/项目名称: ")
    
    if not user_input.strip():
        print("错误：目标名称不能为空。")
        sys.exit()

    initial_state = {
        "target": user_input,
        "search_queries": [],
        "raw_data": "",
        "report": ""
    }
    
    # 运行 Agent
    final_output = app.invoke(initial_state)
    
    # 输出结果
    print("\n" + "="*50)
    print("生成报告摘要：")
    print(final_output["report"])
    print("="*50)
    
    # 保存结果
    filename = f"report_{user_input}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_output["report"])
    print(f"\n[完成] 完整报告已保存至: {filename}")
