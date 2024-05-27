import json
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Union

import streamlit as st
import yaml
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# from langchain_anthropic import ChatAnthropic
from langchain_core.agents import AgentFinish
from langchain_openai import ChatOpenAI

from newsletter_gen.tools.research import FindSimilar, GetContents, SearchAndContents


@CrewBase
class NewsletterGenCrew:
    """
    NewsletterGen crew

    Attributes:
        agents_config (str): The path to the agents configuration file.
        tasks_config (str): The path to the tasks configuration file.

    """

    agents_config = Path("config/agents.yaml")
    tasks_config = Path("config/tasks.yaml")

    # Check if the files exist
    if not agents_config.is_file():
        raise FileNotFoundError(f"No such file: '{agents_config}'")

    if not tasks_config.is_file():
        raise FileNotFoundError(f"No such file: '{tasks_config}'")

    def llm(
        self,
    ) -> ChatOpenAI:  # , ChatAnthropic, ChatGroq, ChatGoogleGenerativeAI]:
        """
        Load the language model

        Returns:
        - llm: Union[ChatOpenAI, ChatAnthropic, ChatGroq, ChatGoogleGenerativeAI]: The language model.

        """
        llm = ChatOpenAI(model="gpt-4o")
        # llm = ChatAnthropic(model_name="claude-3-sonnet-20240229", max_tokens=4096)
        # llm = ChatGroq(model="llama3-70b-8192")
        # llm = ChatGroq(model="mixtral-8x7b-32768")
        # llm = ChatGoogleGenerativeAI(google_api_key=os.getenv("GOOGLE_API_KEY"))

        return llm

    def step_callback(
        self,
        agent_output: Union[str, List[Tuple[Dict, str]], AgentFinish],
        agent_name: str,
        # *args,
    ) -> None:
        """
        Callback function to handle the output of the agents

        Args:
            agent_output (Union[str, List[Tuple[Dict, str]], AgentFinish]): The output of the agent.
            agent_name (str): The name of the agent.

        """

        with st.chat_message("AI"):
            # Try to parse the output if it is a JSON string
            if isinstance(agent_output, str):
                with suppress(json.JSONDecodeError):
                    agent_output = json.loads(agent_output)

            if isinstance(agent_output, list) and all(
                isinstance(item, tuple) for item in agent_output
            ):

                for action, description in agent_output:
                    # Print attributes based on assumed structure
                    st.write(f"Agent Name: {agent_name}")
                    st.write(f"Tool used: {getattr(action, 'tool', 'Unknown')}")
                    st.write(f"Tool input: {getattr(action, 'tool_input', 'Unknown')}")
                    st.write(f"{getattr(action, 'log', 'Unknown')}")
                    with st.expander("Show observation"):
                        st.markdown(f"Observation\n\n{description}")

            # Check if the output is a dictionary as in the second case
            elif isinstance(agent_output, AgentFinish):
                st.write(f"Agent Name: {agent_name}")
                output = agent_output.return_values  # type: ignore[attr-defined]
                st.write(f"I finished my task:\n{output['output']}")

            # Handle unexpected formats
            else:
                st.write(type(agent_output))
                st.write(agent_output)

    @agent
    def researcher(self) -> Agent:
        """
        Creates the Researcher agent

        Returns:
            researcher: Agent: The Researcher agent.

        Raises:
            ValueError: If the researcher is not in the agents_config or the agents_config is not set.
        """

        if not self.agents_config:
            raise ValueError("agents_config is not set")

        # Load the YAML file
        with self.agents_config.open() as f:
            agents_config_data = yaml.safe_load(f)

        if "researcher" not in agents_config_data:
            raise ValueError("researcher is not in agents_config")

        return Agent(
            config=self.agents_config["researcher"],  # type: ignore[index]
            tools=[SearchAndContents(), FindSimilar(), GetContents()],
            verbose=True,
            llm=self.llm(),
            step_callback=lambda step: self.step_callback(step, "Research Agent"),
        )

    @agent
    def editor(self) -> Agent:
        """
        Creates the Editor agent

        Returns:
            Agent: The Editor agent.

        Raises:
            ValueError: If agents_config is not set, agents_config file cannot be opened
                        or "editor" not in the loaded agents_config data.
        """

        if not self.agents_config:
            raise ValueError("agents_config is not set")

        # Load the YAML file
        with self.agents_config.open(encoding="utf-8") as f:
            agents_config_data = yaml.safe_load(f)

        if "editor" not in agents_config_data:
            raise ValueError("editor is not in agents_config")

        return Agent(
            config=agents_config_data["editor"],
            tools=[SearchAndContents(), FindSimilar(), GetContents()],
            verbose=True,
            llm=self.llm(),
            step_callback=lambda step: self.step_callback(step, "Chief Editor"),
        )

    @agent
    def designer(self) -> Agent:
        """
        Creates the Designer agent

        Returns:
        - designer: Agent: The Designer agent.
        """
        return Agent(
            config=self.agents_config["designer"],  # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            llm=self.llm(),
            step_callback=lambda step: self.step_callback(step, "HTML Writer"),
        )

    @task
    def research_task(self) -> Task:  # dead: disable
        """
        Creates the Research Task

        Returns:
        - research_task: Task: The Research Task.
        """
        return Task(
            config=self.tasks_config["research_task"],  # type: ignore[index]
            agent=self.researcher(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_research_task.md",
        )

    @task
    def edit_task(self) -> Task:  # dead: disable
        """
        Creates the Edit Task

        Returns:
        - edit_task: Task: The Edit Task.
        """

        return Task(
            config=self.tasks_config["edit_task"],  # type: ignore[index]
            agent=self.editor(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_edit_task.md",
        )

    @task
    def newsletter_task(self) -> Task:  # dead: disable
        """
        Creates the Newsletter Task

        Returns:
        - newsletter_task: Task: The Newsletter Task.
        """
        return Task(
            config=self.tasks_config["newsletter_task"],  # type: ignore[index]
            agent=self.designer(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_newsletter_task.html",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the NewsletterGen crew

        Returns:
        - crew: Crew: The NewsletterGen crew.
        """
        return Crew(
            agents=self.agents,  # type: ignore[attr-defined]  # Automatically created by the @agent decorator
            tasks=self.tasks,  # type: ignore[attr-defined] # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=2,
        )
