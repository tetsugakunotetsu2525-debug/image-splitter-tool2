import streamlit as st
from PIL import Image
from io import BytesIO
import random
import zipfile

st.set_page_config(page_title="画像ツール", layout="wide")

col1, col2 = st.columns([0.08, 0.92])
with col1:
    try:
        logo = Image.open("logo.jpg")
        logo_resized = logo.resize((40, 40), Image.Resampling.LANCZOS)
        st.image(logo_resized, width=40)
    except:
        pass
with col2:
    st.title("📸 画像ツール")

if 'saved_side_images' not in st.session_state:
    st.session_state.saved_side_images = []

tab1, tab2, tab3 = st.tabs(["4分割のみ", "合成", "ワンステップ"])

def crop_to_16_9(img):
    img_obj = Image.open(BytesIO(img)) if isinstance(img, bytes) else img
    target_ratio = 16 / 9
    current_ratio = img_obj.width / img_obj.height
    
    if current_ratio > target_ratio:
        new_width = int(img_obj.height * target_ratio)
        left = (img_obj.width - new_width) // 2
        right = left + new_width
        img_cropped = img_obj.crop((left, 0, right, img_obj.height))
    else:
        new_height = int(img_obj.width / target_ratio)
        top = (img_obj.height - new_height) // 2
        bottom = top + new_height
        img_cropped = img_obj.crop((0, top, img_obj.width, bottom))
    
    return img_cropped

def split_4(img_cropped):
    crop_width, crop_height = img_cropped.size
    center_x = crop_width // 2
    center_y = crop_height // 2
    
    return [
        img_cropped.crop((0, 0, center_x, center_y)),
        img_cropped.crop((center_x, 0, crop_width, center_y)),
        img_cropped.crop((0, center_y, center_x, crop_height)),
        img_cropped.crop((center_x, center_y, crop_width, crop_height))
    ], crop_width, crop_height

def resize_to_split_size(img, target_width, target_height):
    if target_height <= 0:
        target_height = 1
    
    target_ratio = target_width / target_height
    current_ratio = img.width / img.height
    
    if current_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        right = left + new_width
        img_cropped = img.crop((left, 0, right, img.height))
    else:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        bottom = top + new_height
        img_cropped = img.crop((0, top, img.width, bottom))
    
    result_img = img_cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
    return result_img

def create_zip(images):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, img in enumerate(images):
            buf = BytesIO()
            img.save(buf, format='PNG')
            zipf.writestr(f'{i+1}.png', buf.getvalue())
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def generate_heights(side_height):
    total_side_height = side_height * 2
    min_h = max(1, int(total_side_height * 0.2))
    max_h = int(total_side_height * 0.8)
    
    patterns = []
    for _ in range(4):
        top_ratio = random.uniform(0.3, 0.7)
        patterns.append(top_ratio)
    
    random.shuffle(patterns)
    
    h1 = int(total_side_height * patterns[0])
    h1 = max(1, min(h1, total_side_height - 1))
    h2 = total_side_height - h1
    
    h3 = int(total_side_height * patterns[1])
    h3 = max(min_h, min(h3, max_h))
    
    h4 = total_side_height - h3
    h4 = max(min_h, min(h4, max_h))
    
    return h1, h2, h3, h4

