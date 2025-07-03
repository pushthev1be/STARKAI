from setuptools import setup, find_packages

setup(
    name="starkai",
    version="1.0.0",
    description="Tony Stark inspired AI assistant",
    author="STARKAI Team",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "praw>=7.8.0",
        "PyGithub>=2.6.0",
        "psutil>=7.0.0",
        "pyserial>=3.5",
        "watchdog>=3.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.8.0",
    ],
    entry_points={
        "console_scripts": [
            "starkai=main:main",
        ],
    },
    python_requires=">=3.8",
)
