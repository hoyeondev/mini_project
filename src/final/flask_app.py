from flask import Flask, render_template_string
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

@app.route("/log")
def show_log():
    try:
        df = pd.read_csv("defect_log.txt", header=None, names=["Timestamp", "Detected"])
        df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
        summary = df.groupby('Date').size()

        # 그래프 이미지 생성
        plt.figure(figsize=(8,5))
        summary.plot(kind='bar', color='skyblue')
        plt.title("Defects per Day")
        plt.xlabel("Date")
        plt.ylabel("Number of Defects")
        plt.tight_layout()

        # 이미지 바이너리 변환
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        html = f"""
        <html>
        <head><title>Defect Log</title></head>
        <body>
        <h2>Defects per Day</h2>
        <img src="data:image/png;base64,{plot_url}">
        </body>
        </html>
        """
        return html

    except Exception as e:
        return f"Error reading defect_log.txt: {e}"

if __name__ == "__main__":
    app.run(port=5000, debug=True)
