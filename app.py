import streamlit as st
from ultralytics import YOLO
from PIL import Image
from gtts import gTTS
import os
import base64

# ==============================================================================
# 1. TỪ ĐIỂN SIÊU ĐẦY ĐỦ CÁC MÃ & BIẾN THỂ BIỂN BÁO
# ==============================================================================
VIETNAMESE_SIGNS = {
    # --- BIỂN HẠN CHẾ TỐC ĐỘ ---
    "127": "Biển tốc độ tối đa cho phép",
    "127.1": "Biển tốc độ tối đa cho phép 10 đến 20 km/h",
    "127.2": "Biển tốc độ tối đa cho phép 20 km/h",
    "127.3": "Biển tốc độ tối đa cho phép 30 km/h",
    "127.4": "Biển tốc độ tối đa cho phép 40 km/h",
    "127.5": "Biển tốc độ tối đa cho phép 50 km/h",
    "127.6": "Biển tốc độ tối đa cho phép 60 km/h",
    "127.7": "Biển tốc độ tối đa cho phép 70 km/h",
    "127.8": "Biển tốc độ tối đa cho phép 80 km/h",
    "127a": "Biển tốc độ tối đa cho phép trong khu vực",
    "127b": "Biển hết hạn chế tốc độ tối đa trong khu vực",
    "127c": "Biển tốc độ tối đa cho phép theo làn đường",

    # --- BIỂN CẤM (Nhóm 1xx) ---
    "101": "Biển đường cấm",
    "102": "Biển cấm đi ngược chiều",
    "103": "Biển cấm xe ô tô",
    "103a": "Biển cấm xe ô tô",
    "103b": "Biển cấm xe ô tô rẽ phải",
    "103c": "Biển cấm xe ô tô rẽ trái",
    "104": "Biển cấm xe máy",
    "105": "Biển cấm ô tô và xe máy",
    "106": "Biển cấm xe tải",
    "106a": "Biển cấm xe tải",
    "106b": "Biển cấm xe tải",
    "106c": "Biển cấm xe chở hàng nguy hiểm",
    "107": "Biển cấm xe khách và xe tải",
    "108": "Biển cấm xe kéo rơ moóc",
    "109": "Biển cấm máy kéo",
    "110a": "Biển cấm đi xe đạp",
    "110b": "Biển cấm xe đạp thồ",
    "111a": "Biển cấm xe gắn máy",
    "112": "Biển cấm người đi bộ",
    "115": "Biển hạn chế trọng tải toàn bộ xe",
    "116": "Biển hạn chế trọng tải trục xe",
    "117": "Biển hạn chế chiều cao",
    "118": "Biển hạn chế chiều ngang",
    "119": "Biển hạn chế chiều dài xe",
    "121": "Biển cự ly tối thiểu giữa hai xe",
    "122": "Biển dừng lại",
    "123a": "Biển cấm rẽ trái",
    "123b": "Biển cấm rẽ phải",
    "124a": "Biển cấm quay đầu xe",
    "124b": "Biển cấm ô tô quay đầu xe",
    "125": "Biển cấm vượt",
    "126": "Biển cấm xe tải vượt",
    "128": "Biển cấm bóp còi",
    "129": "Biển kiểm tra",
    "130": "Biển cấm dừng và đỗ xe",
    "131a": "Biển cấm đỗ xe",
    "131b": "Biển cấm đỗ xe ngày lẻ",
    "131c": "Biển cấm đỗ xe ngày chẵn",
    "133": "Biển hết cấm vượt",
    "134": "Biển hết hạn chế tốc độ tối đa",
    "135": "Biển hết tất cả các lệnh cấm",
    "137": "Biển cấm rẽ trái và rẽ phải",  # <-- Đã bổ sung

    # --- BIỂN NGUY HIỂM & CẢNH BÁO (Nhóm 2xx) ---
    "201a": "Biển chỗ ngoặt nguy hiểm vòng bên trái",
    "201b": "Biển chỗ ngoặt nguy hiểm vòng bên phải",
    "202a": "Biển nhiều chỗ ngoặt nguy hiểm liên tiếp",
    "203a": "Biển đường bị hẹp cả hai bên",
    "203b": "Biển đường bị hẹp bên trái",
    "203c": "Biển đường bị hẹp bên phải",
    "204": "Biển đường hai chiều",
    "205": "Biển đường giao nhau cùng cấp",   # <-- Đã bổ sung
    "205a": "Biển đường giao nhau cùng cấp",
    "207a": "Biển giao nhau với đường không ưu tiên",
    "208": "Biển giao nhau với đường ưu tiên",
    "209": "Biển giao nhau có tín hiệu đèn",
    "210": "Biển giao nhau với đường sắt có rào chắn",
    "211a": "Biển giao nhau với đường sắt không có rào chắn",
    "219": "Biển dốc xuống nguy hiểm",
    "221a": "Biển đường có ổ gà, lồi lõm",
    "222a": "Biển đường trơn trượt",
    "224": "Biển đường người đi bộ cắt ngang",
    "225": "Biển trẻ em qua đường",
    "227": "Biển công trường đang thi công",
    "233": "Biển nguy hiểm khác",
    "239": "Biển đường cáp điện phía trên",
    "245": "Biển đoạn đường đi chậm",         # <-- Đã bổ sung
    "245a": "Biển đoạn đường đi chậm",

    # --- BIỂN HIỆU LỆNH (Nhóm 3xx) ---
    "301a": "Biển hướng đi phải theo: Đi thẳng",
    "301b": "Biển hướng đi phải theo: Rẽ phải",
    "301c": "Biển hướng đi phải theo: Rẽ trái",
    "301d": "Biển hướng đi phải theo: Rẽ phải tuyến chính",
    "301e": "Biển hướng đi phải theo: Rẽ trái tuyến chính",
    "301f": "Biển hướng đi phải theo: Đi thẳng và rẽ phải",
    "301h": "Biển hướng đi phải theo: Đi thẳng và rẽ trái",
    "302a": "Biển hướng vòng chướng ngại vật sang phải",
    "302b": "Biển hướng vòng chướng ngại vật sang trái",
    "303": "Biển nơi giao nhau chạy theo vòng xuyến",
    "304": "Biển đường dành cho xe thô sơ",
    "305": "Biển đường dành cho người đi bộ",

    # --- BIỂN CHỈ DẪN (Nhóm 4xx) ---
    "401": "Biển bắt đầu đường ưu tiên",
    "402": "Biển hết đoạn đường ưu tiên",
    "405a": "Biển đường cụt",
    "407a": "Biển đường một chiều",
    "411": "Biển hướng đi trên mỗi làn đường",
    "412": "Biển làn đường dành riêng cho từng loại xe",
    "412b": "Biển làn đường dành cho xe ô tô con",
    "412c": "Biển làn đường dành cho xe ô tô tải",
    "412d": "Biển làn đường dành cho xe máy",
    "423": "Biển vị trí người đi bộ sang ngang",
    "423a": "Biển vị trí người đi bộ sang ngang",
    "423b": "Biển vị trí người đi bộ sang ngang",
    "424a": "Biển cầu vượt qua đường cho người đi bộ",
    "443": "Biển báo chợ",
    
    # --- TRƯỜNG HỢP NGOẠI LỆ ---
    "other": "Biển báo khác"
}

