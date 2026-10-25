
import streamlit as st

st.set_page_config(
    page_title="AirSketch AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #080b18, #11152b);
    color: #f4f5ff;
}
.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}
[data-testid="stSidebar"] {
    background-color: #10152a;
}
.hero {
    padding: 30px;
    border: 1px solid #34365e;
    border-radius: 22px;
    background: linear-gradient(120deg, #211b48, #102a40);
    margin-bottom: 24px;
}
.hero h1 {
    color: white;
    font-size: 42px;
}
.hero p {
    color: #c8cbed;
    font-size: 17px;
}
.feature {
    background: #151b32;
    border: 1px solid #292f50;
    border-radius: 16px;
    padding: 20px;
    min-height: 145px;
    margin-bottom: 12px;
}
.feature h3 {
    color: #b8a6ff;
}
div.stButton > button {
    border-radius: 10px;
    border: 1px solid #8d78ff;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("# 🎨 AirSketch AI")
    st.caption("Intelligent Virtual Painter")
    page = st.radio(
        "NAVIGATION",
        ["🏠 Home", "🖼️ Drawing Workspace", "ℹ️ About Project"]
    )
    st.divider()
    st.caption("MCA Mini Project")

if page == "🏠 Home":
    st.markdown("""
    <div class="hero">
        <h1>🎨 AirSketch AI</h1>
        <p>Turn your creativity into digital art.</p>
        <p>An intelligent gesture-based virtual drawing system.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("✨ Explore Your Creative Workspace")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature">
        <h3>🖐️ Hand Gestures</h3>
        Draw using hand movements with webcam tracking.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature">
        <h3>🖌️ Drawing Tools</h3>
        Brush, colours, eraser and drawing controls.
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature">
        <h3>🔷 Shape Recognition</h3>
        Recognize basic shapes using AI techniques.
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    if st.button("🚀 Open Drawing Workspace", use_container_width=True):
        st.session_state["navigation_page"] = "🖼️ Drawing Workspace"
        st.rerun()

elif page == "🖼️ Drawing Workspace":
    st.title("🖼️ Drawing Workspace")
    st.write("Upload an image to preview it in your workspace.")

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        st.image(
            uploaded_file,
            caption="Your artwork",
            use_container_width=True
        )
    else:
        st.info("Your image preview will appear here after uploading.")

    st.warning(
        "Live webcam gesture drawing is not connected to this web "
        "workspace yet. It requires browser-compatible hand tracking."
    )

elif page == "ℹ️ About Project":
    st.title("ℹ️ About AirSketch AI")
    st.write(
        "AirSketch AI is a Python-based project designed to support "
        "virtual drawing using hand gestures."
    )

    st.subheader("Technology Stack")
    st.write("Python • OpenCV • MediaPipe • Tkinter • SQLite")

    st.subheader("Project Features")
    st.markdown("""
    - Gesture-based virtual drawing
    - Brush, eraser and colour selection
    - Undo and redo
    - Drawing saving
    - User login and registration
    - Shape recognition
    - Voice commands
    """)

st.divider()
st.caption("AirSketch AI | MCA Mini Project")
