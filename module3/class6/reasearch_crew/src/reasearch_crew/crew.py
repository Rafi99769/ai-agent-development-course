from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
from .tools.sql_tool import SQLTool


@CrewBase
class ReasearchCrew():
    """ReasearchCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def data_fetcher(self) -> Agent:
        return Agent(
            config=self.agents_config['data_fetcher'], # type: ignore[index]
            verbose=True,
            tools=[SQLTool()]
        )

    # @agent
    # def reporting_analyst(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['reporting_analyst'], # type: ignore[index]
    #         verbose=True
    #     )
        
    # @agent
    # def data_plotter(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['data_plotter'], # type: ignore[index]
    #         verbose=True,
    #         allow_code_execution=True
    #     )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def user_query_task(self) -> Task:
        return Task(
            config=self.tasks_config['user_query_task'], # type: ignore[index]
        )

    # @task
    # def reporting_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['reporting_task'], # type: ignore[index]
    #         output_file='report.md'
    #     )
        
    # @task
    # def data_plot_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['data_plot_task'], # type: ignore[index]
    #         output_file='data_plot.png'
    #     )

    @crew
    def crew(self) -> Crew:
        """Creates the ReasearchCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
