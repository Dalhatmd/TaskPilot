import google.generativeai as genai
from app.core.config import settings
import os

genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)

MODEL_NAME = "gemini-1.5-flash"

def summarize_tasks(tasks: list[dict]) -> str:
    """
    Summarizes a list of tasks using Google Generative AI.

    Args:
        tasks (list[dict]): List of task dictionaries with 'id', 'title', and 'description'.

    Returns:
        str: Summary of the tasks.
    """
    task_descriptions = "\n".join([
        f"{task['id']}. {task['title']}: {task['description']} " + 
        f"[Status: {task.get('status', 'TODO')}]" +
        (f" (Due: {task['due_date']})" if task.get('due_date') else " (No due date)")
        for task in tasks
    ])
    prompt = f""" You are a personal assistant who handles tasks for me.
                Summarize the following tasks:\n{task_descriptions}\nProvide a concise summary.
                The summary should highlight:
                - the main objectives
                - Deadlines coming up soon
                - Any dependencies between tasks.
                - general progress overview

                Do not use a list to tell me. Just talk naturally about the tasks.
                and suggest timelines to finish them.
                """

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text

