
from flask import Flask, request, send_file, render_template
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import tempfile
import os
import time

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    df = pd.read_excel(file)

    if 'IC' not in df.columns:
        return "Missing 'IC' column in Excel file", 400

    # Setup headless Selenium browser
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    results = []
    for _, row in df.iterrows():
        ic = str(row['IC'])
        try:
            driver.get("https://kelayakan.pekab40.com.my/semakan-kelayakan")
            time.sleep(2)
            input_box = driver.find_element(By.ID, "nokp")
            input_box.clear()
            input_box.send_keys(ic)
            driver.find_element(By.ID, "btnSemak").click()
            time.sleep(3)
            status = driver.find_element(By.ID, "status").text
        except Exception:
            status = "Error"
        results.append(status)
        time.sleep(1)

    driver.quit()
    df["Eligibility Status"] = results

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(tmp.name, index=False)
    return send_file(tmp.name, as_attachment=True, download_name="results.xlsx")

if __name__ == '__main__':
    app.run(debug=True)
