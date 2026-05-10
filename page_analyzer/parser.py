from bs4 import BeautifulSoup


def parse_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    h1 = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''
    title = soup.title.get_text(strip=True) if soup.title else ''

    desc_tag = soup.find('meta', attrs={'name': 'description'})
    content = desc_tag.get('content', '') if desc_tag else ''
    description = content.strip()

    return {
        'h1': h1,
        'title': title,
        'description': description
    }