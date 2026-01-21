# Database Connection Setup

This guide explains how to connect PostgreSQL and MySQL databases to the `multiagent_sql_chart.py` script (or any LangChain SQL agent script).

## Prerequisites

You need to install the appropriate database drivers for Python.

```bash
uv sync

# For PostgreSQL
uv add psycopg2-binary

# For MySQL
uv add pymysql
```

## Connection Strings

The script uses SQLAlchemy connection strings via `SQLDatabase.from_uri()`.

### PostgreSQL

Format: `postgresql+psycopg2://user:password@host:port/dbname`

**Example:**
```python
# In your Python script
db_uri = "postgresql+psycopg2://myuser:mypassword@localhost:5432/mydatabase"
db = SQLDatabase.from_uri(db_uri)
```

### MySQL

Format: `mysql+pymysql://user:password@host:port/dbname`

**Example:**
```python
# In your Python script
db_uri = "mysql+pymysql://myuser:mypassword@localhost:3306/mydatabase"
db = SQLDatabase.from_uri(db_uri)
```

## Connecting Multiple Databases

If you need to connect both databases in the same script, you can initialize two separate `SQLDatabase` instances and create separate toolkits/tools for each.

```python
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

# PostgreSQL
pg_db = SQLDatabase.from_uri("postgresql+psycopg2://user:pass@host/pg_db")
pg_toolkit = SQLDatabaseToolkit(db=pg_db, llm=llm)

# MySQL
mysql_db = SQLDatabase.from_uri("mysql+pymysql://user:pass@host/mysql_db")
mysql_toolkit = SQLDatabaseToolkit(db=mysql_db, llm=llm)

# Combine tools or route to specific agents
pg_tools = pg_toolkit.get_tools()
mysql_tools = mysql_toolkit.get_tools()
```

## Environment Variables

It is best practice to store credentials in a `.env` file instead of hardcoding them.

**.env file:**
```
PG_URI=postgresql+psycopg2://user:pass@localhost:5432/db
MYSQL_URI=mysql+pymysql://user:pass@localhost:3306/db
```

**Python code:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

pg_db = SQLDatabase.from_uri(os.getenv("PG_URI"))
mysql_db = SQLDatabase.from_uri(os.getenv("MYSQL_URI"))
```
