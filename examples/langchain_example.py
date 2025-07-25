# Example: Wrapping a LangChain chatbot
from unified_agent_interface import wrap_agent

# Replace with your LangChain agent instance
my_agent = ...
agent = wrap_agent(my_agent)

if agent.supports("chat"):
    print(agent.chat("Hello!"))
    for tok in agent.stream("Tell me more."):
        print(tok, end="", flush=True)
