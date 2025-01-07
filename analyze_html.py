from bs4 import BeautifulSoup

def analyze_html():
    with open('temp_sdk_doc.html', 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    article = soup.find('article', class_='prose')
    if article:
        print('Found article with classes:', article.get('class'))
        print('\nFirst few children:')
        for child in list(article.children)[:5]:
            print(f'\n--- Child type: {type(child)} ---')
            print(str(child)[:200])
            if hasattr(child, 'name'):
                print('Tag name:', child.name)
                print('Classes:', child.get('class', []))

if __name__ == '__main__':
    analyze_html() 