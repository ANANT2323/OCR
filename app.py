import os
from flask import Flask, request, render_template_string
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from pdf2image import convert_from_path
from PIL import Image
from docx import Document

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
TEXT_FOLDER = "textdata"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEXT_FOLDER, exist_ok=True)
#ocr text store
documents_store = {}


# BEAUTIFUL UI TEMPLATE
PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart OCR Scanner</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Poppins, Arial;
            background: linear-gradient(135deg, #2193b0, #6dd5ed);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            width: 450px;
            padding: 30px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 30px rgba(0,0,0,0.2);
            backdrop-filter: blur(15px);
            color: white;
            text-align: center;
        }

        h1 {
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 600;
        }

        input[type="file"], input[type="text"] {
            width: 90%;
            padding: 12px;
            margin: 10px;
            border-radius: 10px;
            border: none;
            outline: none;
        }

        button {
            padding: 12px 20px;
            border: none;
            background: #fff;
            color: #2193b0;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 10px;
            transition: 0.3s;
        }

        button:hover {
            background: #f1f1f1;
        }

        ul li {
            color: #fff;
            font-size: 18px;
        }

        .msg {
            margin-top: 10px;
            font-size: 18px;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Smart OCR Scanner</h1>

    <h3>Upload & Scan</h3>
    <form method="POST" enctype="multipart/form-data" action="/upload">
        <input type="file" name="file" required>
        <br>
        <button type="submit">Upload & Scan</button>
    </form>

    <h3>Search Documents</h3>
    <form method="GET" action="/search">
        <input type="text" name="q" placeholder="Search keyword..." required>
        <br>
        <button type="submit">Search</button>
    </form>

    <p class="msg">{{message}}</p>

    {% if results %}
        <h3>Results:</h3>
        <ul>
        {% for r in results %}
            <li>{{r}}</li>
        {% endfor %}
        </ul>
    {% endif %}
</div>

</body>
</html>
"""

def perform_ocr(path):
    ext = path.lower().split(".")[-1]

    # Word file
    if ext == "docx":
        doc = Document(path)
        full_text = ""
        for para in doc.paragraphs:
            full_text += para.text + "\n"
        return full_text

    # PDF
    elif ext == "pdf":
        pages = convert_from_path(path)
        text = ""
        for p in pages:
            text += pytesseract.image_to_string(p)
        return text

    # Images
    else:
        img = Image.open(path)
        return pytesseract.image_to_string(img)


@app.route("/")
def home():
    return render_template_string(PAGE, message="", results=None)


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    text = perform_ocr(filepath)

    text_file = os.path.join(TEXT_FOLDER, file.filename + ".txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(text)

    return render_template_string(PAGE, message="✔ Document Scanned Successfully!", results=None)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        keyword = request.args.get("q", "").lower()
    else:
        keyword = request.form.get("keyword", "").lower()

    results = []

    for filename, text in documents_store.items():
        if keyword in text.lower():
            results.append(filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # Auto open file on Windows
            try:
                os.startfile(file_path)
            except:
                print("Unable to open file")

    if not results:
        return "<h2>No file found</h2>"

    return f"<h2>Files found and opened: {', '.join(results)}</h2>"




if __name__ == "__main__":
    app.run(debug=True)
