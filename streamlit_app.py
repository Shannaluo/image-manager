# streamlit_app.py
import os
import pandas as pd
import streamlit as st
from PIL import Image

# === 配置 ===
IMAGE_DIR = "E:/precedents"
CSV_PATH = os.path.join(IMAGE_DIR, "image_tags.csv")

st.set_page_config(page_title="图像资料库", layout="wide")

st.title("🏷️ 项目图像检索界面（标签自动识别）")

# === 加载标签数据 ===
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    df["tags"] = df["tags"].fillna("").astype(str)
    return df

df = load_data()
all_tags = sorted({tag for tags in df["tags"] for tag in tags.split(";") if tag.strip()})

# === 筛选控件 ===
with st.sidebar:
    st.header("🔍 搜索条件")
    selected_tags = st.multiselect("请选择标签", all_tags)
    st.markdown("💡 多选表示“包含任意一个标签”")

# === 筛选结果 ===
if selected_tags:
    filtered_df = df[df["tags"].apply(lambda x: any(tag in x for tag in selected_tags))]
else:
    filtered_df = df

st.write(f"共找到 {len(filtered_df)} 张图片")

# === 图片展示 ===
cols = st.columns(4)
for i, row in enumerate(filtered_df.itertuples()):
    with cols[i % 4]:
        img_path = os.path.join(IMAGE_DIR, row.relative_path)
        try:
            image = Image.open(img_path)
            st.image(image, caption=f"{row.project}\n📎 标签: {row.tags}", use_column_width=True)
            with st.expander("📁 查看路径"):
                st.code(img_path)
        except:
            st.warning(f"无法打开图片：{img_path}")


