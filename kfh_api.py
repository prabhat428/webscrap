#!flask/bin/python
from flask import Flask, jsonify,json,request
from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import requests
import mechanicalsoup

app = Flask(__name__)

@app.route('/api/v1.0/findproperty', methods=['POST'])
def get_tasks():
    req_data = request.get_json()
    browser = mechanicalsoup.StatefulBrowser()
    browser.open("https://www.kfh.co.uk/")
    browser.select_form('form[action="/residential-properties"]')
    browser["searchtext"] = req_data['searchname']
    response = browser.submit_selected()

    page = requests.get(browser.get_url()+"/?v=2")
    soup = BeautifulSoup(page.content, 'html.parser')
    uldiv = soup.find_all('div', {'class': 'result-actions'})
    alldata = []
    for lidiv in uldiv:
        lp = lidiv.find('a').get('href')
        page = requests.get("https://www.kfh.co.uk/"+lp+"/?v=2")
        soup = BeautifulSoup(page.content, 'html.parser')
        uldiv = soup.find_all('div', {'class': 'container'})
        paranames = []
        pricepros = []
        imgnames  = []
        featurenames = []

        for uldivs in uldiv:
            for cvimg in uldivs.find_all("div", {"class": "property-details__header"}):
                pname = cvimg.find('h1').text
                paraname =' '.join(pname.split())
                paranames.append(paraname)
            for proprice in uldivs.find_all("div", {"class": "property-details__price-lg"}):
                price = proprice.find('p').text
                pricepro =' '.join(price.split())
                pricepros.append(pricepro)
            for propimg in uldivs.find_all("img", {"class": "img-responsive"}):
                imgname = propimg['src']
                imgnames.append(imgname)
            for propfeat in uldivs.find_all("ul", {"class": "property-feature-list-horz"}):
                for litag in propfeat.find_all('li'):
                    featurename = litag.text
                    featurenames.append(featurename)
        paranames.extend(pricepros+imgnames+featurenames)
        alldata.append(paranames)
        print(alldata)

    return jsonify({'tasks': alldata})

if __name__ == '__main__':
    app.run(debug=True)