from typing import List
from fastapi import FastAPI, UploadFile, File # type: ignore
from fastapi.responses import JSONResponse, FileResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup # type: ignore
from pymongo import MongoClient # type: ignore
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI()

# MongoDB client setup
client = MongoClient(MONGO_URI)
db = client["Demo"]
collection = db["HtmlList"]

# Enable CORS for frontend access (adjust origin if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload1")
async def process_pdf(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Convert PDF to plain text
        text = extract_text(temp_path)
        os.remove(temp_path)
        
        safe_text = text.replace('\n', '<br>')

        # Basic conversion to HTML (replace newlines with <br>)
        html_raw = f"<div>{safe_text}</div>"

        # Optional: Prettify using BeautifulSoup
        soup = BeautifulSoup(html_raw, "html.parser")
        pretty_html = soup.prettify()

        # Save HTML to file
        with open("output.html", "w", encoding="utf-8") as f:
            f.write(pretty_html)

        # Store HTML in MongoDB
        document = {
            "filename": file.filename,
            "html": pretty_html
        }
        result = collection.insert_one(document)

        # Return the HTML to frontend for Tiptap
        return JSONResponse({
            "message": "html inserted in Mongodb database",
            "insertedid": str(result.inserted_id),
            "html": pretty_html})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/upload")
async def process_pdf(files: List[UploadFile] = File(...)):

    filenames =[]
    htmls =[]
    try:
        for file in files:
            # Save uploaded file temporarily
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(await file.read())

            # Convert PDF to plain text
            text = extract_text(temp_path)
            os.remove(temp_path)
            
            safe_text = text.replace('\n', '<br>')

            # Basic conversion to HTML (replace newlines with <br>)
            html_raw = f"<div>{safe_text}</div>"

            # Optional: Prettify using BeautifulSoup
            soup = BeautifulSoup(html_raw, "html.parser")
            pretty_html = soup.prettify()

            # Save HTML to file
            with open(f"output_{file.filename}.html", "w", encoding="utf-8") as f:
                f.write(pretty_html)

            # Store HTML in MongoDB
            document = {
                "filename": file.filename,
                "html": pretty_html
            }
            print(collection.insert_one(document))

            filenames.append(file.filename)
            htmls.append(str(pretty_html))

        # Return the HTML to frontend for Tiptap
        return JSONResponse({
            "message": "htmls inserted in Mongodb database",
            "htmls": htmls,
            "filenames": filenames})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)



@app.post("/download")
def download_html():
    file_path = "./output.html"
    if not os.path.exists(file_path):
        return JSONResponse({"error": "No HTML file found. Please upload a PDF first."}, status_code=404)
    
    return FileResponse(
        path=file_path,
        media_type='text/html',
        filename=file_path,
        headers={"Content-Disposition": "attachment; filename=output.html"}
    )
