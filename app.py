import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. ページ基本設定 & 高度なデザイン設定 ---
st.set_page_config(page_title="Naenara Monitor JP", page_icon="🌐", layout="wide")

# カスタムCSSで「報道機関のダッシュボード」風に
st.markdown("""
    <style>
    /* 背景とフォント */
    .main { background-color: #f4f4f2; color: #1a1a1a; }
    
    /* ニュースカードのデザイン */
    .news-container {
        background-color: white;
        padding: 25px;
        border-radius: 2px;
        border-bottom: 3px solid #cc0000; /* 北朝鮮カラーのアクセント */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        transition: transform 0.2s;
    }
    .news-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .news-title {
        font-size: 1.4rem !important;
        font-weight: bold !important;
        color: #1a1a1a !important;
        text-decoration: none !important;
        line-height: 1.3;
    }
    .news-meta {
        color: #666;
        font-size: 0.85rem;
        margin-top: 10px;
    }
    /* ボタンデザイン */
    .stButton>button {
        background-color: #1a1a1a;
        color: white;
        border-radius: 0;
        border: none;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #cc0000;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. データ取得ロジック ---
def fetch_naenara_data():
    """ネナラからニュース記事のリストを取得する"""
    url = "http://www.naenara.com.kp/index.php?lang=jp"
    try:
        res = requests.get(url, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        articles = []
        # ネナラの日本語版トップページからリンクとタイトルを抽出
        links = soup.find_all('a', href=True)
        for l in links:
            title = l.get_text().strip()
            # 記事タイトルと思われる長さとURLパターンでフィルタリング
            if len(title) > 18 and "page=" in l['href']:
                full_url = "http://www.naenara.com.kp/" + l['href']
                # 重複排除
                if not any(a['url'] == full_url for a in articles):
                    articles.append({
                        "title": title,
                        "url": full_url
                    })
        return articles
    except Exception as e:
        st.error(f"接続エラーが発生しました: {e}")
        return []

# --- 3. メインレイアウト ---
st.title("🌐 Naenara Monitor")
st.markdown("### 朝鮮民主主義人民共和国 公式ポータル速報")
st.write("---")

# サイドバー設定
with st.sidebar:
    st.header("📋 メニュー")
    st.write("このサイトは『ネナラ』の日本語情報を自動収集するアーカイブサイトです。")
    if st.button("🔄 最新情報に更新"):
        st.cache_data.clear()
        st.rerun()
    st.write("---")
    st.caption("※情報の真偽については一次ソースをご確認ください。")

# 記事の取得と表示
with st.spinner("最新の記事を読み込み中..."):
    news_list = fetch_naenara_data()

if news_list:
    # 2カラムで表示して専門サイト感を出す
    col1, col2 = st.columns(2)
    
    for i, article in enumerate(news_list):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.markdown(f"""
            <div class="news-container">
                <a href="{article['url']}" target="_blank" class="news-title">{article['title']}</a>
                <div class="news-meta">
                    ソース: Naenara (日本語版) <br>
                    区分: 公式発表・ニュース
                </div>
            </div>
            """, unsafe_allow_html=True)
            # 詳細確認ボタン（リンクへ飛ばす）
            st.link_button("記事原文を読む ↗", article['url'])
else:
    st.warning("現在、記事を取得できません。北朝鮮側のサーバーがダウンしている可能性があります。")