# ===== タブ2：合成 =====
with tab2:
    st.subheader("4分割済みメイン画像4枚の上下に各2枚ずつ追加")
    
    st.write("**4分割済みのメイン画像4枚をアップロード**")
    main_files = st.file_uploader("メイン画像（4分割済み）", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], accept_multiple_files=True, key="main_composite")
    
    st.write("---")
    
    if len(st.session_state.saved_side_images) > 0:
        st.write(f"✓ 前回保存した上下用画像: {len(st.session_state.saved_side_images)}枚")
        
        use_saved = st.radio(
            "上下用画像の選択",
            ["前回の画像を使用", "新しい画像をアップロード"],
            key="radio_composite"
        )
        
        if use_saved == "新しい画像をアップロード":
            st.write("**新しい上下用画像をアップロード（4枚、不足時はランダム補充）**")
            side_files = st.file_uploader("上下用画像", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], accept_multiple_files=True, key="sides_composite")
            if len(side_files) > 0:
                st.session_state.saved_side_images = [Image.open(f) for f in side_files]
                if 'comp_sides' in st.session_state:
                    del st.session_state.comp_sides
                if 'comp_image_buffers' in st.session_state:
                    del st.session_state.comp_image_buffers
                if 'comp_heights' in st.session_state:
                    del st.session_state.comp_heights
                st.success(f"✓ {len(side_files)}枚の画像を保存しました")
    else:
        st.write("**上下用画像をアップロード（4枚、不足時はランダム補充）**")
        side_files = st.file_uploader("上下用画像", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], accept_multiple_files=True, key="sides_composite")
        if len(side_files) > 0:
            st.session_state.saved_side_images = [Image.open(f) for f in side_files]
            if 'comp_sides' in st.session_state:
                del st.session_state.comp_sides
            if 'comp_image_buffers' in st.session_state:
                del st.session_state.comp_image_buffers
            if 'comp_heights' in st.session_state:
                del st.session_state.comp_heights
            st.success(f"✓ {len(side_files)}枚の画像を保存しました")
    
    if main_files and len(main_files) == 4 and len(st.session_state.saved_side_images) > 0:
        
        split_images = [Image.open(f) for f in main_files]
        
        split_width = split_images[0].width
        split_height = split_images[0].height
        
        st.write(f"**メイン画像サイズ:** {split_width} × {split_height}")
        
        needed = 4
        final_sides = st.session_state.saved_side_images.copy()
        
        if len(final_sides) < needed:
            shortage = needed - len(final_sides)
            for _ in range(shortage):
                final_sides.append(random.choice(st.session_state.saved_side_images))
        
        if 'comp_heights' not in st.session_state:
            st.session_state.comp_heights = {}
        
        if 'comp_sides' not in st.session_state:
            st.session_state.comp_sides = {}
            for idx in range(4):
                shuffled = final_sides.copy()
                random.shuffle(shuffled)
                st.session_state.comp_sides[idx] = shuffled
        
        final_images = []
        
        for idx, split_img in enumerate(split_images):
            shuffled_sides = st.session_state.comp_sides[idx]
            
            if idx not in st.session_state.comp_heights:
                st.session_state.comp_heights[idx] = generate_heights(split_height)
            
            h1, h2, h3, h4 = st.session_state.comp_heights[idx]
            
            top_img1 = resize_to_split_size(shuffled_sides[0].copy(), split_width, h1)
            top_img2 = resize_to_split_size(shuffled_sides[1].copy(), split_width, h2)
            bottom_img1 = resize_to_split_size(shuffled_sides[2].copy(), split_width, h3)
            bottom_img2 = resize_to_split_size(shuffled_sides[3].copy(), split_width, h4)
            
            total_height = h1 + h2 + split_height + h3 + h4
            combined = Image.new('RGB', (split_width, total_height))
            
            y_offset = 0
            combined.paste(top_img1, (0, y_offset))
            y_offset += h1
            
            combined.paste(top_img2, (0, y_offset))
            y_offset += h2
            
            combined.paste(split_img, (0, y_offset))
            y_offset += split_height
            
            combined.paste(bottom_img1, (0, y_offset))
            y_offset += h3
            
            combined.paste(bottom_img2, (0, y_offset))
            
            final_images.append(combined)
        
        if 'comp_image_buffers' not in st.session_state:
            st.session_state.comp_image_buffers = {}
            for i, img in enumerate(final_images):
                buf = BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)
                st.session_state.comp_image_buffers[i] = buf.getvalue()
        
        st.subheader("プレビュー")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.image(final_images[0], width=150)
        with col2:
            st.image(final_images[1], width=150)
        with col3:
            st.image(final_images[2], width=150)
        with col4:
            st.image(final_images[3], width=150)
        
        st.subheader("ダウンロード")
        
        zip_data = create_zip(final_images)
        st.download_button(
            label="📦 ZIP一括ダウンロード",
            data=zip_data,
            file_name="合成画像.zip",
            mime="application/zip",
            key="comp_zip"
        )
        
        st.write("**個別ダウンロード**")
        col1, col2, col3, col4 = st.columns(4, gap="small")
        with col1:
            st.download_button("1.png", st.session_state.comp_image_buffers[0], "1.png", "image/png", key="comp_1", use_container_width=True)
        with col2:
            st.download_button("2.png", st.session_state.comp_image_buffers[1], "2.png", "image/png", key="comp_2", use_container_width=True)
        with col3:
            st.download_button("3.png", st.session_state.comp_image_buffers[2], "3.png", "image/png", key="comp_3", use_container_width=True)
        with col4:
            st.download_button("4.png", st.session_state.comp_image_buffers[3], "4.png", "image/png", key="comp_4", use_container_width=True)
    
    elif main_files and len(main_files) != 4:
        st.error(f"❌ 4分割済み画像は**ちょうど4枚**必要です（現在{len(main_files)}枚）")
    else:
        st.info("👆 4分割済みメイン画像4枚と上下用画像をアップロードしてください")

