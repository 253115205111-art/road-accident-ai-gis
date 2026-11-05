
import gradio as gr
import requests
import folium
import html
import os

def find_location(lat, lon):
    try:
        if lat is None or lon is None:
            raise ValueError("Enter latitude and longitude.")

        lat, lon = float(lat), float(lon)

        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError("Invalid coordinates.")

        url = "https://nominatim.openstreetmap.org/reverse"

        response = requests.get(
            url,
            params={
                "lat": lat,
                "lon": lon,
                "format": "jsonv2"
            },
            headers={"User-Agent": "RoadAccidentGISProject/1.0"},
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        address = data.get("display_name", "Address unavailable")

        # Create map centered on entered coordinates
        m = folium.Map(
            location=[lat, lon],
            zoom_start=16
        )

        folium.Marker(
            [lat, lon],
            tooltip="Selected GPS Location",
            popup=f"Latitude: {lat}<br>Longitude: {lon}",
            icon=folium.Icon(color="red", icon="map-marker")
        ).add_to(m)

        map_html = m.get_root().render()
        safe_map = html.escape(map_html, quote=True)

        iframe = f"""
        <iframe
            srcdoc="{safe_map}"
            width="100%"
            height="500"
            style="border:0;border-radius:12px;">
        </iframe>
        """

        result = f"""
        ## 📍 Location Found

        **Address:** {address}

        **Latitude:** {lat}

        **Longitude:** {lon}
        """

        return result, iframe

    except requests.exceptions.Timeout:
        return "Location service timed out. Try again.", ""

    except Exception as e:
        return f"Error: {e}", ""


with gr.Blocks(title="GPS Location Finder") as app:

    gr.Markdown("# 🗺️ GPS Location Finder")
    gr.Markdown("Enter GPS coordinates to view the location on a map.")

    with gr.Row():
        latitude = gr.Number(
            label="Latitude",
            value=13.04354054
        )
        longitude = gr.Number(
            label="Longitude",
            value=80.25095281
        )

    button = gr.Button("Find Location on Map", variant="primary")

    result = gr.Markdown()
    map_output = gr.HTML()

    button.click(
        find_location,
        inputs=[latitude, longitude],
        outputs=[result, map_output]
    )

app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", "7860"))
)
        
