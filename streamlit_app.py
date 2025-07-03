import pandas as pd
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from pathlib import Path
import os

# === 加载 .env 配置 ===
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# === 配置路径 ===
IMAGE_DIR = Path(os.getenv("IMAGE_DIR", "."))
CSV_PATH = IMAGE_DIR / os.getenv("TAG_FILE", "image_tags.csv")

st.set_page_config(page_title="图像资料库", layout="wide")
st.title("🏷️ 项目图像检索界面（标签自动识别）")

# === 加载标签数据 ===
@st.cache_data
def load_data():
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        df["tags"] = df["tags"].fillna("").astype(str)
        if "tag_source" not in df.columns:
            df["tag_source"] = "ai"
    else:
        df = pd.DataFrame(columns=["project", "filename", "relative_path", "tags", "tag_source"])
    return df

df = load_data()
existing_paths = set(df["relative_path"].tolist())

# === 扫描新图片并添加标签（仅处理新增） ===
def scan_new_images():
    new_rows = []
    for project_folder in IMAGE_DIR.iterdir():
        if not project_folder.is_dir():
            continue
        project = project_folder.name
        for image_path in sorted(project_folder.glob("*")):
            if not image_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                continue
            rel_path = f"{project}/{image_path.name}"
            if rel_path in existing_paths:
                continue
            new_rows.append({
                "project": project,
                "filename": image_path.name,
                "relative_path": rel_path,
                "tags": "",
                "tag_source": "ai"
            })
    if new_rows:
        new_df = pd.DataFrame(new_rows)
        full_df = pd.concat([df, new_df], ignore_index=True)
        full_df.to_csv(CSV_PATH, index=False)
        st.success(f"已新增 {len(new_rows)} 张图片，请为它们添加标签。")
        st.rerun()

scan_new_images()

# === 获取所有标签 ===
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

# === 图片展示与标签编辑 ===
cols = st.columns(4)
for i, row in enumerate(filtered_df.itertuples()):
    with cols[i % 4]:
        img_path = IMAGE_DIR / row.relative_path
        try:
            image = Image.open(img_path)
            st.image(image, caption=f"{row.project}\n📎 标签: {row.tags}", use_container_width=True)
            with st.expander("📁 查看路径"):
                st.code(img_path.as_posix())
            with st.expander("✏️ 编辑标签"):
                new_tags = st.text_input("输入标签（分号分隔）", value=row.tags, key=row.relative_path)
                if new_tags != row.tags:
                    df.loc[df["relative_path"] == row.relative_path, "tags"] = new_tags
                    df.loc[df["relative_path"] == row.relative_path, "tag_source"] = "manual"
                    df.to_csv(CSV_PATH, index=False)
                    st.success("标签已更新！")
        except Exception as e:
            st.warning(f"无法打开图片：{img_path}, 错误：{e}")
