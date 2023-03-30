import requests
import sys
import zenhan
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def check_seo_criteria(url):

    response = requests.get(url)

    # ステータスコードが200以外の場合はエラーメッセージを表示して終了
    if response.status_code != 200:
        print(f"ステータスコード {response.status_code} . ウェブサイトへのアクセスに失敗しました。URLをご確認の上、再度お試しください。")
        return False

    soup = BeautifulSoup(response.content, 'html.parser')

    # 変数scoreを初期化
    score = 0

    print("1. タイトルタグが適切な長さである。(10点)")
    # タイトルタグの取得
    title_tag = soup.title
    if title_tag is None:
        print("タイトルタグが存在しない -0点")
        score += 0
    else:
        print("タイトルタグが存在する場合は文字数をチェック")
        title_text = title_tag.text.strip()
        print("全角文字を2文字にカウント")
        title_text_z2h = zenhan.z2h(title_text, mode=2, ignore=())
        if len(title_text_z2h) >= 30 and len(title_text_z2h) <= 60:
            print("文字数が30~60文字（適切な長さ）の場合 +10点")
            score += 10
        elif len(title_text_z2h) > 60:
            print("文字数が60文字より多い（長すぎ）場合 +5点")
            score += 5
        else:
            print("文字数が30文字未満（短すぎ）の場合 +0点")
            score += 0
    
    print(f"現在のスコア : {score}/100")

    print("2. メタ情報が適切な長さに設定されている (10点)")
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag is None:
        print("メタ説明タグが存在しない場合 +0点")
        score += 0
    else:
        print("メタ説明タグが存在する場合は文字数をチェック")
        meta_text = meta_tag.get('content').strip()
        print("全角文字を2文字にカウント")
        meta_text_z2h = zenhan.z2h(meta_text, mode=2, ignore=())

        if len(meta_text_z2h) >= 70 and len(meta_text_z2h) <= 155:
            print("文字数が70~155文字（適切な長さ）の場合 +10点")
            score += 10
        elif len(meta_text_z2h) > 155:
            print("文字数が155文字より多い（長すぎ）場合 +5点")
            score += 5
        else:
            print("文字数が70文字未満（短すぎ）の場合 +0点")
            score += 0
    print(f"現在のスコア : {score}/100")


    print("3. HTTPS（エンドツーエンド暗号化通信）の使用 (10点)")
    if url.startswith('https://'):
        print("https:// で暗号化通信している +10点")
        score += 10
    else:
        print("https:// で暗号化通信していなけい +0点")

    print(f"現在のスコア : {score}/100")

    print("4. ヘッダータグ<h1>が適切に設定されている (10点)")
    h1_tags = soup.find_all('h1')
    if h1_tags is None:
       print("ヘッダータグ<h1>が存在しない場合は +0点")
       score += 0
    elif not h1_tags:
        print("設定されたヘッダータグが空の場合は +0点")
        score += 0
    else:
        print("メタ説明タグが存在する場合は文字数をチェック")
        h1_text = h1_tags[0].text.strip()
        print("全角文字を2文字にカウント")
        h1_text_z2h = zenhan.z2h(h1_text, mode=2, ignore=())
        if len(h1_text_z2h) >= 5 and len(h1_text_z2h) <= 60:
            print( "文字数が5~60文字（適切な長さ）の場合 +10点")
            score += 10
        elif len(h1_text_z2h) > 60:
            print("文字数が60文字より多い（長すぎ）場合 +5点")
            score += 5
        else:
            print("文字数が5文字未満（短すぎ）の場合 +0点")
            score += 0
    print(f"現在のスコア : {score}/100")

    print("5. 画像に alt （バリアフリーのための短い要約）が適切に付与されているかのチェック(10点)")
    img_tags = soup.find_all('img')
    if not img_tags:
        print("そもそもページに画像が存在しない +10点（減点なし）")
        score += 10
    else:
        alt_counts = 0
        for img_tag in img_tags:
            if not img_tag.has_attr('alt') or len(zenhan.z2h(img_tag['alt'], mode=2, ignore=())) < 2:
                alt_counts += 0
            else:
                alt_counts += 1
        if alt_counts == len(img_tags):
            print("画像すべてに2文字以上のaltがある +10点")
            score += 10
        else:
            print("altのない画像がある +0点")
            score += 0
    print(f"現在のスコア : {score}/100")

    print("6. モバイルポンシブ対応 (10点)")
    # （完璧に書くとかなり面倒なのでmeta_viewportタグがあって、device-widthが指定されていれば対応とみなす）
    meta_viewport = soup.find('meta', attrs={'name': 'viewport'})
    if meta_viewport:
        if 'width=device-width' in meta_viewport.get('content', ''):
            print("meta_viewportタグがあり、なおかつdevice-widthが指定されている +10点")
            score += 10
    else:
        print("meta_viewportタグがない、またはdevice-widthが指定されていない +0点")
        score += 0
    print(f"現在のスコア : {score}/100")


    print("7. ページスピード (20点)")
    desktop_url = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=desktop'
    mobile_url = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile'
    desktop_response = requests.get(desktop_url)
    mobile_response = requests.get(mobile_url)
    try:
        desktop_speed = desktop_response.json()['lighthouseResult']['categories']['performance']['score']
        if desktop_speed >= 0.9:
            print("デスクトップスピード合格 +10点")
            score += 10
        else:
            print("デスクトップスピード不合格 +0点")
    except KeyError:
        print("デスクトップスピード情報がない +0点")
        score += 0
    try:
        mobile_speed = mobile_response.json()['lighthouseResult']['categories']['performance']['score']
        if mobile_speed >= 0.9:
            print("モバイルスピード合格 +10点")
            score += 10
        else:
            print("モバイルスピード不合格 +0点")
    except KeyError:
        print("モバイルスピード情報がない +0点")
        score += 0
    print(f"現在のスコア {score}/100")

    print("8. コンテンツの長さ (10点)")
    main_content = soup.find('main')

    print("メインコンテンツが存在する場合は文字数をチェック")
    if main_content: 
        print("全角文字を2文字にカウント")
        main_content_text_z2h = zenhan.z2h(main_content.text, mode=2, ignore=())
        if len(main_content_text_z2h) >= 300:
            print("コンテンツが300文字以上（適切な長さ）の場合 +10点")
            score += 10
    else:
        print("コンテンツがない、または300文字未満短すぎる場合 +0点")

    print(f"現在のスコア : {score}/100")

    print("9. インバウンドリンクのチェック (20点)")
    print("入力されたurlからドメインを抽出する")
    domain = urlparse(url).netloc  
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    res = requests.get(f"https://www.google.com/search?q=site:{domain}+link:{url}", headers=headers)
    soup_res = BeautifulSoup(res.text, 'html.parser')
    result_stats = soup_res.find("div", {"id": "result-stats"}).get_text()
    print(result_stats)
    count = int(result_stats.split()[1].replace(",", ""))
    if count < 10:
        print("有効なインバウンドリンクが 10 未満 +0点")
        score += 0
    elif count < 50:
        print("有効なインバウンドリンクが 50 未満 +5点")
        score += 5
    elif count < 100:
        print("有効なインバウンドリンクが 100 未満 +10点")
        score += 10
    elif count < 200:
        print("有効なインバウンドリンクが 200 未満 +15点")
        score += 15
    else:
        print("有効なインバウンドリンクが 200 以上 +20点")
        score += 20
    print(f"現在のスコア : {score}/100")

    print("10. ソーシャルメディア連携 (5点)")
    social_links = soup.find_all('a')
    count_snslink = 0
    for link in social_links:
        href = link.get('href')
        if href and (href.startswith('https://twitter.com/') or href.startswith('https://www.facebook.com/')):
            count_snslink +=1
    if count_snslink > 0:
        print("Twitter または Facebook へのリンクが1つ以上存在する +5点")
        score += 5
    else:
        print("Twitter または Facebook へのリンクがない +0点")
        score += 0

    print(f"現在のスコア : {score}/100")

    return (score / 100) * 100  # return score as percentage

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("URLを指定してください")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("引数の数が正しくありません")
        sys.exit(1)

    url = sys.argv[1]
    result_score = check_seo_criteria(url)
    print ("URLのウェブページのSEO対策評価採点、")
    print (f"リザルト : {result_score}点 / 100点満点中")
    print ("※ 注意1: この startingbasics プログラムによる診断でわかるのは、SEO対策の基礎の基礎が出来ているかだけです。たとえこの診断で100点満点が出たとしても、SEO対策が完璧であることにはなりません。素晴らしいサイトを作るのは、そこからが始まりです。逆に、この診断で100点満点がでなかったサイトは、基礎的な部分に問題があります。出力をよく読んで、減点された項目に合致するようにページを修正して、最低限この診断で100点満点がでるようにましょう。")
    print ("※ 注意2: Google検索のスコアリング基準は日々変化します。このプログラムが有効である期間は短いでしょう。このプログラムを有効なものとするには、日々のメンテナンスが必要です。プロトタイプである現バージョンでは、各採点基準が関数化されていませんが、メンテナンス性のためには、各採点プロセスを関数化して、配点を変えられるようにする改修が必要となるでしょう。")