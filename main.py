import os
import requests
import base64
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from email.message import EmailMessage
from datetime import datetime

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["EMAIL_PASSWORD"]

NEWS_URL = "https://uk.marketscreener.com/news/latest/"

def fetch_news():
    response = requests.get(NEWS_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = soup.select("a")[:20]

    news = []
    for a in articles:
        title = a.get_text(strip=True)
        link = a.get("href")

        if title and link:
            news.append({
                "title": title,
                "link": "https://uk.marketscreener.com" + link
            })

    return news[:10]


def summarize(news):
    summaries = []

    for item in news:
        summaries.append({
            "title": item["title"],
            "summary": item["title"],
            "cn": item["title"]
        })

    return summaries


def create_pdf(summaries):

    filename = "market_report.pdf"

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("Daily Energy & Market Intelligence", styles["Title"]))
    story.append(Spacer(1,20))

    story.append(Paragraph(datetime.now().strftime("%Y-%m-%d"), styles["Normal"]))
    story.append(Spacer(1,20))

    for s in summaries:

        story.append(Paragraph("<b>"+s["title"]+"</b>", styles["Heading3"]))
        story.append(Spacer(1,10))

        story.append(Paragraph("Summary: "+s["summary"], styles["Normal"]))
        story.append(Spacer(1,5))

        story.append(Paragraph("中文: "+s["cn"], styles["Normal"]))
        story.append(Spacer(1,20))

    doc = SimpleDocTemplate(filename)

    doc.build(story)

    return filename


def send_email(file_path):
    print("Preparing email via Resend...")

    api_key = os.environ.get("RESEND_API_KEY")
    email_to = os.environ.get("EMAIL")

    if not api_key:
        raise ValueError("Missing RESEND_API_KEY")
    if not email_to:
        raise ValueError("Missing EMAIL")

    with open(file_path, "rb") as f:
        pdf_data = f.read()

    attachment_base64 = base64.b64encode(pdf_data).decode("utf-8")

    payload = {
        "from": "onboarding@resend.dev",
        "to": [email_to],
        "subject": "Daily Market Intelligence",
        "text": "Today's report is attached.",
        "attachments": [
            {
                "filename": "report.pdf",
                "content": attachment_base64
            }
        ]
    }

    print("Sending request to Resend...")
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    print("Resend status code:", response.status_code)
    print("Resend response:", response.text)

    response.raise_for_status()
    print("EMAIL SENT SUCCESS")

def main():

    print("Fetching news...")

    news = fetch_news()

    print("Summarizing...")

    summaries = summarize(news)

    print("Creating PDF...")

    pdf = create_pdf(summaries)

    print("Sending email...")

    send_email(pdf)

    print("Done.")


if __name__ == "__main__":
    main()
