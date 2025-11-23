#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from reasearch_crew.crew import ReasearchCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run(query: str):
    """
    Run the crew.
    """
    inputs = {
        'user_query': query,
    }

    try:
        result = ReasearchCrew().crew().kickoff(inputs=inputs)
        print(result)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == "__main__":
    run()