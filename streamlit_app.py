=import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io

st.set_page_config(
    page_title="AirSketch AI",
    page_icon="🎨",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #080b18, #11152b);
    color: #f4f5ff;
}
h1, h2, h3 { color: #c4b5fd !important; }
[data-testid="stSidebar"] { background: #10152a; }
div.stButton > button {
    border-radius: 10px;
    border: 1px solid #8d78ff;
}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "Home"

with st.sidebar:
    st.title("🎨 AirSketch AI")
    st.caption("Intelligent Virtual Painter")
    page = st.radio(
        "NAVIGATION",
        ["Home", "Drawing Workspace", "About Project"],
        key="navigation"
    )
    st.session_state.page = page
    st.divider()
    st.caption("MCA Mini Project")

if page == "Home":
    st.title("🎨 AirSketch AI")
    st.subheader("Turn your creativity into digital art.")
    st.write(
        "Create digital artwork with our browser-based "
        "virtual drawing workspace."
    )

    c1, c2, c3 = st.columns(3)
    c1.info("🖐️ **Hand Gestures**\n\nPlanned browser webcam integration")
    c2.info("🖌️ **Drawing Tools**\n\nBrush, colours, eraser and shapes")
    c3.info("🔷 **Shape Recognition**\n\nBasic shape tools")

    if st.button("🚀 Open Drawing Workspace", use_container_width=True):
        st.session_state.navigation = "Drawing Workspace"
        st.rerun()

elif page == "Drawing Workspace":
    st.title("🖼️ Drawing Workspace")
    st.write("Select a tool and start drawing!")

    col1, col2, col3 = st.columns(3)

    with col1:
        tool = st.selectbox(
            "Drawing tool",
            ["Brush", "Line", "Rectangle", "Circle", "Eraser"]
        )

    with col2:
        color = st.color_picker("Brush colour", "#8D78FF")

    with col3:
        width = st.slider("Brush size", 1, 30, 5)

    mode_map = {
        "Brush": "freedraw",
        "Line": "line",
        "Rectangle": "rect",
        "Circle": "circle",
        "Eraser": "freedraw"
    }

    stroke_color = "#FFFFFF" if tool == "Eraser" else color

    if "canvas_key" not in st.session_state:
        st.session_state.canvas_key = 0

    canvas_result = st_canvas(
        fill_color="rgba(141, 120, 255, 0.15)",
        stroke_width=width,
        stroke_color=stroke_color,
        background_color="#FFFFFF",
        height=450,
        width=800,
        drawing_mode=mode_map[tool],
        key=f"canvas_{st.session_state.canvas_key}",
        display_toolbar=True,
        update_streamlit=True,
        return_image_data=True
    )

    b1, b2 = st.columns(2)

    with b1:
        if st.button("🗑️ Clear Canvas", use_container_width=True):
            st.session_state.canvas_key += 1
            st.rerun()

    with b2:
        if canvas_result.image_data is not None:
            image = Image.fromarray(
                canvas_result.image_data.astype("uint8")
            ).convert("RGB")

            output = io.BytesIO()
            image.save(output, format="PNG")

            st.download_button(
                "⬇️ Download Artwork",
                data=output.getvalue(),
                file_name="airs_ketch_artwork.png",
                mime="image/png",
                use_container_width=True
            )

    st.caption(
        "Note: Eraser uses the white canvas background. "
        "Undo/redo, webcam gestures and voice commands "
        "will need additional integration."
    )

elif page == "About Project":
    st.title("ℹ️ About AirSketch AI")
    st.write(
        "AirSketch AI is a Python-based virtual drawing "
        "project designed around gesture recognition."
    )
    st.subheader("Technology Stack")
    st.write("Python • Streamlit • OpenCV • MediaPipe • Pillow")
    st.subheader("Project Features")
    st.markdown("""
    - Digital drawing tools and colour selection
    - Artwork download
    - Browser-based workspace
    - Planned webcam gesture and voice integration
    - Planned login and registration
    """)

st.divider()
st.caption("AirSketch AI | MCA Mini Project")
