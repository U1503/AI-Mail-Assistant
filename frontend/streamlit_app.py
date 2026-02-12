import streamlit as st
import requests
import uuid

API_URL = "http://localhost:8000/api/chat"
HISTORY_URL = "http://localhost:8000/api/history"

st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="📧",
    layout="centered",
)

st.title("📧 AI Email Assistant")
# st.caption("Stateful • DB-backed • Gmail-powered")


# -------------------------------------------------
# Conversation ID persistence
# -------------------------------------------------

query_params = st.query_params

if "conversation_id" in query_params:
    session_id = query_params["conversation_id"]
else:
    session_id = str(uuid.uuid4())
    st.query_params["conversation_id"] = session_id

st.session_state.session_id = session_id

# -------------------------------------------------
# Session state
# -------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False

# -------------------------------------------------
# Load history from DB (once)
# -------------------------------------------------

if not st.session_state.history_loaded:
    try:
        resp = requests.get(
            f"{HISTORY_URL}/{st.session_state.session_id}",
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            history = data.get("history", [])

            formatted_messages = []

            for record in history:
                formatted_messages.append(
                    {"role": "user", "content": record["user_input"]}
                )
                formatted_messages.append(
                    {
                        "role": "assistant",
                        "content": record["assistant_response"],
                    }
                )

            st.session_state.messages = formatted_messages
    except Exception:
        pass

    st.session_state.history_loaded = True

# -------------------------------------------------
# Display chat history (safe rendering)
# -------------------------------------------------

cleaned_messages = []

for msg in st.session_state.messages:
    if isinstance(msg, dict) and "role" in msg and "content" in msg:
        cleaned_messages.append(msg)
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Overwrite state with cleaned list (prevents future crash)
st.session_state.messages = cleaned_messages


# -------------------------------------------------
# User input
# -------------------------------------------------

user_input = st.chat_input("Ask about your emails…")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    payload = {
        "message": user_input,
        "session_id": st.session_state.session_id,
    }

    try:
        with st.spinner("Thinking... 🤖"):
            response = requests.post(API_URL, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            assistant_reply = data.get("response", "")
    except Exception as e:
        assistant_reply = f"❌ Error contacting backend: {e}"


    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_reply}
    )

    with st.chat_message("assistant"):
        st.markdown(assistant_reply)


    # -------------------------------------------------
    # 📧 Draft Editing UI (NEW)
    # -------------------------------------------------

    if "I've drafted your email." in assistant_reply:

        # Try to extract Subject and Body from assistant reply
        lines = assistant_reply.splitlines()

        subject = ""
        body = ""
        capture_body = False

        for line in lines:
            if line.startswith("Subject:"):
                subject = line.replace("Subject:", "").strip()
            elif line.startswith("Body:"):
                capture_body = True
            elif capture_body:
                if line.strip() == "":
                    continue
                body += line + "\n"

        st.divider()
        st.subheader("✏️ Edit Draft Before Sending")

        # edited_subject = st.text_input("Subject", value=subject)
        # edited_body = st.text_area("Body", value=body, height=250)

        # st.info("Edit the draft above. Then type 'yes' in chat to send, or type instructions to modify it.")
        def update_draft():
            payload = {
                "message": f"Update the draft to:\nSubject: {st.session_state.edit_subject}\nBody:\n{st.session_state.edit_body}",
                "session_id": st.session_state.session_id,
            }

            response = requests.post(API_URL, json=payload, timeout=60)
            data = response.json()
            assistant_reply = data.get("response", "")

            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_reply}
            )


        edited_subject = st.text_input(
            "Subject",
            value=subject,
            key="edit_subject",
            on_change=update_draft,
        )

        edited_body = st.text_area(
            "Body",
            value=body,
            height=250,
            key="edit_body",
            on_change=update_draft,
        )




# -------------------------------------------------
# Sidebar
# -------------------------------------------------

with st.sidebar:
    st.subheader("⚙️ Controls")

    st.text("Session ID:")
    st.code(st.session_state.session_id)

    if st.button("🔄 New Conversation"):
        new_id = str(uuid.uuid4())
        st.query_params["conversation_id"] = new_id
        st.session_state.session_id = new_id
        st.session_state.messages = []
        st.session_state.history_loaded = False
        st.rerun()
