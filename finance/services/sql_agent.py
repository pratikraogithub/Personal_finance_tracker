from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
import os
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Connect to Django DB
# If using SQLite:
db = SQLDatabase.from_uri(
    "sqlite:///db.sqlite3",
    sample_rows_in_table_info=3  # Include sample rows for better context
)

# If using Postgres:
# db = SQLDatabase.from_uri(
#     "postgresql://username:password@localhost:5432/dbname",
#     sample_rows_in_table_info=3
# )

# Initialize Ollama LLM
# Make sure Ollama is running: ollama serve
# Popular models: llama3.2, llama3.1, mistral, codellama, deepseek-coder
llm = ChatOllama(
    model="llama3.2",  # Change to your preferred model
    temperature=0,
    base_url="http://localhost:11434"  # Default Ollama URL
)

# Create SQL query generation prompt and chain manually
sql_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a SQL expert. Given an input question, create a syntactically correct SQLite query to run.
Unless the user specifies in the question a specific number of examples to obtain, query for at most 5 results using the LIMIT clause as per SQLite.
Never query for all columns from a table. You must query only the columns that are needed to answer the question.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.

Use the following format:

Question: Question here
SQLQuery: SQL Query to run

Only use the following tables:
{table_info}

Question: {input}"""),
])

sql_chain = sql_prompt | llm | StrOutputParser()

# Create answer generation prompt
answer_prompt = PromptTemplate.from_template(
    """Based on the table schema below, question, sql query, and sql response, write a natural language response:
{table_info}

Question: {question}
SQL Query: {query}
SQL Response: {response}

Provide a clear, conversational answer to the user's question based on the data returned."""
)

# Build complete RAG chain with natural language output
def create_rag_chain():
    """Creates a complete RAG chain that returns natural language answers."""
    
    def execute_query(query: str) -> str:
        """Execute SQL query safely."""
        try:
            return db.run(query)
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return f"Error executing query: {str(e)}"
    
    chain = (
        RunnablePassthrough.assign(
            query=sql_chain,
            table_info=lambda _: db.get_table_info()
        ).assign(
            response=lambda x: execute_query(x["query"])
        )
        | answer_prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

# Initialize the RAG chain
rag_chain = create_rag_chain()

def ask_sql_agent(query: str, return_details: bool = False):
    """
    Ask natural language query and get response.
    
    Args:
        query: Natural language question
        return_details: If True, returns SQL and raw results along with answer
    
    Returns:
        dict with answer and optionally SQL details
    """
    try:
        # Generate SQL
        sql_response = sql_chain.invoke({
            "input": query,
            "table_info": db.get_table_info()
        })
        
        # Extract SQL from response (remove any extra text)
        sql = sql_response.strip()
        if "SQLQuery:" in sql:
            sql = sql.split("SQLQuery:")[-1].strip()
        
        logger.info(f"Generated SQL: {sql}")
        
        # Execute query
        result = db.run(sql)
        logger.info(f"Query result: {result}")
        
        # Generate natural language answer
        answer = rag_chain.invoke({"question": query})
        
        response = {
            "answer": answer,
        }
        
        if return_details:
            response["generated_sql"] = sql
            response["raw_result"] = result
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {
            "answer": f"I encountered an error processing your question: {str(e)}",
            "error": str(e)
        }

def get_sql_only(query: str):
    """Get just the SQL query without executing it."""
    try:
        sql_response = sql_chain.invoke({
            "input": query,
            "table_info": db.get_table_info()
        })
        
        # Extract SQL from response
        sql = sql_response.strip()
        if "SQLQuery:" in sql:
            sql = sql.split("SQLQuery:")[-1].strip()
        
        return sql
    except Exception as e:
        logger.error(f"Error generating SQL: {e}")
        return f"Error: {str(e)}"

def get_table_info():
    """Get information about available tables."""
    return db.get_table_info()

def list_tables():
    """List all available tables in the database."""
    return db.get_usable_table_names()

# Example usage
if __name__ == "__main__":
    print("Available tables:", list_tables())
    print("\n" + "="*50 + "\n")
    
    # Example queries
    test_queries = [
        "How many records are in each table?",
        "Show me the first 5 records",
    ]
    
    for q in test_queries:
        print(f"Question: {q}")
        response = ask_sql_agent(q, return_details=True)
        print(f"Answer: {response['answer']}")
        if 'generated_sql' in response:
            print(f"SQL: {response['generated_sql']}")
        print("\n" + "="*50 + "\n")