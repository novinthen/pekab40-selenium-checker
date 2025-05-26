from selenium.webdriver.chrome.service import Service
from flask import Flask, request, send_file, render_template
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import os

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

    # Set up Selenium with Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

    results = []
    raw_html = []

    for _, row in df.iterrows():
        ic = str(row['IC'])
        try:
            driver.get("https://kelayakan.pekab40.com.my/semakan-kelayakan")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nokp")))
            input_box = driver.find_element(By.ID, "nokp")
            input_box.clear()
            input_box.send_keys(ic)
            driver.find_element(By.ID, "btnSemak").click()

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "status")))
            status = driver.find_element(By.ID, "status").text
        except Exception as e:
            status = "Error"
            raw_html.append(driver.page_source[:1000])  # Limit output size
        else:
            raw_html.append(driver.page_source[:1000])

        results.append(status)

    driver.quit()
    df["Eligibility Status"] = results
    df["Raw HTML"] = raw_html

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(tmp.name, index=False)
    return send_file(tmp.name, as_attachment=True, download_name="results_checked.xlsx")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
