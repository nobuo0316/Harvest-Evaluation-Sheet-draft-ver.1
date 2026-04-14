import streamlit as st
import pandas as pd

st.set_page_config(page_title="情報媒体 比較表", page_icon="📊", layout="wide")

# -----------------------------
# Data
# -----------------------------
media_data = [
    {
        "情報媒体名": "日経GX",
        "サイト名": "日経GX - 脱炭素時代における変革のヒントを伝える",
        "サイトURL": "https://project.nikkeibp.co.jp/gx/",
        "金額": "法人1人 45,606円/年",
        "比較基準": "（新エネルギー新聞 21,450円/年）",
        "媒体": "メール / アプリ / サイト",
        "主な特長": "テクノロジー・市場・政策を幅広く掲載 / 記者取材あり / サイト内検索あり / ランキングあり / 独自記事あり / 記事保存可 / 複数媒体で読める",
        "懸念点": "バイオ系のタグ付けなし（ただし検索可能） / 新エネルギー新聞より高額",
        "おすすめ度": "◎",
        "向いている使い方": "幅広い業界動向の把握、保存・共有、検索ベースの情報収集",
    },
    {
        "情報媒体名": "グリーンプロダクション",
        "サイト名": "株式会社グリーンプロダクション",
        "サイトURL": "https://greenproduction.co.jp/",
        "金額": "無料",
        "比較基準": "（新エネルギー新聞 21,450円/年）",
        "媒体": "ウェブサイトのみ",
        "主な特長": "G&B（グリーン・バイオ）分野に注力 / バイオ燃料のみ見やすい / 更新頻度は約3日に1件 / 参考URL記載あり / 展示会・イベント情報あり / 海外記事多め / 無料",
        "懸念点": "今日更新分の一覧がない / 企業・団体から掲載希望可能 / サイト内検索なし",
        "おすすめ度": "◎",
        "向いている使い方": "バイオ燃料分野を絞って追う、海外トピック確認、無料の補完情報源",
    },
    {
        "情報媒体名": "環境新聞",
        "サイト名": "環境新聞オンライン",
        "サイトURL": "https://www.kankyo-news.co.jp/",
        "金額": "オンラインのみ 26,400円/年 / 紙面付き 34,980円/年",
        "比較基準": "（新エネルギー新聞 21,450円/年）",
        "媒体": "サイト / 紙",
        "主な特長": "大判で通常6～12ページ / 月4回発行（毎週水曜） / サイト内検索あり / 日付・期間指定可 / 補助金や業務委託など公共情報あり / PDFで紙面アーカイブ確認可",
        "懸念点": "新エネルギー新聞より高い / 紙面追加で年8,580円増 / 『脱炭素・エネルギー』中心で関連の薄い情報も混ざる",
        "おすすめ度": "○",
        "向いている使い方": "紙面やPDFで一覧性を重視したい場合、公共案件情報も追いたい場合",
    },
]

comparison_df = pd.DataFrame(media_data)

# URLをクリック可能にするため表示用列を追加
comparison_df_display = comparison_df.copy()
comparison_df_display["サイト"] = comparison_df_display.apply(
    lambda row: f'<a href="{row["サイトURL"]}" target="_blank">{row["サイト名"]}</a>', axis=1
)
comparison_df_display = comparison_df_display[
    [
        "情報媒体名",
        "サイト",
        "金額",
        "媒体",
        "おすすめ度",
        "向いている使い方",
        "主な特長",
        "懸念点",
    ]
]

# -----------------------------
# Header
# -----------------------------
st.title("情報媒体 比較表")
st.caption("バイオマス事業の情報収集向けに、候補媒体を一目で比較できる表です。")

# -----------------------------
# Summary boxes
# -----------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("有料媒体数", "2")
with col2:
    st.metric("無料媒体数", "1")
with col3:
    st.metric("推奨構成", "日経GX + グリーンプロダクション")

st.markdown("---")

# -----------------------------
# Filters
# -----------------------------
left, right = st.columns([1, 2])
with left:
    selected_media = st.multiselect(
        "表示する媒体を選択",
        options=comparison_df["情報媒体名"].tolist(),
        default=comparison_df["情報媒体名"].tolist(),
    )

with right:
    keyword = st.text_input("キーワード検索（特長・懸念点・使い方）", placeholder="例：検索、海外、無料、PDF")

filtered_df = comparison_df.copy()
filtered_df = filtered_df[filtered_df["情報媒体名"].isin(selected_media)]

if keyword:
    mask = filtered_df.apply(
        lambda row: row.astype(str).str.contains(keyword, case=False, na=False).any(), axis=1
    )
    filtered_df = filtered_df[mask]

filtered_display = filtered_df.copy()
filtered_display["サイト"] = filtered_display.apply(
    lambda row: f'<a href="{row["サイトURL"]}" target="_blank">{row["サイト名"]}</a>', axis=1
)
filtered_display = filtered_display[
    [
        "情報媒体名",
        "サイト",
        "金額",
        "媒体",
        "おすすめ度",
        "向いている使い方",
        "主な特長",
        "懸念点",
    ]
]

# -----------------------------
# Table
# -----------------------------
st.subheader("比較一覧")
st.markdown(
    filtered_display.to_html(escape=False, index=False),
    unsafe_allow_html=True,
)

st.info("媒体名の比較だけでなく、サイト名クリックでそのまま対象サイトへ移動できます。")

# -----------------------------
# Conclusion
# -----------------------------
st.subheader("結論")
st.markdown(
    """
**『日経GX』と『グリーンプロダクション』の併用が適している** と考えられます。

**理由**
- **日経GX**：記事数が多く、サイト内検索や保存機能があり、情報の深さと使いやすさに優れる。
- **グリーンプロダクション**：無料で、バイオ燃料系や海外トピックを補完しやすい。
- **環境新聞**：紙面・PDFの一覧性は魅力だが、費用と情報の広さの面で優先度は一段下がる。

**検索結果メモ**
- 「バイオマス発電」で1年分検索した場合：
    - 環境新聞：19件
    - 日経GX：31件

**主な懸念点**
- 日経GXは **45,606円/年** と、新エネルギー新聞 **21,450円/年** の約2.13倍。
- 日経GX・グリーンプロダクションともに、紙面やPDFのような一覧性は弱く、記事ごとの確認が必要。
"""
)

# -----------------------------
# Raw data expander
# -----------------------------
with st.expander("元データを確認"):
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("必要であれば次に、①稟議用の見た目に寄せる版 ②価格比較を色分けした版 ③スマホでも見やすいカード版 に変更できます。")
