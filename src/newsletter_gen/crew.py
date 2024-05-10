from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from newsletter_gen.tools.research import SearchAndContents, FindSimilar, GetContents
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from datetime import datetime

@CrewBase
class NewsletterGenCrew():
  """NewsletterGen crew"""
  agents_config = 'config/agents.yaml'
  tasks_config = 'config/tasks.yaml'
  
  def llm(self):
    llm = ChatAnthropic(model_name="claude-3-sonnet-20240229", max_tokens=4096)
    # llm = ChatGroq(model="llama3-70b-8192")
    # llm = ChatGroq(model="mixtral-8x7b-32768")
    
    return llm
    

  @agent
  def researcher(self) -> Agent:
    return Agent(
      config=self.agents_config['researcher'],
      tools=[SearchAndContents(), FindSimilar(), GetContents()],
      verbose=True,
      llm=self.llm()
    )
    
  @agent 
  def editor(self) -> Agent:
    return Agent(
      config=self.agents_config["editor"],
      verbose=True,
      tools=[SearchAndContents(), FindSimilar(), GetContents()],
      llm=self.llm()
    )

  @agent
  def designer(self) -> Agent:
    return Agent(
      config=self.agents_config["designer"],
      verbose=True,
      allow_delegation=False,
      llm=self.llm()
    )     

  @task
  def research_task(self) -> Task:
    return Task(
      config=self.tasks_config['research_task'],
      agent=self.researcher(),
      output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_research_task.md"
    )

  @task
  def edit_task(self) -> Task:
      return Task(
          config=self.tasks_config["edit_task"],
          agent=self.editor(),
          output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_edit_task.md"
      )

  @task
  def newsletter_task(self) -> Task:
      return Task(
          config=self.tasks_config["newsletter_task"],
          agent=self.designer(),
          output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_newsletter_task.html"
      )

  @crew
  def crew(self) -> Crew:
    """Creates the NewsletterGen crew"""
    return Crew(
      agents=self.agents, # Automatically created by the @agent decorator
      tasks=self.tasks, # Automatically created by the @task decorator
      process=Process.sequential,
      verbose=2,
      # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
    )