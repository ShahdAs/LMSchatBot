import os
from typing import List, Tuple
from utils.load_config import LoadConfig
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import create_sql_agent
import langchain
from langchain.sql_database import SQLDatabase
from langchain.prompts import PromptTemplate, FewShotPromptTemplate 
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
from langchain.llms import OpenAI as LangchainOpenAI
from openai import OpenAI
import re

langchain.debug = True

APPCFG = LoadConfig()


class ChatBot:
    @staticmethod
    def respond(chatbot: List, message: str, chat_type: str, app_functionality: str) -> Tuple:
        
        if app_functionality == "Chat":
            # If we want to use langchain agents for Q&A with our SQL DBs that was created from .sql files.
            if chat_type == "Q&A with stored SQL-DB":
                # directories
                try:
                    db = SQLDatabase.from_uri("mysql+pymysql://root:@localhost/mrlearning")
                   
                    top_k = 10   

                    examples = [
                            { "input": "top 10 employees", "query": "select top 10 emp from emp_table"}
                    ]


                    example_prompt = PromptTemplate.from_template( "Questions: {input}\nSQL query: {query}" )


                    mssql_prompt = FewShotPromptTemplate(
                        examples=examples,
                        example_prompt=example_prompt,
                        prefix="""
                            You are a SQL expert. Generate a correct SQL query for the given question.
                            **Return ONLY the SQL query, no additional text, no prefixes like "SQLQuery:".**
                            Limit to {top_k} results unless specified otherwise.
                            Tables: {table_info}
                            Question: {input}
                        """,
                        suffix="SQL: ",  # Directly prompt for SQL
                        input_variables=["input", "top_k", "table_info"],
                    )


                    Query = create_sql_query_chain(APPCFG.llm, db, prompt = mssql_prompt, k = top_k)
                    execute_query = QuerySQLDataBaseTool(db=db)

                    answer_prompt = PromptTemplate.from_template(
                        """Given the following user question, corresponding SQL query, and SQL result, answer the user question. 

                    Question: {question}
                    SQL Query: {query}
                    SQL Result: {result}
                    Answer: """
                    )

                    answer = answer_prompt | APPCFG.llm | StrOutputParser()
                    chain = (
                        RunnablePassthrough.assign(query=Query).assign(
                            result=itemgetter("query") | execute_query
                        )
                        | answer
                    )



                    response = chain.invoke({"question": message})

                    
                    # execute_query = QuerySQLDataBaseTool(db=db)
                    # write_query = create_sql_query_chain(
                    #     APPCFG.llm, db)
                    # answer_prompt = PromptTemplate.from_template(
                    #     APPCFG.agent_llm_system_role)
                    # answer = answer_prompt | APPCFG.llm | StrOutputParser()
                    # chain = (
                    #     RunnablePassthrough.assign(query=write_query).assign(
                    #         result=itemgetter("query") | execute_query
                    #     )
                    #     | answer
                    # )
                    # response = chain.invoke({"question": message})

                except Exception as e:
                    chatbot.append((message, f"⚠️ فشل الاتصال بقاعدة البيانات: {str(e)}"))
                    return "", chatbot
            # Get the `response` variable from any of the selected scenarios and pass it to the user.
            chatbot.append(
                (message, response))
            return "", chatbot
        else:
            pass
