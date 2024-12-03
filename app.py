import streamlit as st
from pathlib import Path
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

# Page Configuration
st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

# Constants
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"
radio_opt = ["Use SQLLite 3 Database- Student.db", "Connect to MySQL Database"]

# Database Selection
selected_opt = st.sidebar.radio(label="Choose the Database", options=radio_opt)

# Input Handling
if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide MySQL Host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")
else:
    db_uri = LOCALDB
    mysql_host = mysql_user = mysql_password = mysql_db = None

# API Key Input
api_key = st.sidebar.text_input(label="Groq API Key", type="password")

# Validation and Error Handling
def validate_inputs():
    """Validate database and API key inputs"""
    if not db_uri:
        st.error("Please select a database type")
        return False
    
    if not api_key:
        st.error("Please provide a Groq API key")
        return False
    
    if db_uri == MYSQL and not all([mysql_host, mysql_user, mysql_password, mysql_db]):
        st.error("Please provide all MySQL connection details")
        return False
    
    return True

# Only proceed if inputs are valid
if not validate_inputs():
    st.stop()

# Safe LLM Initialization
try:
    llm = ChatGroq(
        groq_api_key=api_key, 
        model_name="Llama3-8b-8192", 
        streaming=True
    )
except Exception as e:
    st.error(f"Error initializing Groq LLM: {e}")
    st.stop()

@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    """Configure database connection"""
    try:
        if db_uri == LOCALDB:
            # SQLite configuration
            dbfilepath = (Path(__file__).parent/"student.db").absolute()
            creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
            return SQLDatabase(create_engine("sqlite:///", creator=creator))
        
        elif db_uri == MYSQL:
            # MySQL configuration
            from urllib.parse import quote_plus
            safe_password = quote_plus(mysql_password)  # URL-encode the password
            connection_string = f"mysql+mysqlconnector://{mysql_user}:{safe_password}@{mysql_host}/{mysql_db}"
            return SQLDatabase(create_engine(connection_string))

    
    except Exception as e:
        st.error(f"Database configuration error: {e}")
        st.stop()

# Database Configuration
try:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
except Exception as e:
    st.error(f"Error setting up database: {e}")
    st.stop()

try:
    toolkit = SQLDatabaseToolkit(
        db=db, 
        llm=llm
    )
    
    # Modify agent creation to handle parsing errors
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,  # Add this to handle parsing errors
        max_iterations=30,  # Limit iterations to prevent infinite loops
        early_stopping_method="force"  # Add an early stopping method
    )
except Exception as e:
    st.error(f"Error creating SQL agent: {e}")
    st.stop()

# Chat Session Management
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you with the database?"}]

# Add clear history function
def clear_chat_history():
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you with the database?"}]

# Clear history button
st.sidebar.button("Clear message history", on_click=clear_chat_history)

# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User Query Handling
user_query = st.chat_input(placeholder="Ask anything about the database")

if user_query:
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    # Process query with enhanced error handling
    with st.chat_message("assistant"):
        try:
            streamlit_callback = StreamlitCallbackHandler(st.container())
            
            # Alternative query execution method
            response = agent.invoke(
                {"input": user_query}, 
                config={"callbacks": [streamlit_callback]}
            )
            
            # Extract the response
            if isinstance(response, dict):
                final_response = response.get('output', 'No response generated')
            else:
                final_response = str(response)
            
            st.session_state.messages.append({"role": "assistant", "content": final_response})
            st.write(final_response)
        
        except Exception as e:
            error_message = f"Error processing your query: {e}"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})