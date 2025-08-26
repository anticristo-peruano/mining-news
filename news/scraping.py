import pandas as pd
from tqdm import tqdm
from newspaper import Article
import nltk
import requests as rq
from bs4 import BeautifulSoup as bs
nltk.download('punkt')

def known_bad_sites(url):
    resp = rq.get(url,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0'})
    soup = bs(resp.content.decode('utf-8'),'html.parser')

    if 'gob' in url:
        title = soup.find('h1').get_text()
        body = soup.find('div',{'class':'description feed-content'}).get_text()
        keywords = None
        tags = None
    elif 'larepublica' in url:
        title = soup.find('h1').get_text()
        body = ' '.join(x.get_text() for x in soup.find_all('p')[:-3])
        keywords = soup.find('meta',{'name':'keywords'}).get('content')
        tags = None
    elif 'elpopular' in url:
        title = soup.find('h1').get_text()
        body = ' '.join([x.get_text() for x in list(soup.find('div',{'class':'MainContent_main__body__LUkri'}).children) if x.name not in ['div','aside','style','script']])
        keywords = soup.find('meta',{'name':'keywords'}).get('content')
        tags = None
    else:
        raise ConnectionRefusedError('URL malo.')

    return title, body, keywords, tags, None

def extract_info_from_url(url):
    try:
        article = Article(url, language='es')  # Se especifica el idioma español
        article.download()
        article.parse()
        return article.title, article.text, article.meta_keywords, article.tags, None  # No hay error
    except:
          try:
              return known_bad_sites(url)  # Intenta extraer información de sitios conocidos

          except Exception as e:
              return None, None, None, None, str(e)  # Si hay error, retorna el mensaje de error

df = pd.read_excel('/content/drive/MyDrive/AnaWeb - Anexos/dump/all_news.xlsx',index_col=0)

results = []
for url in tqdm(df['link'], desc="Procesando enlaces"):
    results.append(extract_info_from_url(url))

# Convertir los resultados en un DataFrame
df[['title', 'body', 'keywords', 'tags','error']] = pd.DataFrame(results, index=df.index)