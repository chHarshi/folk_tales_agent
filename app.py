import streamlit as st
from agents.coordinator import CoordinatorAgent

st.set_page_config(page_title="Indian Folk Tales Agent", layout="centered")

st.title("Indian Folk Tales Agent")
st.write("Preserving Indian folk tales using AI")

agent = CoordinatorAgent()

query = st.text_input("Enter your query")

language = st.selectbox(
    "Choose Audio language",
    options=["English", "Hindi", "Telugu"]
)

lang_map = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te"
}

do_tts = st.checkbox(" Enable Audio Narration")
do_image = st.checkbox("Generate Image")

if st.button("Generate Story"):
    if not query:
        st.warning("Please enter a query")
    else:
        with st.spinner("Generating..."):
            result = agent.handle_query(
                query=query,
                language=lang_map[language],
                do_tts=do_tts,
                do_image=do_image
            )

        st.subheader("Story")
        st.write(result["story"])

        if result["audio"]:
            st.subheader("Audio Narration")
            st.audio(result["audio"])

        if result["image"]:
            st.subheader("Generated Image")
            st.image(result["image"])
