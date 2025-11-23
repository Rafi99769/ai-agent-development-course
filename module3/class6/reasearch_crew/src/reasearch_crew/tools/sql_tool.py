from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_uri = os.getenv('DATABASE_URL')


class SQLToolInput(BaseModel):
    """Input schema for SQLTool."""
    query: str = Field(..., description="The Read SQL query to execute.")

class SQLTool(BaseTool):
    name: str = "SQLTool"
    description: str = "A tool for executing Read SQL queries. Only the read queries are allowed."
    args_schema: Type[BaseModel] = SQLToolInput

    def _run(self, query: str) -> str:
        query = query.strip().lower()
        
        if not query.startswith('select'):
            return "Only read queries are allowed. Queries must start with SELECT keyword."
        
        conn = psycopg2.connect(db_uri)
        cursor = conn.cursor()
        
        cursor.execute(query)
        result = cursor.fetchall()
        
        return result