import gradio as gr

def dashboard():
    return """
    ROAD ACCIDENT AI & GIS

    Dataset Records: 8116
    AI Model Test Accuracy: 87.44%

    Black spots are ranked by recorded accident counts.
    GIS sample point is not a verified accident.
    """

app = gr.Interface(
    fn=dashboard,
    inputs=[],
    outputs=gr.Textbox(label="Project Dashboard"),
    title="Road Accident AI & GIS"
)

app.launch(
    server_name="0.0.0.0",
    server_port=10000
)
