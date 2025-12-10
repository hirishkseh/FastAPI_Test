# instagramy_streamlit.py
import streamlit as st
import requests
import base64
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="Social Thread", layout="wide")

# -----------------------
# Session state defaults
# -----------------------
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None

# -----------------------
# Small CSS to emulate IG
# -----------------------
st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background: #fafafa;
    }

    /* Top bar */
    .topbar {
        display:flex;
        justify-content:space-between;
        align-items:center;
        padding:12px 20px;
        border-bottom:1px solid #e6e6e6;
        background: white;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .brand {
        font-family: 'Helvetica Neue', Arial;
        font-weight: 700;
        font-size: 20px;
        letter-spacing: 1px;
    }

    /* Post card */
    .post-card {
        background: white;
        border: 1px solid #efefef;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        padding: 12px;
        margin-bottom: 18px;
    }
    .post-header {
        display:flex;
        align-items:center;
        gap:10px;
    }
    .avatar {
        width:44px;
        height:44px;
        border-radius:50%;
        object-fit:cover;
        border:1px solid #ddd;
    }
    .post-image {
        width:100%;
        border-radius: 8px;
        margin-top: 10px;
    }
    .caption-overlay {
        position: relative;
        margin-top: 8px;
    }
    .caption-text {
        font-size: 14px;
        color: #262626;
    }
    .action-row {
        display:flex;
        justify-content:space-between;
        align-items:center;
        margin-top:8px;
    }
    .icons { display:flex; gap:12px; align-items:center; }
    .small-muted { color:#8e8e8e; font-size:12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# Helper functions
# -----------------------
def get_headers():
    """Get authorization headers with token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def encode_text_for_overlay(text):
    """Encode text for ImageKit overlay - base64 then URL encode"""
    if not text:
        return ""
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    return urllib.parse.quote(base64_text)

def create_transformed_url(original_url, transformation_params, caption=None):
    if caption:
        encoded_caption = encode_text_for_overlay(caption)
        text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-100,co-white,bg-000000A0,l-end"
        transformation_params = text_overlay

    if not transformation_params:
        return original_url

    parts = original_url.split("/")
    if len(parts) < 5:
        return original_url
    imagekit_id = parts[3]
    file_path = "/".join(parts[4:])
    base_url = "/".join(parts[:4])
    return f"{base_url}/tr:{transformation_params}/{file_path}"

# -----------------------
# Pages
# -----------------------
def login_page():
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">Social Thread</div>
            <div style="width:120px"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    container = st.container()
    with container:
        left, right = st.columns([1, 1])
        with left:
            st.markdown("<h2 style='margin-bottom:6px'>Welcome 👋</h2>", unsafe_allow_html=True)
            email = st.text_input("Email:", key="login_email")
            password = st.text_input("Password:", type="password", key="login_pass")

            if email and password:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Login", key="btn_login", use_container_width=True):
                        login_data = {"username": email, "password": password}
                        response = requests.post("http://localhost:8000/auth/jwt/login", data=login_data)
                        if response.status_code == 200:
                            token_data = response.json()
                            st.session_state.token = token_data["access_token"]
                            user_response = requests.get("http://localhost:8000/users/me", headers=get_headers())
                            if user_response.status_code == 200:
                                st.session_state.user = user_response.json()
                                st.rerun()
                            else:
                                st.error("Failed to get user info")
                        else:
                            st.error("Invalid email or password!")
                with c2:
                    if st.button("Sign Up", key="btn_signup", use_container_width=True):
                        signup_data = {"email": email, "password": password}
                        response = requests.post("http://localhost:8000/auth/register", json=signup_data)
                        if response.status_code == 201:
                            st.success("Account created! Click Login now.")
                        else:
                            try:
                                error_detail = response.json().get("detail", "Registration failed")
                            except Exception:
                                error_detail = "Registration failed"
                            st.error(f"Registration failed: {error_detail}")
            else:
                st.info("Enter your email and password above")

        with right:
            # Visual promo on right column
            st.markdown(
                """
                <div style='text-align:center;padding:20px;border-radius:10px;background:white;border:1px solid #eee;'>
                    <img src='https://images.unsplash.com/photo-1503023345310-bd7c1de61c7d?q=80&w=400&auto=format&fit=crop&ixlib=rb-4.0.3&s=1' style='width:100%;border-radius:8px;'>
                    <h4 style='margin:8px 0 4px 0'>Share your moments</h4>
                    <div class="small-muted">A simple social app inspired by Instagram — images, videos, captions.</div>
                </div>
                """,
                unsafe_allow_html=True
            )

def upload_page():
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">Social Thread</div>
            <div style="width:120px"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## 📸 Share Something")
    with st.form("upload_form", clear_on_submit=False):
        uploaded_file = st.file_uploader("Choose media", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'])
        caption = st.text_area("Caption:", placeholder="What's on your mind?", key="caption_field")
        submit = st.form_submit_button("Share")

        if submit:
            if not uploaded_file:
                st.warning("Please choose a file to upload.")
            else:
                with st.spinner("Uploading..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {"caption": caption}
                    response = requests.post("http://localhost:8000/upload", files=files, data=data, headers=get_headers())
                    if response.status_code == 200:
                        st.success("Posted!")
                        st.rerun()
                    else:
                        st.error("Upload failed!")

def render_post_card(post):
    # Card wrapper
    st.markdown('<div class="post-card">', unsafe_allow_html=True)

    # Header
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        avatar_url = post.get("avatar", "https://via.placeholder.com/150")
        st.markdown(
            f"""
            <div class="post-header">
                <img src="{avatar_url}" class="avatar" />
                <div>
                    <div style="font-weight:700">{post['email']}</div>
                    <div class="small-muted">{post['created_at'][:10]}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if post.get('is_owner', False):
            if st.button("🗑️", key=f"delete_{post['id']}", help="Delete post", use_container_width=True):
                response = requests.delete(f"http://localhost:8000/posts/{post['id']}", headers=get_headers())
                if response.status_code == 200:
                    st.success("Post deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete post!")

    # Media
    caption = post.get('caption', '')
    if post['file_type'] == 'image':
        # bigger, Instagram-style image card
        display_url = create_transformed_url(post['url'], "w-900,h-900,cm-pad_resize", caption)
        st.markdown(f'<img src="{display_url}" class="post-image" />', unsafe_allow_html=True)
        if caption:
            st.markdown(f'<div class="caption-overlay"><div class="caption-text">{caption}</div></div>', unsafe_allow_html=True)
    else:
        display_url = create_transformed_url(post['url'], "w-900,h-500,cm-pad_resize")
        # Streamlit video respects remote links
        st.video(display_url)
        if caption:
            st.markdown(f'<div class="caption-overlay"><div class="caption-text">{caption}</div></div>', unsafe_allow_html=True)

    # Action row (like/comment placeholders) and small details
    st.markdown(
        f"""
        <div class="action-row">
            <div class="icons">
                <div>❤️</div>
                <div>💬</div>
                <div>🔗</div>
            </div>
            <div class="small-muted">{post.get('likes', 0)} likes • {post.get('comments_count', 0)} comments</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)  # close card

def feed_page():
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">Social Thread</div>
            <div style="width:120px"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## 🏠 Feed")
    response = requests.get("http://localhost:8000/feed", headers=get_headers())
    if response.status_code == 200:
        posts = response.json().get("posts", [])
        if not posts:
            st.info("No posts yet! Be the first to share something.")
            return

        # Center feed with a max width feel
        left_col, main_col, right_col = st.columns([1, 2.5, 1])
        with main_col:
            for post in posts:
                render_post_card(post)
    else:
        st.error("Failed to load feed")

# -----------------------
# Main app logic
# -----------------------
if st.session_state.user is None:
    login_page()
else:
    # Top-left greeting in sidebar
    st.sidebar.title(f"👋 Hi {st.session_state.user['email']}!")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate:", ["🏠 Feed", "📸 Upload"])

    if page == "🏠 Feed":
        feed_page()
    else:
        upload_page()
