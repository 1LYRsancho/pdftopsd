import io
import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

st.set_page_config(page_title="PDF to PSD Converter", page_icon="📄")

st.title("📄 PDF to Layered PSD Converter")
st.write("PDFの全ページを1枚ずつ個別レイヤーにした1つのPSDファイルを生成します。")

# 1. ファイルアップローダー
uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type=["pdf"])

# 2. 解像度（DPI）設定
dpi = st.selectbox(
    "解像度 (DPI)",
    options=[72, 150, 300],
    index=1,
    help="数値が高いほど高画質になりますが、生成時間とファイルサイズが大きくなります。"
)

if uploaded_file is not None:
    if st.button("PSDに変換して生成", type="primary"):
        with st.spinner("PDFページを分解・レンダリング中..."):
            try:
                # PDFを画像リストに変換 (PIL Imageのリスト)
                pdf_bytes = uploaded_file.read()
                images = convert_from_bytes(pdf_bytes, dpi=dpi)
                
                total_pages = len(images)
                st.info(f"全 {total_pages} ページの処理を開始します。")

                progress_bar = st.progress(0)
                
                # 1ページ目のサイズとモードを基準にして空のPSDを作成 (.new() を使用)
                first_img = images[0].convert('RGB')
                width, height = first_img.size
                
                # PSDオブジェクトを構築
                psd = PSDImage.new(mode='RGB', size=(width, height))

                # ページごとにレイヤーを作成して追加
                for idx, img in enumerate(images):
                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    # PixelLayer を追加
                    layer = PixelLayer.fromimage(img)
                    layer.name = f"Page {idx + 1}"
                    psd.append(layer)

                    # 進捗更新
                    progress_bar.progress((idx + 1) / total_pages)

                # PSDをバイナリ（BytesIO）に保存
                psd_buffer = io.BytesIO()
                psd.save(psd_buffer)
                psd_buffer.seek(0)

                st.success("PSDファイルの作成が完了しました！")

                # ダウンロードボタンを表示
                output_filename = uploaded_file.name.rsplit(".", 1)[0] + "_layered.psd"
                st.download_button(
                    label="PSDファイルをダウンロード",
                    data=psd_buffer,
                    file_name=output_filename,
                    mime="image/vnd.adobe.photoshop"
                )

            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