# ===== タブ1：4分割のみ =====
with tab1:
    st.subheader("画像を16:9にして4分割")
    
    uploaded_file = st.file_uploader("画像をアップロード", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], key="split_only")
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        original_width, original_height = img.size
        
        st.write(f"**元のサイズ:** {original_width} × {original_height}")
        
        img_cropped = crop_to_16_9(img)
        crop_width, crop_height = img_cropped.size
        st.write(f"**16:9トリミング後:** {crop_width} × {crop_height}")
        
        split_images, cw, ch = split_4(img_cropped)
        
        st.subheader("プレビュー")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.image(split_images[0], width=150)
        with col2:
            st.image(split_images[1], width=150)
        with col3:
            st.image(split_images[2], width=150)
        with col4:
            st.image(split_images[3], width=150)
        
        st.subheader("ダウンロード")
        
        zip_data = create_zip(split_images)
        st.download_button(
            label="📦 ZIP一括ダウンロード",
            data=zip_data,
            file_name="分割画像.zip",
            mime="application/zip",
            key="split_zip"
        )
        
        st.write("**個別ダウンロード**")
        col1, col2, col3, col4 = st.columns(4, gap="small")
        with col1:
            buf = BytesIO()
            split_images[0].save(buf, format='PNG')
            buf.seek(0)
            st.download_button("1.png", buf.getvalue(), "1.png", "image/png", key="split_1", use_container_width=True)
        with col2:
            buf = BytesIO()
            split_images[1].save(buf, format='PNG')
            buf.seek(0)
            st.download_button("2.png", buf.getvalue(), "2.png", "image/png", key="split_2", use_container_width=True)
        with col3:
            buf = BytesIO()
            split_images[2].save(buf, format='PNG')
            buf.seek(0)
            st.download_button("3.png", buf.getvalue(), "3.png", "image/png", key="split_3", use_container_width=True)
        with col4:
            buf = BytesIO()
            split_images[3].save(buf, format='PNG')
            buf.seek(0)
            st.download_button("4.png", buf.getvalue(), "4.png", "image/png", key="split_4", use_container_width=True)
    else:
        st.info("👆 画像をアップロードしてください")

