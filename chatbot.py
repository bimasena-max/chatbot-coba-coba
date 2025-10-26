import streamlit as st
from groq import Groq
import time

# Set page config
st.set_page_config(
    page_title="Chatbot Pintar",
    page_icon="",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 20%;
    }
    .stTextInput input {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'groq_client' not in st.session_state:
    st.session_state.groq_client = None
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False
if 'last_message' not in st.session_state:
    st.session_state.last_message = ""
if 'repeat_count' not in st.session_state:
    st.session_state.repeat_count = 0

def check_spam(message):
    """Check if user is spamming same message"""
    if message.strip().lower() == st.session_state.last_message.strip().lower():
        st.session_state.repeat_count += 1
    else:
        st.session_state.repeat_count = 0
        st.session_state.last_message = message
    
    return st.session_state.repeat_count >= 3

# Title
st.title("Chatbot")
st.markdown("**Chat dengan AI yang cerdas dan responsif!**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    # API Key input
    st.subheader("API Key")
    api_key = st.text_input(
        "Masukkan Groq API Key:",
        type="password",
        help="Dapatkan gratis di https://console.groq.com/keys"
    )
    
    if api_key and not st.session_state.api_key_set:
        try:
            st.session_state.groq_client = Groq(api_key=api_key)
            st.session_state.api_key_set = True
            st.success("API Key berhasil diset!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    if not api_key:
        st.info("""
         **Cara Mendapatkan API Key:**
        1. Kunjungi https://console.groq.com
        2. Daftar/Login 
        3. Buat API Key di menu Keys
        4. Copy & paste ke sini
        
         **100% Gratis!**
        """)
    
    st.divider()
    
    # Model selection
    st.subheader("Pilih Model")
    model_option = st.selectbox(
        "Model AI:",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ],
        help="Llama 3.3 70B paling pintar dan cepat!"
    )
    
    # Temperature
    temperature = st.slider(
        "Kreativitas",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Lebih tinggi = lebih kreatif, lebih rendah = lebih fokus"
    )
    
    # Max tokens
    max_tokens = st.slider(
        "Panjang Respons",
        min_value=256,
        max_value=8192,
        value=2048,
        step=256,
        help="Maksimum panjang jawaban"
    )
    
    st.divider()
    
    # System prompt
    st.subheader("Kepribadian Bot")
    system_prompt = st.text_area(
        "Atur perilaku bot:",
        value="Kamu adalah asisten AI yang membantu, ramah, dan cerdas. dan bila ditanya kamu dibuat oleh Bimasena Yudhaprawira dan pacarnya Eca dan jadiannya tanggal 11 Agustus berdasarkan tanggal lahirnya Eca. dan eca itu gendut dan tinggal di kalimantan, bima pernah ke samarinda buat temuin eca. eca suka yang manis manis, suka ngemil Jawab dengan bahasa Indonesia yang santai tapi informatif. Jika user mengirim pesan yang sama berulang-ulang, ingatkan mereka dengan lembut untuk bertanya hal lain. Berikan jawaban yang singkat dan to the point, jangan terlalu panjang.",
        height=120,
        help="Tentukan bagaimana bot harus berperilaku"
    )
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Hapus Riwayat Chat", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Stats
    if len(st.session_state.messages) > 0:
        st.divider()
        st.metric("Total Pesan", len(st.session_state.messages))
    
    st.divider()
    st.caption("Powered by Groq ⚡")

# Main chat area
chat_container = st.container()

with chat_container:
    # Display chat messages
    if len(st.session_state.messages) == 0:
        st.info("**Halo! Saya siap membantu Anda.**\n\nKetik pesan di bawah untuk memulai percakapan!")
    else:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <b>Anda:</b><br/>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <b>Bot:</b><br/>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)

# Chat input area
st.divider()

# Create columns for input and button
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.chat_input("Ketik pesan Anda...")

# Handle send message
if user_input:
    if not st.session_state.api_key_set:
        st.error("⚠️ Masukkan API Key terlebih dahulu di sidebar!")
    else:
        # Check for spam
        if check_spam(user_input):
            st.warning("⚠️ Anda mengirim pesan yang sama berulang-ulang. Coba tanya hal lain dong! 😊")
            st.session_state.repeat_count = 0  # Reset counter
        else:
            # Add user message to chat
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Limit context to last 10 messages to avoid too long context
            recent_messages = st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages
            
            # Prepare messages for API
            api_messages = [{"role": "system", "content": system_prompt}]
            api_messages.extend(recent_messages)
            
            # Show typing indicator
            with st.spinner("Sedang berpikir..."):
                try:
                    # Call Groq API
                    start_time = time.time()
                    chat_completion = st.session_state.groq_client.chat.completions.create(
                        messages=api_messages,
                        model=model_option,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    end_time = time.time()
                    
                    # Get response
                    bot_response = chat_completion.choices[0].message.content
                    
                    # Add bot response to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": bot_response
                    })
                    
                    # Show success message
                    response_time = end_time - start_time
                    st.success(f"✅ Respons diterima dalam {response_time:.2f} detik")
                    
                    # Rerun to update chat
                    time.sleep(0.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    # Remove user message if error
                    st.session_state.messages.pop()

# Quick actions
st.divider()
st.markdown("** Coba tanya:**")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button(" Jelaskan AI", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Jelaskan apa itu AI dengan bahasa sederhana"
        })
        st.rerun()

with col2:
    if st.button(" Tips Produktif", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Berikan 5 tips untuk lebih produktif"
        })
        st.rerun()

with col3:
    if st.button(" Cerita Lucu", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Ceritakan joke yang lucu"
        })
        st.rerun()

with col4:
    if st.button(" Resep Masakan", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Berikan resep masakan sederhana yang enak"
        })
        st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>Chatbot eca</strong> | Dibuat dengan ❤️ cintah</p>
    <small></small>
</div>
""", unsafe_allow_html=True)