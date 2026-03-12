import os
import requests
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from email.message import EmailMessage
import smtplib
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


def send_email(file):

    msg = EmailMessage()

    msg["Subject"] = "Daily Energy Intelligence"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    msg.set_content("Attached is today's market intelligence report.")

    with open(file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=file
        )

    smtp = smtplib.SMTP_SSL("smtp.gmail.com", 587)
    smtp.login(EMAIL, PASSWORD)
    smtp.send_message(msg)
    smtp.quit()


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
