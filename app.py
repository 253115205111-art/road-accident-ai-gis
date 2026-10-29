

import os
import pandas as pd
import gradio as gr
import folium

DATA_URL = (
    "https://zenodo.org/records/16946653/files/"
    "ETP_4_New_Data_Accidents.csv?download=1"
)

SAMPLE_LAT = 13.04354054
SAMPLE_LON = 80.25095281


def load_blackspots():
    df = pd.read_csv(DATA_URL)

    spots = (
        df.groupby([
            "Accident_Location_A",
            "Accident_Location_A_Chainage_km"
        ])
        .size()
        .reset_index(name="Accident_Count")
        .sort_values("Accident_Count", ascending=False)
        .head(15)
    )

    spots["Location_Type"] = spots[
        "Accident_Location_A"
    ].map({1: "Urban", 2: "Rural"})

    spots["Chainage_km"] = spots[
        "Accident_Location_A_Chainage_km"
    ].round(2)

    return spots[[
        "Location_Type",
        "Chainage_km",
        "Accident_Count"
    ]]


def create_map():
    m = folium.Map(
        location=[SAMPLE_LAT, SAMPLE_LON],
        zoom_start=14
    )

    folium.Marker(
        [SAMPLE_LAT, SAMPLE_LON],
        tooltip="Teynampet Sample Point",
        popup=(
            "<b>Sample Testing Point</b><br>"
            "Teynampet, Chennai<br>"
            "<b>Not a verified accident location.</b>"
        ),
        icon=folium.Icon(color="blue")
    ).add_to(m)

    return m.get_root().render()


def dashboard():
    try:
        spots = load_blackspots()
        status = (
            "Dataset loaded successfully. "
            "These are highway candidates, not verified GPS points."
        )
        return create_map(), spots, status
    except Exception as e:
        return create_map(), pd.DataFrame(), (
            "Dataset could not load. Please refresh and try again. "
            + str(e)
        )


with gr.Blocks(title="Road Accident AI & GIS") as app:
    gr.Markdown("# Road Accident AI & GIS")
    gr.Markdown(
        "## Teynampet, Chennai — Sample Map\n"
        "🔵 Blue pin is for testing only, not a verified accident."
    )

    map_output = gr.HTML()
    gr.Markdown("## Top 15 Highway Black-Spot Candidates")
    gr.Markdown(
        "Ranked by dataset accident counts. "
        "GPS coordinates are not available, so these are not map pins."
    )
    table_output = gr.Dataframe(
        headers=["Location Type", "Chainage (km)", "Accident Count"],
        interactive=False
    )
    status_output = gr.Textbox(label="Dataset Status")

    app.load(
        fn=dashboard,
        inputs=[],
        outputs=[map_output, table_output, status_output]
    )

app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", "10000"))
)
