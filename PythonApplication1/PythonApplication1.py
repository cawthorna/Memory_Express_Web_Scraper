from bs4 import BeautifulSoup
from urllib2 import urlopen
from smtplib import SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import locale
import datetime
import re
import os

# Set Debug
debug = False
debugSend = True
SendToOthers = False

# From https://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-a-python-script
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Send mail Method
def send_email(toEmail):

    # Put params together
    from_addr = 'Do Not Reply <no.reply.cawthornpi@gmail.com>'
    subject = "MemEx Deal of the Day: " + productName
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    locale.setlocale(locale.LC_NUMERIC,'')
    message_text = productName + " is on sale at Memory Express today for " + salePrice + ".\n\nIt is " + saleAmount[1:-1] + " off of the regular price of " + regularPrice + " (" + str(round((float(locale.atof(saleAmount[2:-1]))/float(locale.atof(regularPrice[1:-1])))*100,2)) + "% off).\n\n" + saleEnds

    # Create Message Container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = toEmail


    # Create Message Body
    text = message_text

    html = "<html><head></head><body>"
    html += "<p>" + message_text + "</p>"
    html += "<a href=\"" + productURL + "\">" + productName  + "</a><br><br>"
    html += str(picTag)
    html += "</body></html>"

    # Record MIME Types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container
    msg.attach(part1)
    msg.attach(part2)

    # Send message
    if not debug or (debug and debugSend):
        smtp.sendmail(from_addr,toEmail,msg.as_string())
    else:
        print msg

# Scrape Information
if(debug):
   print "Scraping Information... 0%"
soup = BeautifulSoup(urlopen("http://www.memoryexpress.com/"), 'html.parser')
dailyDealUrl = soup.body.find("div",id="HomePageRotatorItems").find("img", src=re.compile('24hrDailyDeal')).parent
picTag = soup.body.find("div",id="HomePageRotatorItems").find("img", src=re.compile('24hrDailyDeal'))

if(debug):
   print "Scraping Information... 5% "

soup = BeautifulSoup(urlopen("https://www.memoryexpress.com" + dailyDealUrl['href']), 'html.parser')
productName = soup.title.text.split(' at Memory Express - Memory Express Inc.')[0]
productURL = "https://www.memoryexpress.com" + dailyDealUrl['href']

priceStructure = soup.find('div', attrs={'id':"ProductPricing"})

salePrice = priceStructure.find('div', attrs={'class':'GrandTotal'}).get_text()
salePrice = str(salePrice[salePrice.find("$"):salePrice.find(".",salePrice.find("$"))+3])
saleAmount = priceStructure.find('div', attrs={'class':'InstantSavings'}).get_text()
regularPrice = priceStructure.find('div', attrs={'class':'RegularPrice'}).get_text()
saleEnds = priceStructure.find('div', attrs={'class':'EndDate'}).get_text()

if(debug):
   print "Scraping Information... 50% " + productName + " " + saleEnds

saleAmount = saleAmount[1:].split('\n')[1]
regularPrice = regularPrice[1:].split('\n')[0]

if(debug):
   print "Scraping Information... 100% " + salePrice + " " + saleAmount + " " + regularPrice
   print "Setting up SMTP"

# Email productName, salePrice, saleAmmount, regularPrice, saleEnds to text mailing list
## Setup SMTP
smtp = SMTP_SSL()
smtp.set_debuglevel(0)

if(debug):
   print "Connecting..."

smtp.connect('smtp.gmail.com')


if(debug):
   print "Logging in..."

f = open(os.path.join(__location__, 'email_credentials.txt'), 'r');
username = f.readline().strip('\n\r')
password = f.readline().strip('\n\r')
f.close()
if debug:
    print "'" + username + "'"
    print "'" + password + "'"

smtp.login(username,password)

f = open(os.path.join(__location__, 'emails.txt'), 'r');
## Send Emails
for email in f:
    send_email(email)
    if(debug):
        print "Sending Email to: " + email + "\n"
        break

f.close()

## Close SMTP
smtp.close()

if(debug):
    print "SMTP closed."

