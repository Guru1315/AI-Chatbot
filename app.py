import streamlit as st
from google import genai
import os

# ─── Page Config ───
st.set_page_config(
    page_title="Saveetha Campus Foodie Bot 🍕",
    page_icon="🍕",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS for Premium Look ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Header */
    .header-container {
        text-align: center;
        padding: 1.5rem 1rem 1rem;
        margin-bottom: 1rem;
    }
    .header-emoji {
        font-size: 3.5rem;
        margin-bottom: 0.3rem;
    }
    .header-title {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF6B35, #F7C948, #FF6B35);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .header-subtitle {
        font-size: 0.95rem;
        color: #888;
        margin-top: 0.3rem;
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 16px !important;
        margin-bottom: 0.5rem !important;
        padding: 0.8rem 1rem !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    /* Input box */
    .stChatInput {
        border-radius: 25px !important;
    }

    /* Quick action buttons */
    .quick-btn {
        display: inline-block;
        padding: 0.45rem 1rem;
        margin: 0.25rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #FF6B35, #e85d26);
        color: white !important;
        font-size: 0.82rem;
        font-weight: 500;
        text-decoration: none;
        cursor: pointer;
        border: none;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .quick-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255,107,53,0.4);
    }

    /* Info cards */
    .info-card {
        background: linear-gradient(135deg, rgba(255,107,53,0.08), rgba(247,201,72,0.08));
        border: 1px solid rgba(255,107,53,0.2);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #666;
        font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Load Knowledge Base ───
@st.cache_data
def load_knowledge_base():
    kb_path = os.path.join(os.path.dirname(__file__), "saveetha_university_infos.txt")
    with open(kb_path, "r", encoding="utf-8") as f:
        return f.read()


# ─── Initialize Gemini Client ───
def get_gemini_client():
    api_key = st.session_state.get("api_key", os.environ.get("GOOGLE_API_KEY", ""))
    if not api_key:
        return None

    # Re-use the same client across reruns for this API key, so the
    # underlying connection isn't closed out from under an existing chat.
    if (
        "gemini_client" not in st.session_state
        or st.session_state.get("gemini_client_key") != api_key
    ):
        st.session_state["gemini_client"] = genai.Client(api_key=api_key)
        st.session_state["gemini_client_key"] = api_key
        # A new client means any existing chat is now stale.
        st.session_state.pop("chat", None)

    return st.session_state["gemini_client"]


def get_system_prompt(kb):
    return f"""
you are Saveetha Campus foodie instructor executive your job is to provide answers to the questions asked by the customers,
you should answer them in polite, if there is any questions out of the kb say you did not have that info, only refer the kb and provide answers:

{kb}
"""


# ─── Sidebar: API Key & Info ───
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="Paste your API key here...",
        help="Get your free API key from https://aistudio.google.com/apikey",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input

    st.markdown("---")
    st.markdown("### 📍 Quick Info")
    st.markdown("""
    <div class="info-card">
        <strong>🏫 Saveetha University</strong><br>
        Thandalam, Chennai<br>
        180+ acres campus
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
        <strong>🍛 Popular Spots</strong><br>
        • Creamy Spoon - Biriyani ₹130<br>
        • Sai's Kitchen - Egg Rice ₹60<br>
        • Ram Cafe - Biriyani ₹110<br>
        • Sree Caters - Meals & Fried Rice
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<div class="footer">Made with ❤️ for Saveetha Students</div>',
        unsafe_allow_html=True,
    )


# ─── Header ───
st.markdown("""
<div class="header-container">
    <div class="header-emoji">🍕</div>
    <h1 class="header-title">Saveetha Campus Foodie Bot</h1>
    <p class="header-subtitle">Your AI guide to the best food on campus! Ask me anything 🍛</p>
</div>
""", unsafe_allow_html=True)


# ─── Check API Key ───
client = get_gemini_client()
if not client:
    st.warning("👋 Please enter your **Google Gemini API Key** in the sidebar to start chatting!")
    st.markdown("""
    **How to get your free API key:**
    1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
    2. Click **"Create API Key"**
    3. Copy and paste it in the sidebar
    """)
    st.stop()


# ─── Initialize Chat History ───
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    kb = load_knowledge_base()
    system_prompt = get_system_prompt(kb)
    st.session_state.chat = client.chats.create(
        model="gemini-3.6-flash",
        config={"system_instruction": system_prompt},
    )


# ─── Display Chat History ───
for message in st.session_state.messages:
    avatar = "🍕" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# ─── Quick Action Buttons (only shown when chat is empty) ───
if not st.session_state.messages:
    st.markdown("#### 💡 Try asking:")
    cols = st.columns(2)
    quick_prompts = [
        "🍗 Best biriyani on campus?",
        "🍳 Where to get egg rice?",
        "🏫 Tell me about Saveetha University",
        "💰 Cheapest food options?",
    ]
    for i, prompt_text in enumerate(quick_prompts):
        with cols[i % 2]:
            if st.button(prompt_text, key=f"quick_{i}", use_container_width=True):
                st.session_state["quick_prompt"] = prompt_text
                st.rerun()


# ─── Handle Quick Prompt ───
quick_prompt = st.session_state.pop("quick_prompt", None)


# ─── Chat Input ───
user_input = st.chat_input("Ask me about campus food, locations, prices... 🍛")

# Use quick prompt if clicked
if quick_prompt:
    user_input = quick_prompt

if user_input:
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get bot response
    with st.chat_message("assistant", avatar="🍕"):
        with st.spinner("Cooking up an answer... 🍳"):
            try:
                response = st.session_state.chat.send_message(user_input)
                bot_reply = response.text
            except Exception as e:
                bot_reply = f"Oops! Something went wrong: {str(e)}\n\nPlease check your API key and try again."

        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
