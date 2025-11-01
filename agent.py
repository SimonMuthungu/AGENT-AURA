from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
import psycopg2
from dotenv import load_dotenv
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

model = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash",
    temperature=0.2,
    google_api_key=gemini_api_key
    )


def _get_db_connection():
    """Establishes and returns a database connection using the DATABASE_URL URI."""
    
    # 1. Get the single connection string
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("Error: DATABASE_URL environment variable is not set.")
        return None
        
    try:
        # 2. Pass the entire URI string to psycopg2.connect()
        conn = psycopg2.connect(db_url)
        print("Connection successful!")

        # Example query
        # cursor.execute("SELECT NOW();")
        # result = cursor.fetchone()
        # print("Current Time:", result)
        return conn

    except Exception as e:
        # Catch any connection errors (e.g., bad password, host unreachable)
        print(f"Database connection error: {e}")
        return None


@tool
def get_project_costs(project_id: str) -> str:
    """
    Fetches the total budget and non-labor costs (licensing/fees) for a given project ID.
    This provides the baseline financial data from the 'project_budget' table.
    """
    conn = _get_db_connection()
    if not conn:
        return json.dumps({"error": "Database connection failed."})

    sql = f"""
    SELECT total_budget, licensing_costs_ytd
    FROM project_budget
    WHERE project_id = %s;
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (project_id,))
            result = cur.fetchone()
            
            if not result:
                return json.dumps({"error": f"No budget data found for project ID: {project_id}"})
            
            # Use column names for clear JSON output
            data = {
                "total_budget": float(result[0]),
                "non_labor_costs": float(result[1])
            }
            return json.dumps(data)
    except Exception as e:
        return json.dumps({"error": f"SQL execution error: {e}"})
    finally:
        conn.close()


@tool
def get_hours_logged(project_id: str) -> str:
    """
    Fetches employee hours and hourly rates, then calculates the total labor cost for a project.
    This provides the key resource expenditure data from the 'employee_time' table.
    """
    conn = _get_db_connection()
    if not conn:
        return json.dumps({"error": "Database connection failed."})

    sql = f"""
    SELECT hours_logged, hourly_rate
    FROM employee_time
    WHERE project_id = %s;
    """
    
    total_hours = 0
    estimated_labor_cost = 0.0

    try:
        with conn.cursor() as cur:
            cur.execute(sql, (project_id,))
            results = cur.fetchall()
            
            if not results:
                return json.dumps({"total_hours_logged": 0, "estimated_labor_cost": 0.00})
            
            for hours, rate in results:
                total_hours += hours
                estimated_labor_cost += (hours * rate)
                
            # Return the aggregated and calculated result
            output_data = {
                "total_hours_logged": total_hours,
                "estimated_labor_cost": round(estimated_labor_cost, 2)
            }
            return json.dumps(output_data)
            
    except Exception as e:
        return json.dumps({"error": f"SQL execution error: {e}"})
    finally:
        conn.close()


@tool
def get_project_status(project_id: str) -> str:
    """
    Fetches the current status (e.g., 'At Risk') and completion percentage of a project.
    This provides the health metrics from the 'projects' table.
    """
    conn = _get_db_connection()
    if not conn:
        return json.dumps({"error": "Database connection failed."})

    sql = f"""
    SELECT status, completion_pct
    FROM projects
    WHERE project_id = %s;
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (project_id,))
            result = cur.fetchone()
            
            if not result:
                return json.dumps({"error": f"No status data found for project ID: {project_id}"})
            
            data = {
                "project_status": result[0],
                "completion_percentage": float(result[1])
            }
            return json.dumps(data)
    except Exception as e:
        return json.dumps({"error": f"SQL execution error: {e}"})
    finally:
        conn.close()


aura = create_agent(
    model=model, 
    tools=[get_project_costs, get_project_status, get_hours_logged],
    system_prompt="""
    You are a helpful AI assistant that helps a software development company manage their projects. You have access to the following tools:
    - get_project_costs: This function takes a string of project id and returns the total cost of the project so far, showing how much has been spent on the project (except labor costs).
    - get_project_status: This function takes a string of project id and returns the progress of the project so far, showing how much has been completed.
    - get_hours_logged: This function takes a string of project id and returns the total hours logged for the project so far, thus estimating labor costs for the project.
    You are given a project id and a task description. You must use the tools to get the information needed to complete the task. You must then return a response to the user.
    """
    ) 


result = aura.invoke(
    {"messages": [{"role": "user", "content": "what is the project status as of now for project ID Q3_REDESIGN. Is the company on track to achieve its goals within its budget?"}]}
)

print(f"\n\n{result['messages'][-1].content}\n")