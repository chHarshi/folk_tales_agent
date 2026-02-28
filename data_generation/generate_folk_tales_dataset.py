import os
import csv
import time
import zipfile
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

regions = [
    "North India", "South India", "East India", "West India",
    "Central India", "Northeast India", "Punjab", "Bengal",
    "Rajasthan", "Kerala", "Tamil Nadu", "Telangana",
    "Uttar Pradesh", "Maharashtra", "Assam", "Odisha",
]

themes = [
    "wisdom", "courage", "honesty", "selflessness",
    "friendship", "compassion", "bravery", "kindness"
]

output_dir = "data/folk_tales"
os.makedirs(output_dir, exist_ok=True)

metadata_path = os.path.join(output_dir, "metadata.csv")
with open(metadata_path, "w", newline="", encoding="utf-8") as meta_file:
    writer = csv.writer(meta_file)
    writer.writerow(["filename", "title", "region", "language", "theme"])

def generate_story(title, region, theme):
    prompt = f"""
You are an expert storyteller of Indian folk tales.
Write a full, detailed Indian folk tale in English.

Title: {title}
Region: {region}
Theme: {theme}

Requirements:
- 5–7 paragraphs
- Clear narrative with characters
- Moral at the end
"""
    response = llm.invoke(prompt)
    return response.content

count = 20

for i in range(1, count + 1):
    title = f"Folk Tale {i:03d}"
    region = regions[i % len(regions)]
    theme = themes[i % len(themes)]

    print(f"Generating story {i}/{count}...")
    story_text = generate_story(title, region, theme)

    filename = f"{title.replace(' ', '_')}.txt"
    path = os.path.join(output_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n")
        f.write(f"Region: {region}\n")
        f.write(f"Language: English\n")
        f.write(f"Theme: {theme}\n\n")
        f.write(story_text.strip())

    with open(metadata_path, "a", newline="", encoding="utf-8") as meta_file:
        writer = csv.writer(meta_file)
        writer.writerow([filename, title, region, "English", theme])

    time.sleep(1)

zip_path = "indian_folk_tales_dataset_generated.zip"
with zipfile.ZipFile(zip_path, "w") as z:
    for file in os.listdir(output_dir):
        z.write(os.path.join(output_dir, file), arcname=file)

print(f"Dataset ready: {zip_path}")
