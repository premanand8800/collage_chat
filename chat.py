import os
from dotenv import load_dotenv
import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_community.tools import TavilySearchResults
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage

# Set API keys
load_dotenv()
groq_api_key = "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"
os.environ["TAVILY_API_KEY"] = "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"

# Initialize tools
TavilySearch = TavilySearchResults()

tools = [
    Tool(name="Tavily_Search", func=TavilySearch.run, description="Useful for answering questions about current events or the current state of the world"),
]

# Initialize memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def LLM_init(selected_llm, selected_model=None):
    if selected_llm == "ChatGroq":
        llm = ChatGroq(groq_api_key=groq_api_key, model_name=selected_model)
    else:
        llm = ChatGroq(groq_api_key=groq_api_key)
    
    return initialize_agent(
        tools=tools,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        llm=llm,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )

# Streamlit UI
st.set_page_config(page_title="College Advisor")
st.markdown("<h1 style='text-align: center;'><b>Chat with our College Advisor</b></h1>", unsafe_allow_html=True)

# Display robot emoji as logo
st.markdown("<p style='text-align: center; font-size: 50px;'>🤖</p>", unsafe_allow_html=True)

# LLM selection
selected_llm = st.sidebar.selectbox("Select LLM", ["ChatGroq", "ChatGoogleGenerativeAI"])

selected_model = None
if selected_llm == "ChatGroq":
    selected_model = st.sidebar.selectbox("Select ChatGroq Model", ['llama3-8b-8192', 'Llama3-70b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it'])

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! How can I assist you with your college search today?"}
    ]
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Load chat history into memory
for message in st.session_state["chat_history"]:
    if message["role"] == "user":
        memory.chat_memory.add_user_message(message["content"])
    else:
        memory.chat_memory.add_ai_message(message["content"])

# Display messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    llm_chain = LLM_init(selected_llm, selected_model)
    response = llm_chain({"input": prompt})

    # Ensure the response has the correct format
    output_content = response.get("output", str(response))

    st.session_state.messages.append({"role": "assistant", "content": output_content})
    st.chat_message("assistant").write(output_content)
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    st.session_state["chat_history"].append({"role": "assistant", "content": output_content})