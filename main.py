from openai import OpenAI
import streamlit as st

ENV = {}

with open(".env", "r") as f:
    for line in f:
        k, v = line.split("=")
        ENV[k] = v.removesuffix("\n")

client = OpenAI(api_key=ENV["OPENAI_API"])
assistant_id = ENV["ASSISTANT_ID"]

st.title("MENTOR AI")

st.caption(
    """_This AI is designed to be your mentor drawing from knowledge and example of
  the great authors and their books._

  _We are inspired by the famous speech by Steve Jobs, where he mentions
  that he became jealous of 'Alexandar the Great' when he learnt that he
  was taught by Aristotle_
  
  _This project is an attempt to make that a reality._"""
)


if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = client.beta.threads.create().id

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def stream(run):
    for i in run:
        if i.event == "thread.message.delta":
            yield i.data.delta.content[0].text.value


if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        client.beta.threads.messages.create(
            st.session_state["thread_id"], role="user", content=prompt
        )
        run = client.beta.threads.runs.create(
            thread_id=st.session_state["thread_id"],
            assistant_id=assistant_id,
            stream=True,
        )

        response = st.write_stream(stream(run))

        st.session_state.messages.append({"role": "assistant", "content": response})
