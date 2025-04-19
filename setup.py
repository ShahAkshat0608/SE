from setuptools import setup, find_packages

setup(
    name="task-manager-monorepo",
    version="0.3.0",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        "click",
        "Werkzeug",
        "fastapi",
        "uvicorn[standard]",
        "requests",
        "pydantic",
        "pydantic-settings",
        "python-dotenv",
        "sqlalchemy",
        "passlib",
        "python-jose",
        "python-multipart",
        "matplotlib",
        "pandas",
        "bcrypt",
    ],
    entry_points="""
        [console_scripts]
        taskman=cli:cli
    """,
) 