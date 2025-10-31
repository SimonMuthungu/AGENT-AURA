from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool

model = ChatOpenAI(
    model = "gpt-5",
    temperature=0.2,
    max_tokens=300
    )

@tool
def get_project_costs (project_id: str) -> str:
    """
    This function takes a string of project id and returns the total cost of the project so far, showing how much has been spent on the project (except labor costs).
    """

@tool
def get_project_status(project_id: str) -> str:
    """
    This function takes a string of project id and returns the progress of the project so far, showing how much has been completed.
    """

@tool
def get_hours_logged(project_id: str) -> str:
    """
    This function takes a string of project id and returns the total hours logged for the project so far, thus estimating labor costs for the project.
    """


aura = create_agent(
    model=model, 
    tools=[get_project_costs, get_project_status, get_hours_logged],
    system_prompt="""
    You are an AI assistant that helps a software development company manage their projects. You have access to the following tools:
    - get_project_costs: This function takes a string of project id and returns the total cost of the project so far, showing how much has been spent on the project (except labor costs).
    - get_project_status: This function takes a string of project id and returns the progress of the project so far, showing how much has been completed.
    - get_hours_logged: This function takes a string of project id and returns the total hours logged for the project so far, thus estimating labor costs for the project.
    You are given a project id and a task description. You must use the tools to get the information needed to complete the task. You must then return a response to the user.
    """
    ) 