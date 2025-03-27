from setuptools import setup

setup(
    name="task-manager",
    version="0.1.0",
    py_modules=["cli", "task_manager", "storage", "task"],
    install_requires=[
        "click",
    ],
    entry_points="""
        [console_scripts]
        taskman=cli:cli
    """,
) 