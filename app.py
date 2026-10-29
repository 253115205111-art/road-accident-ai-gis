
import gradio as gr
import folium
import html
import pandas as pd

LAT = 13.04354054
LON = 80.25095281

# Previously extracted dataset counts.
# These are candidates, not verified GPS black spots.
DATA = [
    ["Rural", 400.575, 34],
    ["Urban", 499.250, 32],
    ["Rural", 230.200, 22],
    ["Rural", 465.500, 22],
    ["Rural", 152.400, 20],
    ["Rural", 189.600, 18],
    ["Urban", 496.500, 18],
    ["Rural", 228.600, 18],
    ["Rural", 231.000, 16],
    ["Urban", 497.750, 16],
    ["Rural", 226.000, 16],
    ["Urban", 499.100, 16],
    ["Rural", 242.200, 14],
    ["Rural", 187.500, 14],
    ["Rural", 228.000, 14],
]

def make_map(lat=None, lon=None, name="GPS Point", notes=""):
    m = folium.Map(location=[LAT, LON], zoom_start=12)

    folium.Marker(
        [LAT, LON],
        tooltip="Sample point - not a verified accident",
        icon=folium.Icon(color="blue")
    ).add_to(m)

    if lat is not None and lon is not None:
        folium.Marker(
            [lat, lon],
            tooltip=str(name),
            popup=(
                html.escape(str(name)) + "<br>" +
                html.escape(str(notes)) +
                "<br>Accident status not verified"
            ),
            icon=folium.Icon(color="red")
        ).add_to(m)
        m.location = [lat, lon]
        m.zoom_start = 15

    return m.get_root().render()

def show_map(latitude, longitude, name, notes):
    try:
        if latitude is None or longitude is None:
            raise ValueError("Enter both latitude and longitude.")

        lat = float(latitude)
        lon = float(longitude)

        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90.")
        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be between -180 and 180.")

        message = f"GPS point added: {lat}, {lon}"
        map_html = make_map(lat, lon, name or "GPS Point", notes or "")
    except (ValueError, TypeError) as e:
        message = f"Error: {e}"
        map_html = make_map()

    safe = html.escape(map_html, quote=True)
    frame = (
        '<iframe srcdoc="' + safe +
        '" width="100%" height="500" '
        'style="border:0;border-radius:10px"></iframe>'
    )
    return frame, message

def initial_map():
    safe = html.escape(make_map(), quote=True)
    return (
        '<iframe srcdoc="' + safe +
        '" width="100%" height="500" '
        'style="border:0;border-radius:10px"></iframe>'
    )

table = pd.DataFrame(
    DATA,
    columns=["Area Type", "Chainage (km)", "Accident Records"]
)

with gr.Blocks(title="Road Accident AI and GIS") as app:
    gr.Markdown("# Road Accident Black Spot Detection")
    gr.Markdown(
        "Explore sample GIS points and accident-count candidates. "
        "Blue = sample point; red = entered GPS point."
    )

    with gr.Row():
        latitude = gr.Number(label="Latitude", value=LAT)
        longitude = gr.Number(label="Longitude", value=LON)

    name = gr.Textbox(label="Location Name", value="My GPS Point")
    notes = gr.Textbox(label="Notes (optional)")
    button = gr.Button("Show GPS Point on Map", variant="primary")
    status = gr.Markdown()
    map_view = gr.HTML(value=initial_map())

    button.click(
        show_map,
        inputs=[latitude, longitude, name, notes],
        outputs=[map_view, status]
    )

    gr.Markdown("## Top 15 Black-Spot Candidates")
    gr.Markdown(
        "Counts are from previously extracted dataset records. "
        "Chainage is not GPS latitude/longitude."
    )
    gr.Dataframe(value=table, interactive=False)

app.launch()
