
import io

import numpy as np
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="AirSketch AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- DESIGN ----------------

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
</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------

if "navigation" not in st.session_state:
    st.session_state.navigation = "🏠 Home"

if "canvas_version" not in st.session_state:
    st.session_state.canvas_version = 0


def open_workspace():
    st.session_state.navigation = "🖼️ Drawing Workspace"


def clear_canvas():
    st.session_state.canvas_version += 1


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("# 🎨 AirSketch AI")
    st.caption("Intelligent Virtual Painter")

    st.radio(
        "NAVIGATION",
        [
            "🏠 Home",
            "🖼️ Drawing Workspace",
            "ℹ️ About Project",
        ],
        key="navigation",
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
        <p>An intelligent virtual drawing system.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("✨ Explore Your Creative Workspace")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature">
            <h3>🖐️ Hand Gestures</h3>
            Browser webcam gesture drawing is planned.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature">
            <h3>🖌️ Drawing Tools</h3>
            Use the brush, colours, eraser and shapes.
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature">
            <h3>💾 Save Artwork</h3>
            Download your drawing as a PNG image.
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    st.button(
        "🚀 Open Drawing Workspace",
        on_click=open_workspace,
        use_container_width=True,
    )


# ---------------- DRAWING WORKSPACE ----------------

elif page == "🖼️ Drawing Workspace":

    st.title("🖼️ Drawing Workspace")
    st.write("Choose a tool and create your artwork.")
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        tool = st.selectbox(
            "🖌️ Drawing Tool",
            ["Brush", "Line", "Rectangle", "Circle", "Triangle", "Eraser"],
        )

    with col2:
        brush_color = st.color_picker(
            "🎨 Choose Colour",
            "#8D78FF",
        )

    with col3:
        brush_size = st.slider(
            "📏 Brush Size",
            min_value=1,
            max_value=30,
            value=5,
        )

    drawing_modes = {
        "Brush": "freedraw",
        "Line": "line",
        "Rectangle": "rect",
        "Circle": "circle",
        "Triangle": "polygon",
        "Eraser": "freedraw",
    }

    selected_color = (
        "#FFFFFF" if tool == "Eraser" else brush_color
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
    )

    st.caption(
        "Draw with your mouse or trackpad. "
        "For the triangle tool, click points to create a polygon."
    )

    st.divider()

    col_clear, col_download = st.columns(2)

    with col_clear:
        st.button(
            "🗑️ Clear Canvas",
            on_click=clear_canvas,
            use_container_width=True,
        )

    with col_download:
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
                "⬇️ Download Artwork",
                data=image_buffer.getvalue(),
                file_name="AirSketch_AI_Artwork.png",
                mime="image/png",
                use_container_width=True,
            )
        else:
            st.button(
                "⬇️ Draw something to enable download",
                disabled=True,
                use_container_width=True,
            )

    st.info(
        "The drawing canvas and PNG download are available here. "
        "Dedicated undo/redo, webcam gestures and voice commands "
        "are not connected yet."
    )


# ---------------- ABOUT PROJECT ----------------

elif page == "ℹ️ About Project":

    st.title("ℹ️ About AirSketch AI")

    st.write(
        "AirSketch AI is a Python-based virtual drawing project "
        "designed to make digital drawing interactive."
    )

    st.subheader("Technology Stack")
    st.write(
        "Python • Streamlit • NumPy • Pillow • OpenCV • MediaPipe"
    )

    st.subheader("Current Features")
    st.markdown("""
    - Brush and colour selection
    - Eraser and geometric shapes
    - Adjustable brush size
    - PNG artwork download
    """)

    st.subheader("Planned Improvements")
    st.markdown("""
    - Browser-based webcam gesture drawing
    - Voice commands
    - Login and registration
    - Shape recognition
    - Dedicated undo and redo
    """)


# ---------------- FOOTER ----------------

st.divider()
st.caption("AirSketch AI | MCA Mini Project")
