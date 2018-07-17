from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import sys

def download_latest_form10k(cik):
    """Download latest Form 10-K file of company and save at <cik>.txt
    
    Args:
        cik: `string` CIK number of company
    """
    
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=10-K&count=40".format(cik)
    
    filings_page = urlopen(url).read()
    
    soup = BeautifulSoup(filings_page, 'html.parser')
    
    table = soup.find("table", attrs={'class': 'tableFile2'})
    
    rows = table.find_all("tr")
    
    for row in rows:
        tds = row.find_all("td")
        if tds:
            if tds[0].get_text().lower() == '10-k':
                acc_number = tds[2].get_text()
                start = acc_number.find('Acc-no: ') + len('Acc-no: ')
                acc_number = acc_number[start:start+20]
                file_url = "https://www.sec.gov/Archives/edgar/data/{0}/{1}.txt".format(cik, acc_number)
                report = urlopen(file_url).read().decode('utf-8')
                with open("data/sandp500/{}.txt".format(cik), "w") as f:
                    f.write(report)
                break
                
def download_reports(ciks, start):
    """Download reports.
    
    Args: 
        ciks: `list` CIK list of companies.
        start: `int` starting index.
    """
    for i in range(start, len(ciks)):
        print("Downloading CIK#{}: {}".format(i, ciks[i]))
        download_latest_form10k(ciks[i])

def get_sp500_list():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    wiki_page = urlopen(url).read()
    
    soup = BeautifulSoup(wiki_page, 'html.parser')
    
    table = soup.find('table', attrs={'class': 'wikitable sortable'})
    
    ths = table.find_all('th')
    headers = [th.get_text() for th in ths]
    headers[6] = headers[6].strip("[3][4]")
    headers[8] = headers[8].strip()
    headers.append("File")
    
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    
    companies = []
    for row in rows:
        data = []
        tds = row.find_all('td')
        for td in tds:
            data.append(td.get_text().strip())
        
        # check for data length not including File
        if len(data) == len(headers)-1:
            data.append("{}.txt".format(data[7]))
            companies.append(data)

    # create dataframe
    df = pd.DataFrame(companies, columns=headers)
    df = df.drop_duplicates(subset=['CIK'], keep='first')
    
    # remove duplicate CIK numbered rows, keep only first
    df.to_csv("data/sandp500/companies_list.csv", index=False)
    
    return df


df = get_sp500_list()

# download
# ciks = list(df['CIK'].values)
# start = int(sys.argv[1])
# download_reports(ciks, start)