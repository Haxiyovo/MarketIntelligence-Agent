# 🚀 AI Investment Intelligence Agent

这是一个基于 **LangGraph** 和 **GPT-4o** 的自动化企业级投研与竞品监控 Agent。

## 🌟 核心价值
传统的 LLM 无法获取实时信息，本项目通过 **Multi-Agent 协作流** 解决了这一痛点：
1. **Planner Agent**: 负责将模糊的需求拆解为多维度的搜索任务。
2. **Researcher Agent**: 通过 Tavily API 实时抓取互联网最新的财报、新闻及行业动态。
3. **Analyst Agent**: 模拟专家思维，对海量非结构化数据进行提炼，输出 Markdown 格式的专业简报。

## 🛠️ 安装与使用
1. 克隆仓库并安装依赖：
   ```bash
   pip install -r requirements.txt
