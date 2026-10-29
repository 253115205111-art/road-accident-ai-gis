
import gradio as gr
import pandas as pd
import folium
import html
import os

DATA_URL = (
    "https://zenodo.org/records/16946653/files/"
    "ETP_4_New_Data_Accidents.csv?download=1"
)

def load_blackspots():
    try:
        df = pd.read_csv(DATA_URL)

        result = (
            df.groupby([
                "Accident_Location_A",
                "Accident_Location_A_Chainage_km"
            ])
            .size()
            .reset_index(name="Accident_Count")
            .sort_values("Accident_Count", ascending=False)
            .head(15)
        )

        result["Area_Type"] = result[
            "Accident_Location_A"
        ].map({1: "Urban", 2: "Rural"})

        return result[[
            "Area_Type",
            "Accident_Location_A_Chainage_km",
            "Accident_Count"
        ]].rename(columns={
            "Accident_Location_A_Chainage_km": "Chainage_km"
        })

    except Exception:
        return pd.DataFrame({
            "Status": [
                "Dataset unavailable. Please refresh and try again."
            ]
        })


def create_map(lat=None, lon=None, location="User Point",
               details=""):
    m = folium.Map(
        location=[13.04354054, 80.25095281],
        zoom_start=13
    )

    folium.Marker(
        [13.04354054, 80.25095281],
        popup="Teynampet sample point - not verified accident data",
        tooltip="Sample Point",
        icon=folium.Icon(color="blue")
    ).add_to(m)

    if lat is not None and lon is not None:
        popup_text = (
            f"Location: {html.escape(str(location))}<br>"
            f"Details: {html.escape(str(details))}<br>"
            "User-entered GPS point; accident status unverified"
        )

        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip="Entered GPS Point",
            icon=folium.Icon(color="red")
        ).add_to(m)

        m.location = [lat, lon]
        m.zoom_start = 15

    return m.get_root().render()


def show_map(latitude, longitude, location, details):
    try:
        if latitude is None or longitude is None:
            raise ValueError("Enter both latitude and longitude.")

        lat = float(latitude)
        lon = float(longitude)

        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90.")

        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180.")

        map_html = create_map(lat, lon, location, details)
        safe_html = html.escape(map_html, quote=True)

        iframe = f"""
        <iframe
            srcdoc="{safe_html}"
            width="100%"
            height="500"
            style="border:0;border-radius:10px;"
            loading="lazy">
        </iframe>
        """

        return iframe, f"GPS point added: {lat}, {lon}"

    except (ValueError, TypeError) as error:
        map_html = create_map()
        safe_html = html.escape(map_html, quote=True)

        iframe = f"""
        <iframe srcdoc="{safe_html}"
            width="100%" height="500"
            style="border:0;border-radius:10px;">
        </iframe>
        """

        return iframe, f"Error: {error}"


def initial_map():
    map_html = create_map()
    safe_html = html.escape(map_html, quote=True)

    return f"""
    <iframe srcdoc="{safe_html}"
        width="100%" height="500"
        style="border:0;border-radius:10px;">
    </iframe>
    """


with gr.Blocks(title="Road Accident AI & GIS") as app:
    gr.Markdown(
        "# 🚦 Road Accident Black Spot Detection"
    )
    gr.Markdown(
        "AI and GIS-based framework for exploring "
        "accident data and user-entered GPS points."
    )

    gr.Markdown("## 📍 Enter GPS Coordinates")

    with gr.Row():
        latitude = gr.Number(
            label="Latitude",
            value=13.04354054
        )
        longitude = gr.Number(
            label="Longitude",
            value=80.25095281
        )

    location = gr.Textbox(
        label="Location Name",
        value="Teynampet"
    )
    details = gr.Textbox(
        label="Additional Details",
        placeholder="Enter notes (optional)"
    )

    show_button = gr.Button(
        "Show GPS Point on Map",
        variant="primary"
    )

    status = gr.Markdown()
    map_output = gr.HTML(value=initial_map())

    show_button.click(
        fn=show_map,
        inputs=[latitude, longitude, location, details],
        outputs=[map_output, status]
    )

    gr.Markdown("## 📊 Top 15 Black-Spot Candidates")
    gr.Markdown(
        "Ranked by accident-record counts in the source dataset. "
        "These are candidates, not independently verified black spots."
    )

    table = gr.Dataframe(
        value=load_blackspots(),
        interactive=False
    )

app.launch()
