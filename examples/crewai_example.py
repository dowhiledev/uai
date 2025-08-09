from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

# Define Agents
researcher = Agent(
    role='Senior Research Analyst',
    goal='Uncover cutting-edge developments in AI and data science',
    backstory="Expert at identifying emerging trends; presents actionable insights.",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool]
)

writer = Agent(
    role='Tech Content Strategist',
    goal='Craft compelling content on tech advancements',
    backstory="Renowned strategist who transforms complex concepts into compelling narratives.",
    verbose=True,
    allow_delegation=True
)

# Define Tasks
research_task = Task(
    description="Research recent trends in AI.",
    expected_output="A summary of latest AI developments.",
    agent=researcher
)

writing_task = Task(
    description="Write a blog post based on the research summary.",
    expected_output="A well-structured tech blog post.",
    agent=writer
)

# Define Crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
    verbose=True
)

# # Kick off
# result = crew.kickoff(inputs={"topic": "AI trends"})
# print(result)
