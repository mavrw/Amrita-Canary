from selenium import webdriver
from time import sleep
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import pyimgur
import smtplib
import ssl

# Imgur OAuth2 credentials
IMGUR_CLIENT_ID = '4a04992d0c1fd6d'
IMGUR_CLIENT_SECRET = 'a37fe66070716997601d5796a466f11c8a70621a' # this is invalid, but go ahead and try it if you want lol

# Date Time formatting
now = datetime.now()
date_time = now.strftime("%m-%d-%Y_%H-%M-%S")

# Canary Settings
webpage = 'https://www.amrita.net'
search_string = '© 2020 Amrita® Aromatherapy'

# Email Settings
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "canary@amrita.net"
sender_password = 'Amrita Website Canary!@#'
# recipient_emails = ["matthew.reederwillson@amrita.net"]
recipient_emails = ["matthew.reederwillson@amrita.net",
                    "stuart.goris@amrita.net",
                    "shaun@shaunbanton.co.uk",
                    "kevin@olamz.com"]

# Get the source of the webpage
r = requests.get(webpage)
homepage_source = r.text


# Setup selenium driver, load the webpage, and then take the screenshot
def get_webpage_screenshot():
    driver = webdriver.Firefox()
    driver.get(webpage)
    sleep(1)
    driver.get_screenshot_as_file(date_time + ".png")
    driver.quit()


# Upload the Screenshot to Imgur
def upload_screenshot():
    im = pyimgur.Imgur(client_id=IMGUR_CLIENT_ID, client_secret=IMGUR_CLIENT_SECRET)
    uploaded_image = im.upload_image(date_time + ".png")
    return uploaded_image.link


def send_email(recipient_email, status_code, image_link, test_mode):
    message = MIMEMultipart("alternative")
    if test_mode:
        message["Subject"] = "Amrita Canary: TEST"
    elif status_code == '200':
        message["Subject"] = "Amrita Canary: HTTP Status Code " + status_code
    else:
        message["Subject"] = "Amrita Canary: ERROR " + status_code
    message["From"] = sender_email
    message["To"] = recipient_email

    # Plain-text email
    text = """\
    Amrita Webpage is inaccessible.
    HTTP Status code: %s
    """ % status_code

    # HTML email
    html = """\
    <html>
        <body>
            <center>
                <div style="border-style: ridge">
                    <p style="font-family: Courier;">
                        <h1>Amrita's Website is currently inaccessible!</h3>
                        <h2>HTTP Status Code: %s</h4>
                        <hr>
                    </p>
                    <img src="%s">
                </div>
            </center>
        </body>
    </html>
    """ % (status_code, image_link)

    # Create the MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add the MIMEText objects to the Multipart message
    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp_server)
    print(datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ": Connecting to SMTP server...")
    server.connect(smtp_server, smtp_port)
    print(datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ": Connected!")
    print(datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ": Server ehlo...")
    server.ehlo()
    print(datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ": ehlo successful!")
    print(datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ": Attempting starttls...")
    server.starttls()
    print(datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ": starttls successful!")
    print(datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ": Attempting to login to smtp server...")
    server.login(sender_email, sender_password)
    print(datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ": Login successful!")
    print(datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ": Sending email...")
    server.sendmail(sender_email, recipient_email, message.as_string())
    print(datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ": Email sent!")
    print(datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ": Quitting SMTP connection.")
    server.quit()


# Run the checks against the status code, and substring search
if r.status_code not in [200, 301, 302]:
    print("THE SITE IS DOWN")

    # Take Screenshot of page
    get_webpage_screenshot()
    # Upload the screenshot
    screenshot = upload_screenshot()

    for recipient in recipient_emails:
        send_email(recipient, str(r.status_code), screenshot)
elif search_string not in homepage_source:
    print("Search string was NOT FOUND. Check website IMMEDIATELY")

    # Take Screenshot of page
    get_webpage_screenshot()
    # Upload the screenshot
    screenshot = upload_screenshot()

    for recipient in recipient_emails:
        send_email(recipient, str(r.status_code), screenshot)
else:
    print("Search String FOUND. Site should be accessible as normal.")
    # for recipient in recipient_emails:
        # send_email(recipient, str(r.status_code), screenshot, test_mode=True)

# Print the status of the canary
print("======== AMRITA.NET CANARY ========")
print("Ran at: " + date_time)
print("HTTP STATUS CODE: " + str(r.status_code))
print("===================================\n")
# print("Webpage Screenshot: " + screenshot)
