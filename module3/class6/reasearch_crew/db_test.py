from src.reasearch_crew.tools.sql_tool import SQLTool

sql_tool = SQLTool()

result = sql_tool.run("SELECT * FROM scripts LIMIT 10")

print(result)