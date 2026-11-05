
import gradio as gr
import requests
import os

def get_location(latitude, longitude):
    try:
        if latitude is None or longitude is None:
            return "Please enter both coordinates."

        lat = float(latitude)
        lon = float(longitude)

        if not (-90 <= lat <= 90):
            return "Invalid latitude. Enter between -90 and 90."

        if not (-180 <= lon <= 180):
            return "Invalid longitude. Enter between -180 and 180."

        url = "https://nominatim.openstreetmap.org/reverse"

        response = requests.get(
            url,
            params={
                "lat": lat,
                "lon": lon,
                "format": "jsonv2"
            },
            headers={
                "User-Agent": "RoadAccidentGISCollegeProject/1.0"
            },
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return "Location not found. Check the coordinates."

        address = data.get("address", {})

        return f"""
### 📍 Location Found

**Full Address:**  
{data.get('display_name', 'Not available')}

**Area:** {address.get('suburb', address.get('neighbourhood', 'Not available'))}

**City:** {address.get('city', address.get('town', address.get('village', 'Not available')))}

**District:** {address.get('state_district', 'Not available')}

**State:** {address.get('state', 'Not available')}

**Country:** {address.get('country', 'Not available')}

**Latitude:** {lat}

**Longitude:** {lon}
"""

    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."

    except requests.exceptions.RequestException:
        return "Unable to connect to location service. Try again later."

    except Exception as e:
        return f"Error: {e}"


with gr.Blocks(title="GPS Location Finder") as app:

    gr.Markdown("# 📍 GPS Location Finder")
    gr.Markdown(
        "Enter latitude and longitude to find the location address."
    )

    latitude = gr.Number(
        label="Enter Latitude",
        placeholder="Example: 13.04354"
    )

    longitude = gr.Number(
        label="Enter Longitude",
        placeholder="Example: 80.25095"
    )

    button = gr.Button(
        "Find My Location",
        variant="primary"
    )

    result = gr.Markdown()

    button.click(
        fn=get_location,
        inputs=[latitude, longitude],
        outputs=result
    )

app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860))
)
