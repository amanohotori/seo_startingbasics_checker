import requests
import sys
import zenhan
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def check_seo_criteria(url):

    response = requests.get(url)

    # ステータスコードが200以外の場合はエラーメッセージを表示して終了
    if response.status_code != 200:
        print("Failed to access the website. Please check the URL and try again.")
        return False

    soup = BeautifulSoup(response.content, 'html.parser')

    # 変数scoreを初期化
    score = 0

    # 1. タイトルタグが適切な長さである。(10点)
    # タイトルタグの取得
    title_tag = soup.title
    if title_tag is None:
        # タイトルタグが存在しない場合は0点
        score += 0
    else:
        # タイトルタグが存在する場合は文字数をチェック
        title_text = title_tag.text.strip()
        # 全角文字を2文字にカウント
        title_text_z2h = zenhan.z2h(title_text, mode=2, ignore=())
        if len(title_text_z2h) >= 30 and len(title_text_z2h) <= 60:
            # 文字数が30~60文字の場合は満点
            score += 10
        elif len(title_text_z2h) > 60:
            # 文字数が60文字より多い場合は5点
            score += 5
        else:
            # 文字数が30文字未満の場合は0点
            score += 0

    # 2. メタ情報が適切な長さに設定されている (10点)
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag is None:
        # メタ説明タグが存在しない場合は0点
        score += 0
    else:
        # メタ説明タグが存在する場合は文字数をチェック
        meta_text = meta_tag.get('content').strip()
        # 全角文字を2文字にカウント
        meta_text_z2h = zenhan.z2h(meta_text, mode=2, ignore=())

        if len(meta_text_z2h) >= 70 and len(meta_text_z2h) <= 155:
            # 文字数が70~155文字の場合は満点
            score += 10
        elif len(meta_text_z2h) > 155:
            # 文字数が155文字より多い場合は5点
            score += 5
        else:
            # 文字数が70文字未満の場合は0点
            score += 0

    # 3. HTTPS（エンドツーエンド暗号化通信）の使用 (10点)
    if url.startswith('https://'):
        score += 10

    # 4. ヘッダータグ<h1>が適切に設定されている (10点)
    h1_tags = soup.find_all('h1')
    if h1_tags is None:
        # ヘッダータグ<h1>が存在しない場合は0点
        score += 0
    else:
        # メタ説明タグが存在する場合は文字数をチェック
        h1_text = h1_tags[0].text.strip()
        # 全角文字を2文字にカウント
        h1_text_z2h = zenhan.z2h(h1_text, mode=2, ignore=())

        if len(h1_text_z2h) >= 5 and len(h1_text_z2h) <= 60:
            # 文字数が5~60文字の場合は満点
            score += 10
        elif len(h1_text_z2h) > 60:
            # 文字数が60文字より多い場合は5点
            score += 5
        else:
            # 文字数が5文字未満の場合は0点
            score += 0

    # 5. バリアフリーのため画像に alt （短い要約）が適切に付与されているかのチェック）(10点)
    img_tags = soup.find_all('img')
    # 画像が存在しなければ 10点（減点なし）
    if not img_tags:
        score += 10
    else:
        alt_counts = 0
        for img_tag in img_tags:
            if not img_tag.has_attr('alt') or len(zenhan.z2h(img_tag['alt'], mode=2, ignore=())) < 2:
                alt_counts += 0
            else:
                alt_counts += 1
        # 画像の数がalt_countsと同じ（全部に2文字以上のaltがあれば）10点
        if alt_counts == len(img_tags):
            score += 10
        # altのない画像があれば0点
        else:
            score += 0

    # 6. モバイルポンシブ対応 (10点)
    # （完璧に書くとかなり面倒なのでmeta_viewportタグがあって、device-widthが指定されていれば対応とみなす）
    meta_viewport = soup.find('meta', attrs={'name': 'viewport'})
    if meta_viewport or 'width=device-width' in meta_viewport.get('content', ''):
        score += 10
    else:
        score += 0

    # 7. ページスピード (20点)
    desktop_url = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=desktop'
    mobile_url = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile'
    desktop_response = requests.get(desktop_url)
    mobile_response = requests.get(mobile_url)
    desktop_speed = desktop_response.json()['lighthouseResult']['categories']['performance']['score']
    mobile_speed = mobile_response.json()['lighthouseResult']['categories']['performance']['score']
    if desktop_speed >= 0.9:
        score += 10
    if mobile_speed >= 0.9:
        score += 10

    # 8. コンテンツの長さ (5点)
    main_content = soup.find('main')
    main_content_text_z2h = zenhan.z2h(main_content.text, mode=2, ignore=())
    if len(main_content_text_z2h) >= 300:
        score += 10

    # 9. インバウンドリンクのチェック (20点)
    # 入力されたurlからドメインを抽出する
    domain = urlparse(url).netloc  
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    res = requests.get(f"https://www.google.com/search?q=site:{domain}+link:{url}", headers=headers)
    soup_res = BeautifulSoup(res.text, 'html.parser')
    result_stats = soup_res.find("div", {"id": "result-stats"}).get_text()
    count = int(result_stats.split()[1].replace(",", ""))
    if count < 10:
        score += 0
    elif count < 50:
        score += 5
    elif count < 100:
        score += 10
    elif count < 200:
        score += 15
    else:
        score += 20

    # 10. ソーシャルメディア連携 (5点)
    """
    try cach 分で先に以下を試す。
    startswith() メソッドは、文字列（str 型）の先頭が指定した文字列で始まる場合に True を返すメソッドです。例えば、"http://www.example.com"という文字列に対して startswith('http') を呼び出すと、Trueが返ります。

    しかしながら、今回のエラーは 'NoneType' object has no attribute 'startswith' と出ていますので、startswith()メソッドが None型の変数に対して呼び出されたためにエラーが発生しているということです。具体的には、link.get('href')が Noneを返したことが原因の可能性があります。

    このエラーを回避するために、hrefがNoneの場合は startswith() メソッドを呼び出す前に、if文でチェックを行い、hrefが存在する場合のみ startswith() メソッドを呼び出すようにすることが必要です。
    """
    social_links = soup.find_all('a', href=lambda href: href.startswith('https://twitter.com/') or href.startswith('https://www.facebook.com/'))
    if not href or not social_links or len(social_links) < 2:
        score += 0
    else:
        score +=5

    return (score / 100) * 100  # return score as percentage

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("URLを指定してください")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("引数の数が正しくありません")
        sys.exit(1)

    url = sys.argv[1]
    check_seo_criteria(url)