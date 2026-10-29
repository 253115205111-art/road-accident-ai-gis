
import os
import html
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


def make_map(records=None):
    m = folium.Map(
        location=[SAMPLE_LAT, SAMPLE_LON],
        zoom_start=13
    )

    folium.Marker(
        [SAMPLE_LAT, SAMPLE_LON],
        tooltip="Teynampet Sample Point",
        popup=(
            "Sample testing point — "
            "NOT a verified accident location."
        ),
        icon=folium.Icon(color="blue")
    ).add_to(m)

    if records is not None:
        for _, row in records.iterrows():
            lat = float(row["latitude"])
            lon = float(row["longitude"])

            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                continue

            location = str(row.get("location", "Uploaded GPS point"))
            details = str(row.get("details", "No details supplied"))

            popup = (
                f"<b>{html.escape(location)}</b><br>"
                f"{html.escape(details)}<br>"
                "<b>Uploaded record — verify source.</b>"
            )

            folium.Marker(
                [lat, lon],
                tooltip=location,
                popup=popup,
                icon=folium.Icon(color="red")
            ).add_to(m)

        if not records.empty:
            coords = [
                [float(r["latitude"]), float(r["longitude"])]
                for _, r in records.iterrows()
                if -90 <= float(r["latitude"]) <= 90
                and -180 <= float(r["longitude"]) <= 180
            ]
            if coords:
                m.fit_bounds(coords)

    map_html = m.get_root().render()

    return (
        '<iframe srcdoc="' +
        html.escape(map_html, quote=True) +
        '" width="100%" height="450" '
        'style="border:0;border-radius:10px;"></iframe>'
    )


def dashboard():
    try:
        spots = load_blackspots()
        return (
            make_map(),
            spots,
            "Dataset loaded. Highway rows are candidates, not GPS pins."
        )
    except Exception as e:
        return make_map(), pd.DataFrame(), (
            "Dataset loading failed: " + str(e)
        )


def upload_gps(file):
    if file is None:
        return make_map(), pd.DataFrame(), "Upload a CSV file first."

    try:
        records = pd.read_csv(file.name)

        required = {"latitude", "longitude"}
        if not required.issubset(records.columns):
            return (
                make_map(),
                pd.DataFrame(),
                "CSV needs latitude and longitude columns."
            )

        records["latitude"] = pd.to_numeric(
            records["latitude"], errors="coerce"
        )
        records["longitude"] = pd.to_numeric(
            records["longitude"], errors="coerce"
        )

        records = records.dropna(
            subset=["latitude", "longitude"]
        )

        records = records[
            records["latitude"].between(-90, 90)
            & records["longitude"].between(-180, 180)
        ]

        if records.empty:
            return (
                make_map(),
                pd.DataFrame(),
                "No valid GPS coordinates found in this file."
            )

        return (
            make_map(records),
            records,
            f"Loaded {len(records)} GPS records. Verify their source "
            "before treating them as confirmed accidents."
        )

    except Exception as e:
        return make_map(), pd.DataFrame(), "Upload failed: " + str(e)


with gr.Blocks(title="Road Accident AI & GIS") as app:
    gr.Markdown("# Road Accident AI & GIS")

    gr.Markdown(
        "## Teynampet, Chennai — Sample Map\n"
        "🔵 Blue pin = sample only, not a verified accident."
    )

    map_output = gr.HTML()

    gr.Markdown("## Upload Accident GPS Data")
    gr.Markdown(
        "Upload a CSV with latitude and longitude columns. "
        "Optional columns: location, details. "
        "Uploaded records are not automatically verified."
    )

    gps_file = gr.File(
        label="Choose GPS CSV",
        file_types=[".csv"],
        type="filepath"
    )
    upload_button = gr.Button("Show GPS Points on Map")

    gps_table = gr.Dataframe(
        label="Uploaded GPS Records",
        interactive=False
    )
    status = gr.Textbox(label="Status")

    upload_button.click(
        fn=upload_gps,
        inputs=[gps_file],
        outputs=[map_output, gps_table, status]
    )

    gr.Markdown("## Top 15 Highway Black-Spot Candidates")
    gr.Markdown(
        "Ranked by dataset counts. These do not have GPS coordinates "
        "and are not shown as map pins."
    )

    spots_table = gr.Dataframe(interactive=False)

    app.load(
        fn=dashboard,
        inputs=[],
        outputs=[map_output, spots_table, status]
    )

app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", "10000"))
)