# Hàm ép tự phát âm thanh bằng mã HTML
def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Giao diện Web
st.set_page_config(page_title="Nhận diện biển báo VN", page_icon="🚦")

@st.cache_resource
def load_yolo_model():
    return YOLO('YOLOV8/yolov8m/Yolov8m_final.pt')

try:
    model = load_yolo_model()
    st.sidebar.success("Đã nạp thành công não YOLO!")
    
    st.sidebar.markdown("---")
    if st.sidebar.checkbox("Soi danh sách mã gốc của AI"):
        st.sidebar.write("**Tất cả các mã AI có thể nhận diện:**")
        st.sidebar.json(model.names)
        
except Exception as e:
    st.sidebar.error(f"Lỗi nạp model: {e}")

st.title("AI Quét & Đọc Biển Báo Tự Động")
st.write("Tải ảnh lên, AI sẽ tự quét, dịch nghĩa chuẩn QC41 và tự động đọc!")
st.markdown("---")

uploaded_file = st.file_uploader("Chọn ảnh để quét...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Ảnh gốc bạn tải lên", use_container_width=True)
    
    if st.button("QUÉT TÌM BIỂN BÁO", type="primary"):
        if 'model' in locals():
            with st.spinner('YOLO đang quét ảnh...'):
                results = model.predict(source=image, conf=0.35, iou=0.45)
                
                res_image = results[0].plot() 
                res_image_rgb = res_image[..., ::-1]
                
                st.success("Quét xong!")
                st.image(res_image_rgb, caption="Kết quả từ YOLOv8", use_container_width=True)
                
                boxes = results[0].boxes
                
                valid_boxes = []
                danh_sach_doc = []
                
                for box in boxes:
                    class_id = int(box.cls[0])
                    # Xóa khoảng trắng thừa để tra từ điển chính xác 100%
                    ma_bien_bao = str(model.names[class_id]).strip() 
                    conf = float(box.conf[0]) * 100
                    
                    # Luật lọc
                    if ma_bien_bao == "227" and conf < 75.0:
                        continue 
                    if conf < 55.0:
                        continue
                    
                    valid_boxes.append((ma_bien_bao, conf))
                
                if len(valid_boxes) == 0:
                    st.warning("Không tìm thấy biển báo nào đủ độ tin cậy!")
                else:
                    st.write(f"**Phát hiện {len(valid_boxes)} biển báo:**")
                    
                    for ma_bien_bao, conf in valid_boxes:
                        # Tra từ điển mở rộng
                        ten_tieng_viet = VIETNAMESE_SIGNS.get(ma_bien_bao, f"Biển số {ma_bien_bao}")
                        
                        st.write(f"- **{ten_tieng_viet}** (Độ tin cậy: {conf:.2f}%)")
                        
                        if ten_tieng_viet not in danh_sach_doc:
                            danh_sach_doc.append(ten_tieng_viet)
                    
                    if danh_sach_doc:
                        cau_noi = "Hệ thống phát hiện các biển báo: " + ", ".join(danh_sach_doc)
                        tts = gTTS(text=cau_noi, lang='vi')
                        tts.save("doc_bien_bao.mp3")
                        
                        autoplay_audio("doc_bien_bao.mp3")
                        st.info("AI đang đọc thành tiếng...")