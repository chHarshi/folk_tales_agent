import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from agents.coordinator import CoordinatorAgent

st.set_page_config(page_title="Indian Folk Tales Agent", layout="centered")

@st.cache_resource
def get_agent():
    return CoordinatorAgent()

agent = get_agent()
st.title("Indian Folk Tales Agent")
st.write("Preserving Indian folk tales using AI")

query = st.text_input("What kind of tale would you like?")
language = st.selectbox("Story & audio language", ["English", "Hindi", "Telugu"])
lang_map = {"English": "en", "Hindi": "hi", "Telugu": "te"}
do_tts = st.checkbox("Enable audio narration", value=True)
do_image = st.checkbox("Generate illustration (via Hugging Face)")

if st.button("Generate Story"):
    if not query:
        st.warning("Please enter a query")
    else:
        with st.spinner("Finding and narrating your tale..."):
            r = agent.handle_query(query, lang_map[language], do_tts, do_image)

        if not r["found"]:
            st.info(r["story"])
        else:
            st.subheader("Story")
            st.write(r["story"])

            if r["image"]:
                st.image(r["image"])
            if r["audio"]:
                st.subheader("Audio Narration")
                st.audio(r["audio"])

            for s in r["sources"]:
                st.caption(f"Source: {s['title']} ({s['region']}) — {s['source']}, match score {s['score']}")

            if r["validation"] and "error" not in r["validation"]:
                with st.expander("Quality check"):
                    st.json(r["validation"])