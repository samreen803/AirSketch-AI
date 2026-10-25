import streamlit as st

st.set_page_config(
    page_title="AirSketch AI",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 AirSketch AI")
st.subheader("Intelligent Gesture-Based Virtual Drawing System")

st.write(
    "AirSketch AI is an AI-based drawing project that aims "
    "to let users draw digitally using hand gestures."
)

st.divider()

st.header("✨ Project Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🖐️ Gesture-Based Drawing")
    st.write("Draw using hand movements with a webcam in the desktop application.")

    st.markdown("### 🎨 Drawing Tools")
    st.write("Brush, eraser, color selection, undo and redo.")

    st.markdown("### 💾 Save Drawings")
    st.write("Save your digital artwork for later use.")

with col2:
    st.markdown("### 🔐 User Login")
    st.write("User registration and login using a database in the desktop application.")

    st.markdown("### 🔷 Shape Recognition")
    st.write("Recognize basic shapes using the project's shape recognition module.")

    st.markdown("### 🎙️ Voice Commands")
    st.write("Use voice commands in the desktop application.")

st.divider()

st.header("🖼️ Try the Web Demo")
st.write("Upload an image to preview it here.")

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    st.image(
        uploaded_file,
        caption="Your uploaded image",
        use_container_width=True
    )

st.divider()

st.header("🛠️ Technology Stack")
st.write(
    "Python • OpenCV • MediaPipe • Tkinter • SQLite"
)

st.info(
    "Note: This is the web demonstration page. "
    "Live webcam gesture drawing is currently part of the desktop application."
)

st.caption("AirSketch AI | MCA Mini Project")
