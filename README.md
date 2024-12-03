# LangChain SQL Database Chat Interface

## Project Overview
This is a Streamlit application that allows users to interact with SQL databases (SQLite and MySQL) using natural language queries powered by LangChain and Groq's language model.

## Features
- Support for SQLite and MySQL databases
- Natural language querying using AI
- Streamlit-based web interface
- Secure API key management
- Query history and chat interface

## Prerequisites
- Python 3.8+
- Streamlit
- LangChain
- Groq API Key
- SQLAlchemy
- sqlite3 (for local database)
- MySQL Connector (for MySQL connections)

## Installation

1. Clone the repository:
```bash
git clone https://your-repository-url.git
cd your-repository-name
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration
### Database Setup
- For SQLite: Ensure student.db is in the project directory
- For MySQL: Prepare your MySQL connection details
### Groq API
- Obtain an API key from Groq

## Running the Application
streamlit run app.py

## Usage
1. Select database type (SQLite or MySQL)
2. Enter Groq API key
3. For MySQL, provide connection details
4. Start querying your database using natural language

## Database Schema
- NAME (VARCHAR)
- CLASS (VARCHAR)
- SECTION (VARCHAR)
- MARKS (INT)

## Technologies Used
- Streamlit
- LangChain
- Groq AI
- SQLAlchemy
- SQLite/MySQL

## License


## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
