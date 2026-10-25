import io

import streamlit as st
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="AirSketch AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #080b18, #11152b);
    color: #f4f5ff;
}

.block-container {
    padding-top: 2rem;
    max-width: 1300px;
}

[data-testid="stSidebar"] {
    background-color: #10152a;
}

h1, h2, h3 {
    color: #c4b5fd !important;
}

.hero {
    padding: 30px;
    border: 1px solid #34365e;
    border-radius: 22px;
    background: linear-gradient(120deg, #211b48, #102a40);
    margin-bottom: 24px;
}

.hero h1 {
    color: white !important;
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
    color: #b8a6ff !important;
}

div.stButton > button,
div.stDownloadButton > button {
    border-radius: 10px;
    border: 1px solid #8d78ff;
    min-height: 42px;
}

div.stButton > button:hover,
div.stDownloadButton > button:hover {
    border-color: #c4b5fd;
    color: #c4b5fd;
}
</style>
""", unsafe_allow_html=True)


# ---------------- NAVIGATION ----------------

def open_workspace():
    st.session_state.navigation = "🖼️ Drawing Workspace"


if "navigation" not in st.session_state:
    st.session_state.navigation = "🏠 Home"

if "canvas_version" not in st.session_state:
    st.session_state.canvas_version = 0


with st.sidebar:
    st.markdown("# 🎨 AirSketch AI")
    st.caption("Intelligent Virtual Painter")

    st.radio(
        "NAVIGATION",
        [
            "🏠 Home",
            "🖼️ Drawing Workspace",
            "ℹ️ About Project"
        ],
        key="navigation"
    )

    st.divider()
    st.caption("MCA Mini Project")


page = st.session_state.navigation


# ---------------- HOME PAGE ----------------

if page == "🏠 Home":

    st.markdown("""
    <div class="hero">
        <h1>🎨 AirSketch AI</h1>
        <p>Turn your creativity into digital art.</p>
        <p>
            An intelligent virtual drawing system designed
            to make digital art simple and creative.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("✨ Explore Your Creative Workspace")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature">
            <h3>🖐️ Hand Gestures</h3>
            Webcam-based gesture drawing is planned
            for a future update.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature">
            <h3>🖌️ Drawing Tools</h3>
            Draw with different colours, brush sizes,
            shapes and eraser.
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature">
            <h3>🔷 Creative Canvas</h3>
            Create artwork and download it as a PNG image.
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    st.button(
        "🚀 Open Drawing Workspace",
        on_click=open_workspace,
        use_container_width=True
    )


# ---------------- DRAWING WORKSPACE ----------------

elif page == "🖼️ Drawing Workspace":

    st.title("🖼️ Drawing Workspace")
    st.write("Choose your drawing tools and start creating!")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        tool = st.selectbox(
            "🖌️ Select Tool",
            [
                "Brush",
                "Line",
                "Rectangle",
                "Circle",
                "Triangle",
                "Eraser"
            ]
        )

    with col2:
        brush_color = st.color_picker(
            "🎨 Choose Colour",
            "#8D78FF"
        )

    with col3:
        brush_size = st.slider(
            "📏 Brush Size",
            min_value=1,
            max_value=30,
            value=5
        )

    # Map the selected tool to a supported canvas mode.
    drawing_modes = {
        "Brush": "freedraw",
        "Line": "line",
        "Rectangle": "rect",
        "Circle": "circle",
        "Triangle": "polygon",
        "Eraser": "freedraw"
    }

    selected_color = (
        "#FFFFFF" if tool == "Eraser"
        else brush_color
    )

    st.markdown("### ✏️ Your Canvas")

    canvas_result = st_canvas(
        fill_color="rgba(141, 120, 255, 0.15)",
        stroke_width=brush_size,
        stroke_color=selected_color,
        background_color="#FFFFFF",
        height=450,
        width=800,
        drawing_mode=drawing_modes[tool],
        key=f"airs_ketch_canvas_{st.session_state.canvas_version}",
        display_toolbar=True,
        update_streamlit=True,
        return_image_data=True
    )

    st.caption(
        "For a triangle, select Triangle and click the canvas "
        "to add its three points, then close the shape."
    )

    st.divider()

    button1, button2 = st.columns(2)

    with button1:
        if st.button(
            "🗑️ Clear Canvas",
            use_container_width=True
        ):
            st.session_state.canvas_version += 1
            st.rerun()

    with button2:
        if canvas_result.image_data is not None:
            image_array = np.asarray(
                canvas_result.image_data
            ).astype("uint8")

            artwork = Image.fromarray(
                image_array
            ).convert("RGB")

            image_buffer = io.BytesIO()
            artwork.save(image_buffer, format="PNG")

            st.download_button(
                label="⬇️ Download Artwork",
                data=image_buffer.getvalue(),
                file_name="AirSketch_AI_Artwork.png",
                mime="image/png",
                use_container_width=True
            )

    st.info(
        "The canvas supports drawing and PNG export. "
        "The canvas toolbar provides its available editing controls. "
        "Dedicated undo/redo, webcam gestures and voice commands "
        "are not integrated in this version."
    )


# ---------------- ABOUT PROJECT ----------------

elif page == "ℹ️ About Project":

    st.title("ℹ️ About AirSketch AI")

    st.markdown("""
    AirSketch AI is a Python-based virtual drawing project
    intended to make digital drawing more interactive.

    ### ✨ Project Features

    - Digital drawing canvas
    - Brush and colour selection
    - Eraser and geometric shapes
    - Adjustable brush size
    - Download artwork as a PNG image

    ### 🛠️ Technology Stack

    - Python
    - Streamlit
    - NumPy
    - Pillow
    - OpenCV and MediaPipe for planned gesture integration

    ### 🚀 Future Improvements

    - Browser webcam hand tracking
    - Voice commands
    - User registration and login
    - Shape recognition
    - Dedicated undo and redo
    """)


# ---------------- FOOTER ----------------

st.divider()
st.caption("AirSketch AI | MCA Mini Project")