# ===== タブ3：ワンステップ =====
with tab3:
    st.subheader("一気に処理（4分割+合成）")
    
    st.write("**メイン画像をアップロード**")
    main_file_onestep = st.file_uploader("メイン画像", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], key="main_onestep")
    
    st.write("**上下用画像をアップロード（4枚、不足時はランダム補充）**")
    side_files_onestep = st.file_uploader("上下用画像", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], accept_multiple_files=True, key="sides_onestep")
    
    if main_file_onestep is not None and len(side_files_onestep) > 0:
        if 'current_main_file' not in st.session_state or st.session_state.current_main_file != main_file_onestep.name:
            st.session_state.current_main_file = main_file_onestep.name
            if 'one_image_buffers' in st.session_state:
                del st.session_state.one_image_buffers
            if 'one_sides' in st.session_state:
                del st.session_state.one_sides
            if 'one_heights' in st.session_state:
                del st.session_state.one_heights
        
        st.write(f"✓ {len(side_files_onestep)}枚の上下用画像がアップロードされました")
        
        main_img = Image.open(main_file_onestep)
        original_width, original_height = main_img.size
        
        st.write(f"**メイン画像サイズ:** {original_width} × {original_height}")
        
        main_cropped = crop_to_16_9(main_img)
        crop_width, crop_height = main_cropped.size
        
        # 統一サイズにリサイズ（1200×675に統一）
        STANDARD_WIDTH = 1200
        STANDARD_HEIGHT = 675
        main_cropped = main_cropped.resize((STANDARD_WIDTH, STANDARD_HEIGHT), Image.Resampling.LANCZOS)
        crop_width, crop_height = main_cropped.size
        
        st.write(f"**16:9トリミング後:** {crop_width} × {crop_height}")
        
        split_images, cw, ch = split_4(main_cropped)
        
        split_width = crop_width // 2
        split_height = crop_height // 2
        
        st.write(f"**基準サイズ（メイン分割後）:** {split_width} × {split_height}")
        
        side_images = [Image.open(f) for f in side_files_onestep]
        
        needed = 4
        final_sides = side_images.copy()
        
        if len(final_sides) < needed:
            shortage = needed - len(final_sides)
            for _ in range(shortage):
                final_sides.append(random.choice(side_images))
        
        if 'one_heights' not in st.session_state:
            st.session_state.one_heights = {}
        
        if 'one_sides' not in st.session_state:
            st.session_state.one_sides = {}
            for idx in range(4):
                shuffled = final_sides.copy()
                random.shuffle(shuffled)
                st.session_state.one_sides[idx] = shuffled
        
        final_images = []
        
        for idx, split_img in enumerate(split_images):
            shuffled_sides = st.session_state.one_sides[idx]
            
            if idx not in st.session_state.one_heights:
                st.session_state.one_heights[idx] = generate_heights(split_height)
            
            h1, h2, h3, h4 = st.session_state.one_heights[idx]
            
            top_img1 = resize_to_split_size(shuffled_sides[0].copy(), split_width, h1)
            top_img2 = resize_to_split_size(shuffled_sides[1].copy(), split_width, h2)
            bottom_img1 = resize_to_split_size(shuffled_sides[2].copy(), split_width, h3)
            bottom_img2 = resize_to_split_size(shuffled_sides[3].copy(), split_width, h4)
            
            total_height = h1 + h2 + split_height + h3 + h4
            combined = Image.new('RGB', (split_width, total_height))
            
            y_offset = 0
            combined.paste(top_img1, (0, y_offset))
            y_offset += h1
            
            combined.paste(top_img2, (0, y_offset))
            y_offset += h2
            
            combined.paste(split_img, (0, y_offset))
            y_offset += split_height
            
            combined.paste(bottom_img1, (0, y_offset))
            y_offset += h3
            
            combined.paste(bottom_img2, (0, y_offset))
            
            final_images.append(combined)
        
        if 'one_image_buffers' not in st.session_state:
            st.session_state.one_image_buffers = {}
            for i, img in enumerate(final_images):
                buf = BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)
                st.session_state.one_image_buffers[i] = buf.getvalue()
        
        st.subheader("プレビュー")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.image(final_images[0], width=150)
        with col2:
            st.image(final_images[1], width=150)
        with col3:
            st.image(final_images[2], width=150)
        with col4:
            st.image(final_images[3], width=150)
        
        st.subheader("ダウンロード")
        
        zip_data = create_zip(final_images)
        st.download_button(
            label="📦 ZIP一括ダウンロード",
            data=zip_data,
            file_name="合成画像.zip",
            mime="application/zip",
            key="one_zip"
        )
        
        st.write("**個別ダウンロード**")
        col1, col2, col3, col4 = st.columns(4, gap="small")
        with col1:
            st.download_button("1.png", st.session_state.one_image_buffers[0], "1.png", "image/png", key="one_1", use_container_width=True)
        with col2:
            st.download_button("2.png", st.session_state.one_image_buffers[1], "2.png", "image/png", key="one_2", use_container_width=True)
        with col3:
            st.download_button("3.png", st.session_state.one_image_buffers[2], "3.png", "image/png", key="one_3", use_container_width=True)
        with col4:
            st.download_button("4.png", st.session_state.one_image_buffers[3], "4.png", "image/png", key="one_4", use_container_width=True)
    else:
        st.info("👆 メイン画像と上下用画像をアップロードしてください")
