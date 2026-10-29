
import gradio as gr
import folium

# Teynampet sample point — NOT a verified accident
SAMPLE_LAT = 13.04354054
SAMPLE_LON = 80.25095281

def show_map():
    m = folium.Map(
        location=[SAMPLE_LAT, SAMPLE_LON],
        zoom_start=15
    )

    folium.Marker(
        [SAMPLE_LAT, SAMPLE_LON],
        tooltip="Sample Testing Point",
        popup="""
        <b>Sample Testing Point</b><br>
        Teynampet, Chennai<br>
        NOT a verified accident location.
        """,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    # Add verified accident points here in future.
    # Each point must have verified latitude and longitude.
    verified_accidents = []

    for point in verified_accidents:
        folium.Marker(
            [point["lat"], point["lon"]],
            tooltip=point["location"],
            popup=point["details"],
            icon=folium.Icon(color="red")
        ).add_to(m)

    return m._repr_html_()

with gr.Blocks(title="Road Accident AI & GIS") as app:
    gr.Markdown("# Road Accident AI & GIS")
    gr.Markdown(
        "### Teynampet, Chennai — Interactive Sample Map\n"
        "**Blue pin = sample only. Not a verified accident.**"
    )
    gr.HTML(value=show_map())

app.launch(
    server_name="0.0.0.0",
    server_port= int(__import__("os").environ.get("PORT", "10000"))
)
