# Example: Wrapping a CrewAI agent
from unified_agent_interface import wrap_agent

# Replace with your CrewAI agent instance
my_agent = ...
agent = wrap_agent(my_agent)

if agent.supports("run"):
    tid = agent.run("Example task")
    while agent.status(tid)["state"] != "completed":
        import time; time.sleep(2)
    print(agent.results(tid))
