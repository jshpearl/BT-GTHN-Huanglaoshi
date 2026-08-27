import streamlit as st
import requests
import datetime
import json

# ==========================================================
# 1. CẤU HÌNH TRANG & CSS CUSTOMIZATION (TONG PASTEL)
# ==========================================================
st.set_page_config(
    page_title="Bài tập Giáo trình Hán ngữ (1)",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for Pastel Styling
st.markdown("""
<style>
    /* Nền trang màu kem nhạt */
    .stApp {
        background-color: #FAF6F0;
    }
    
    /* Font và màu chữ tối tương phản */
    body, p, div, span, label {
        color: #2c3e50 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Thiết kế thẻ Card cho mỗi câu hỏi */
    .quiz-card {
        background-color: #FFFFFF;
        padding: 22px;
        border-radius: 16px;
        border-left: 6px solid #FFD1DC; /* Viền hồng pastel */
        box-shadow: 0 4px 12px rgba(44, 62, 80, 0.04);
        margin-bottom: 20px;
    }
    
    /* Tiêu đề chính */
    .main-title {
        color: #4A5568 !important;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }
    
    /* Tiêu đề phụ */
    .sub-title {
        color: #718096 !important;
        text-align: center;
        font-style: italic;
        margin-bottom: 25px;
    }
    
    /* Banner đầu mỗi bài tập */
    .lesson-banner {
        background-color: #E8F5E9; /* Xanh lá pastel nhạt */
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #81C784;
        margin-bottom: 20px;
        font-weight: bold;
    }
    
    /* Footer ở cuối trang */
    .footer {
        text-align: center;
        padding: 20px;
        margin-top: 50px;
        border-top: 1px solid #E2E8F0;
        color: #A0AEC0 !important;
        font-weight: 500;
    }

    /* Các expander giải thích câu sai */
    .explanation-box {
        background-color: #FFF9E6;
        border: 1px solid #FFE082;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# URL Webhook Google Sheets (Giáo viên thay thế link này sau khi deploy)
# Để trống hoặc cấu hình trong Secrets của Streamlit
WEBHOOK_URL = st.secrets.get("GOOGLE_SHEET_WEBHOOK", "https://script.google.com/macros/s/AKfycbyWd_lmpFBAQP1ZPa-X_Njwvqj-Frii7PThZV7yL8OmaFDJYVNjCeUTaP5eiapalRDX/exec")

# ==========================================================
# 2. NGÂN HÀNG CÂU HỎI CHUẨN 3 BÀI 6, 7, 8 (MỖI BÀI 30 CÂU)
# ==========================================================
QUESTIONS = {
    'bai_8': {
        'title': 'BÀI 8: BẠN ĂN CÁI GÌ? / 你吃什么',
        'listening': [
            # Phần 1 (Câu 1-5): Phán đoán đúng/sai
            {'id': 1, 'type': 'tf', 'text': 'Câu 1. 吃饭 / Chī fàn', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '吃饭 (Chī fàn - Ăn cơm)', 'explanation': 'Audio phát chính xác cụm từ "吃饭" (Ăn cơm).'},
            {'id': 2, 'type': 'tf', 'text': 'Câu 2. 请坐 / Qǐng zuò', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '请坐 (Qǐng zuò - Xin mời ngồi)', 'explanation': 'Audio phát chính xác cụm từ "请坐" (Xin mời ngồi).'},
            {'id': 3, 'type': 'tf', 'text': 'Câu 3. 美国人 / Měiguó rén', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '美国人 (Měiguó rén - Người Mỹ)', 'explanation': 'Hình ảnh không khớp với từ chỉ người nước Mỹ.'},
            {'id': 4, 'type': 'tf', 'text': 'Câu 4. 朋友 / Péngyou', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '朋友 (Péngyou - Bạn bè)', 'explanation': 'Nội dung hình ảnh và cụm từ "朋友" không đồng nhất.'},
            {'id': 5, 'type': 'tf', 'text': 'Câu 5. 请喝茶 / Qǐng hē chá', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '请喝茶 (Qǐng hē chá - Mời uống trà)', 'explanation': 'Audio phát chính xác cụm từ "请喝茶" (Xin mời uống trà).'},
            # Phần 2 (Câu 6-10): Nghe đối thoại, nối hình
            {'id': 6, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 6: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'D', 'script': '男：他叫什么名字？\n女：他叫大卫。他是美国人。\n(Nam: Cậu ấy tên là gì?\nNữ: Cậu ấy tên là David. Cậu ấy là người Mỹ.)', 'explanation': 'Hội thoại nhắc đến David - một người Mỹ (Hình D tương ứng).'},
            {'id': 7, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 7: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'B', 'script': '男：你想吃米饭吗？\n女：我想吃。\n(Nam: Bạn có muốn ăn cơm không?\nNữ: Mình muốn ăn.)', 'explanation': 'Hội thoại nhắc đến mong muốn ăn cơm (米饭), khớp với hình B.'},
            {'id': 8, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 8: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'F', 'script': '男：中午你去哪儿吃饭？\n女：我去学生食堂。\n(Nam: Buổi trưa bạn đi đâu ăn cơm?\nNữ: Mình đến nhà ăn sinh viên.)', 'explanation': 'Nhân vật nữ trả lời đi ăn cơm ở nhà ăn sinh viên (学生食堂), khớp với hình F.'},
            {'id': 9, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 9: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'A', 'script': '男：我请你喝咖啡怎么样？\n女：太好了，谢谢！\n(Nam: Mình mời bạn uống cà phê được không?\nNữ: Tuyệt quá, cảm ơn bạn!)', 'explanation': 'Lời mời đi uống cà phê (喝咖啡) đầy hào hứng, khớp với hình A.'},
            {'id': 10, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 10: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'E', 'script': '男：老师，您叫什么名字？\n女：我叫李月。\n(Nam: Thưa cô, cô tên là gì ạ?\nNữ: Cô tên là Lý Nguyệt.)', 'explanation': 'Học sinh hỏi tên giáo viên và cô trả lời tên Lý Nguyệt (李月), khớp với hình E.'},
            # Phần 3 (Câu 11-15): Nghe và chọn đáp án đúng nhất
            {'id': 11, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 11: Chọn đáp án đúng cho câu hỏi: 他不想吃什么？ (Anh ấy không muốn ăn gì?) \n- A: 包子 / bāozi \n- B: 面条儿 / miàntiáor \n- C: 米饭 / mǐfàn', 'audio_part': 3, 'correct': 'C', 'script': '我这几天中午吃的 đều là 米饭，不想吃 le。\n问：他不想吃什么？\n(Mấy ngày nay buổi trưa tôi đều ăn cơm, không muốn ăn nữa rồi.\nHỏi: Anh ấy không muốn ăn gì?)', 'explanation': 'Nhân vật nam nói đã chán ăn cơm (米饭). Do đó đáp án đúng là C.'},
            {'id': 12, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 12: Chọn đáp án đúng cho câu hỏi: 他是哪国人？ (Anh ấy là người nước nào?) \n- A: 美国人 / Měiguó rén \n- B: 中国人 / Zhōngguó rén \n- C: 日本人 / Rìběn rén', 'audio_part': 3, 'correct': 'B', 'script': '他叫王心，他是中国人。\n问：他是哪国人？\n(Anh ấy tên là Vương Tâm, anh ấy là người Trung Quốc.\nHỏi: Anh ấy là người nước nào?)', 'explanation': 'Đoạn ghi âm giới thiệu rõ ràng Vương Tâm là người Trung Quốc (中国人). Chọn B.'},
            {'id': 13, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 13: Chọn đáp án đúng cho câu hỏi: 她叫什么名字？ (Cô ấy tên là gì?) \n- A: 王方 / Wáng Fāng \n- B: 李心 / Lǐ Xīn \n- C: 玛丽 / Mǎlì', 'audio_part': 3, 'correct': 'B', 'script': '她叫李心，是我的中国朋友。\n问：她叫什么名字？\n(Cô ấy tên là Lý Tâm, là người bạn Trung Quốc của tôi.\nHỏi: Cô ấy tên là gì?)', 'explanation': 'Hội thoại nêu rõ tên cô ấy là Lý Tâm (李心). Chọn B.'},
            {'id': 14, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 14: Chọn đáp án đúng cho câu hỏi: 前面那个人是谁？ (Người phía trước kia là ai?) \n- A: 他的爸爸 / tā de bàba \n- B: 他的朋友 / tā de péngyou \n- C: 彼の老师 / tā de lǎoshī', 'audio_part': 3, 'correct': 'C', 'script': '前面那个人是我的老师，不是我爸爸。\n问：前面那个人是谁？\n(Người phía trước kia là giáo viên của tôi, không phải bố tôi.\nHỏi: Người phía trước là ai?)', 'explanation': 'Nhân vật nói rõ người phía trước là giáo viên của mình (我的老师). Chọn C.'},
            {'id': 15, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 15: Chọn đáp án đúng cho câu hỏi: 他们骑车去哪儿？ (Họ đạp xe đi đâu?) \n- A: 公园 / gōngyuán \n- B: 银行 / yínháng \n- C: 学校 / xuéxiào', 'audio_part': 3, 'correct': 'A', 'script': '我和丽丽骑车去公园。\n问：他们骑车去哪儿？\n(Tôi và Lệ Lệ đạp xe đi công viên.\nHỏi: Họ đạp xe đi đâu?)', 'explanation': 'Họ đạp xe đi công viên (公园). Chọn A.'}
        ],
        'reading': [
            # Phần 1 (Câu 16-20): Xem từ vựng phán đoán hình
            {'id': 16, 'type': 'tf', 'text': 'Câu 16. bāozi / 包子 (Hình ảnh mô tả: Một giỏ trứng luộc đặt trong cốc giấy)', 'correct': 'Đúng (✓)', 'explanation': 'Theo đáp án chính thức từ sách giáo khoa, câu này được đánh giá là Đúng (✓).'},
            {'id': 17, 'type': 'tf', 'text': 'Câu 17. jīdàn / 鸡蛋 (Hình ảnh mô tả: Một con gà mái đứng cạnh rổ trứng nhỏ)', 'correct': 'Sai (✗)', 'explanation': 'Theo đáp án chính thức từ sách giáo khoa, câu này được đánh giá là Sai (✗).'},
            {'id': 18, 'type': 'tf', 'text': 'Câu 18. chī jiǎozi / 吃饺子 (Hình ảnh mô tả: Người phụ nữ đang dùng dĩa ăn sủi cảo)', 'correct': 'Sai (✗)', 'explanation': 'Theo đáp án chính thức từ sách giáo khoa, câu này được đánh giá là Sai (✗).'},
            {'id': 19, 'type': 'tf', 'text': 'Câu 19. xiě Hànzì / 写汉字 (Hình ảnh mô tả: Tay cầm bút lông viết chữ Hán lên giấy)', 'correct': 'Đúng (✓)', 'explanation': 'Hình ảnh tay cầm bút lông viết chữ Hán khớp hoàn toàn với cụm từ "写汉字". Chọn Đúng (✓).'},
            {'id': 20, 'type': 'tf', 'text': 'Câu 20. hē píjiǔ / 喝啤酒 (Hình ảnh mô tả: Hai cốc bia tươi đầy bọt đang cụng nhau)', 'correct': 'Đúng (✓)', 'explanation': 'Hình ảnh hai cốc bia cụng nhau chính là hành động uống bia "喝啤酒". Chọn Đúng (✓).'},
            # Phần 2 (Câu 21-25): Phối hợp câu hỏi - câu trả lời
            {'id': 21, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 21. 你去哪儿吃饭？ / Nǐ qù nǎr chī fàn? \n- Lựa chọn: A: 去食堂。 | B: 这些是馒头。 | C: 不喝，我喝茶。 | D: 三个。 | E: 我吃面条儿。', 'correct': 'A', 'explanation': 'Câu hỏi "Ăn cơm ở đâu?" ghép với câu trả lời "Đi nhà ăn" (去食堂 - A).'},
            {'id': 22, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 22. 你吃什么？ / Nǐ chī shénme? \n- Lựa chọn: A: 去食堂。 | B: 这些是馒头。 | C: 不喝，我喝茶。 | D: 三个。 | E: 我吃面条儿。', 'correct': 'E', 'explanation': 'Câu hỏi "Ăn gì?" ghép với câu trả lời "Tôi ăn mì" (我吃面条儿 - E).'},
            {'id': 23, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 23. 你喝啤酒吗？ / Nǐ hē píjiǔ ma? \n- Lựa chọn: A: 去食堂。 | B: 这些是馒头。 | C: 不喝，我喝茶。 | D: 三个。 | E: 我吃面条儿。', 'correct': 'C', 'explanation': 'Câu hỏi "Có uống bia không?" ghép với câu trả lời "Không uống, tôi uống trà" (不喝，我喝茶 - C).'},
            {'id': 24, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 24. 这些是什么？ / Zhèxiē shì shénme? \n- Lựa chọn: A: 去食堂。 | B: 这些是馒头。 | C: 不喝，我喝茶。 | D: 三个。 | E: 我吃面条儿。', 'correct': 'B', 'explanation': 'Câu hỏi số nhiều "Đây là những cái gì?" ghép với "Đây là bánh màn thầu" (这些是馒头 - B).'},
            {'id': 25, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 25. 你要几个包子？ / Nǐ yào jǐ ge bāozi? \n- Lựa chọn: A: 去食堂。 | B: 这些是馒头。 | C: 不喝，我喝茶。 | D: 三个。 | E: 我吃面条儿。', 'correct': 'D', 'explanation': 'Câu hỏi về số lượng bao nhiêu bánh bao ghép với câu trả lời "3 cái" (三个 - D).'},
            # Phần 3 (Câu 26-30): Điền từ vào chỗ trống
            {'id': 26, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 26. 明天中午我（  ）你吃饭。 \n[A: 汤 / tāng | B: 碗 / wǎn | C: 食堂 / shítáng | D: 名字 / míngzi | E: 请 / qǐng | F: 米饭 / mǐfàn]', 'correct': 'E', 'explanation': 'Chọn động từ "请" (mời) để tạo nghĩa: "Trưa mai tôi mời bạn ăn cơm".'},
            {'id': 27, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 27. 我不吃（  ），我吃面条儿。 \n[A: 汤 / tāng | B: 碗 / wǎn | C: 食堂 / shítáng | D: 名字 / míngzi | E: 请 / qǐng | F: 米饭 / mǐfàn]', 'correct': 'F', 'explanation': 'Chọn danh từ món ăn "米饭" (cơm) để tạo vế đối lập: "Tôi không ăn cơm, tôi ăn mì".'},
            {'id': 28, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 28. 我要一（  ）面条儿，一个馒头。 \n[A: 汤 / tāng | B: 碗 / wǎn | C: 食堂 / shítáng | D: 名字 / míngzi | E: 请 / qǐng | F: 米饭 / mǐfàn]', 'correct': 'B', 'explanation': 'Chọn lượng từ "碗" (bát/tô) đi kèm với mì: "Tôi muốn một bát mì, một cái màn thầu".'},
            {'id': 29, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 29. 女：你喝什么（  ）？ 男：我不喝（  ），我喝啤酒。 \n[A: 汤 / tāng | B: 碗 / wǎn | C: 食堂 / shítáng | D: 名字 / míngzi | E: 请 / qǐng | F: 米饭 / mǐfàn]', 'correct': 'A', 'explanation': 'Chọn từ "汤" (canh/súp): "Bạn uống canh gì? - Tôi không uống canh, tôi uống bia".'},
            {'id': 30, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 30. 男：我们去哪儿吃饭？ 女：去（  ）吧。 \n[A: 汤 / tāng | B: 碗 / wǎn | C: 食堂 / shítáng | D: 名字 / míngzi | E: 请 / qǐng | F: 米饭 / mǐfàn]', 'correct': 'C', 'explanation': 'Điền danh từ địa điểm "食堂" (nhà ăn): "Chúng mình đi nhà ăn ăn cơm nhé".'}
        ]
    },
    'bai_7': {
        'title': 'BÀI 7: TÔI HỌC TIẾNG HÁN / 我学习汉语',
        'listening': [
            # Phần 1 (Câu 1-5): Phán đoán đúng/sai (Khuyết hình scan trong PDF)
            {'id': 1, 'type': 'tf', 'text': 'Câu 1. 你好！/ Nǐhǎo! [Ghi chú: Bản scan PDF thiếu hình ảnh minh họa]', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '你好！(Nǐhǎo! - Xin chào!)', 'explanation': 'Theo đáp án chuẩn gốc, câu này được phán đoán là Sai (✗).'},
            {'id': 2, 'type': 'tf', 'text': 'Câu 2. 再见 / Zàijiàn [Ghi chú: Bản scan PDF thiếu hình ảnh minh họa]', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '再见 (Zàijiàn - Tạm biệt)', 'explanation': 'Theo đáp án chuẩn gốc, câu này được phán đoán là Đúng (✓).'},
            {'id': 3, 'type': 'tf', 'text': 'Câu 3. 学习汉语 / Xuéxí Hànyǔ [Ghi chú: Bản scan PDF thiếu hình ảnh minh họa]', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '学习汉语 (Xuéxí Hànyǔ - Học tiếng Hán)', 'explanation': 'Theo đáp án chuẩn gốc, câu này được phán đoán là Đúng (✓).'},
            {'id': 4, 'type': 'tf', 'text': 'Câu 4. 老师 / Lǎoshī [Ghi chú: Bản scan PDF thiếu hình ảnh minh họa]', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '老师 (Lǎoshī - Giáo viên)', 'explanation': 'Theo đáp án chuẩn gốc, câu này được phán đoán là Sai (✗).'},
            {'id': 5, 'type': 'tf', 'text': 'Câu 5. 很好 / Hěn hǎo [Ghi chú: Bản scan PDF thiếu hình ảnh minh họa]', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '很好 (Hěn hǎo - Rất tốt)', 'explanation': 'Theo đáp án chuẩn gốc, câu này được phán đoán là Đúng (✓).'},
            # Phần 2 (Câu 6-10): Nghe đối thoại, nối hình
            {'id': 6, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 6: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'D', 'script': '男：这本书是谁的？\n女：是王老师的。\n(Nam: Quyển sách này của ai?\nNữ: Là của thầy giáo Vương.)', 'explanation': 'Đối thoại nói về quyển sách (书) trên bàn, tương ứng hình D.'},
            {'id': 7, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 7: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'A', 'script': '女：你一个人去中国？\n男：不，和我爸妈，我们三个人。\n(Nữ: Bạn đi Trung Quốc một mình à?\nNam: Không, đi cùng bố mẹ tôi, chúng tôi có ba người.)', 'explanation': 'Nhân vật nam dắt vali đi Trung Quốc cùng gia đình, khớp hình A.'},
            {'id': 8, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 8: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'F', 'script': '男：您好！您是美国人吗？\n男：是，我是美国人。\n(Nam: Xin chào! Ngài là người Mỹ phải không?\nNam: Đúng vậy, tôi là người Mỹ.)', 'explanation': 'Hai người nam mặc comple bắt tay chào hỏi nhau lịch sự trong văn phòng, khớp hình F.'},
            {'id': 9, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 9: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'E', 'script': '男：她是哪国人？\n女：她是中国人。\n(Nam: Cô ấy là người nước nào?\nNữ: Cô ấy là người Trung Quốc.)', 'explanation': 'Nói về một cô gái người Trung Quốc đang ăn cơm rất giản dị, khớp hình E.'},
            {'id': 10, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 10: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'B', 'script': '女：老师，谢谢您，再见！\n男：再见！\n(Nữ: Em cảm ơn thầy, tạm biệt thầy!\nNam: Tạm biệt em!)', 'explanation': 'Học sinh nữ chào tạm biệt thầy giáo ra về, khớp hình B.'},
            # Phần 3 (Câu 11-15): Nghe và chọn đáp án đúng nhất
            {'id': 11, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 11: Chọn đáp án đúng cho câu hỏi: 她叫什么名字？ (Cô ấy tên là gì?) \n- A: 李月 / Lǐ Yuè \n- B: 张东 / Zhāng Dōng \n- C: 玛丽 / Mǎlì', 'audio_part': 3, 'correct': 'A', 'script': '她叫李月，她是老师。\n问：她叫什么名字？\n(Cô ấy tên là Lý Nguyệt, cô ấy là giáo viên.\nHỏi: Cô ấy tên là gì?)', 'explanation': 'Audio nói rõ tên cô ấy là "李月". Chọn A.'},
            {'id': 12, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 12: Chọn đáp án đúng cho câu hỏi: 他是谁？ (Thầy ấy là ai?) \n- A: 我的朋友 / wǒ de péngyou \n- B: 我的哥哥 / wǒ de gēge \n- C: 我的老师 / wǒ de lǎoshī', 'audio_part': 3, 'correct': 'C', 'script': '他是中国人，他是我的汉语老师。\n问：他是谁？\n(Thầy ấy là người Trung Quốc, thầy ấy là giáo viên tiếng Trung của tôi.\nHỏi: Thầy ấy là ai?)', 'explanation': 'Người này được giới thiệu là giáo viên tiếng Hán của tôi (我的汉语老师). Chọn C.'},
            {'id': 13, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 13: Chọn đáp án đúng cho câu hỏi: 明天星期几？ (Ngày mai thứ mấy?) \n- A: 星期一 / xīngqīyī \n- B: 星期六 / xīngqīliù \n- C: 星期天 / xīngqītiān', 'audio_part': 3, 'correct': 'C', 'script': '今天是星期天，我们明天回家。\n问：明天星期几？\n(Hôm nay là Chủ Nhật, ngày mai chúng tôi về nhà.\nHỏi: Ngày mai là thứ mấy?)', 'explanation': 'Lưu ý: Mặc dù hôm nay là chủ nhật thì ngày mai phải là thứ hai (星期一 - A), nhưng trong đáp án tham khảo chính thức của HSK, đáp án ghi nhận là C (Chủ Nhật). Ta chọn C theo barem điểm chính thức.'},
            {'id': 14, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 14: Chọn đáp án đúng cho câu hỏi: 他们一个星期学习几天？ (Họ học mấy ngày một tuần?) \n- A: 5天 / wǔ tiān \n- B: 3天 / sān tiān \n- C: 7天 / qī tiān', 'audio_part': 3, 'correct': 'A', 'script': '我和朋友来中国学习汉语，我们一个星期学习五天。\n问：他们一个星期学习几天？\n(Tôi và bạn tôi đến Trung Quốc học tiếng Trung, một tuần học năm ngày.\nHỏi: Họ học mấy ngày một tuần?)', 'explanation': 'Audio phát rõ ràng học năm ngày "五天". Chọn A.'},
            {'id': 15, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 15: Chọn đáp án đúng cho câu hỏi: 他在这儿做什么？ (Anh ấy làm gì ở đây?) \n- A: 喝咖啡 / hē kāfēi \n- B: 学习 / xuéxí \n- C: 去公园 / qù gōngyuán', 'audio_part': 3, 'correct': 'B', 'script': '我不是北京人，我在这儿学习。\n问：他在这儿做什么？\n(Tôi không phải là người Bắc Kinh, tôi học tập ở đây.\nHỏi: Anh ấy làm gì ở đây?)', 'explanation': 'Nhân vật nói đang ở đây học tập (学习). Chọn B.'}
        ],
        'reading': [
            # Phần 1 (Câu 16-20): Xem từ vựng phán đoán hình đúng sai
            {'id': 16, 'type': 'tf', 'text': 'Câu 16. Hànzì / 汉字 (Hình ảnh mô tả: Bảng chữ cái tiếng Anh từ A đến Z)', 'correct': 'Sai (✗)', 'explanation': 'Bảng chữ cái tiếng Anh không phải là chữ Hán "汉字". Chọn Sai (✗).'},
            {'id': 17, 'type': 'tf', 'text': 'Câu 17. xīngqīyī / 星期一 (Hình ảnh mô tả: Khối gỗ ghép chữ "HAPPY MONDAY")', 'correct': 'Đúng (✓)', 'explanation': 'Monday chính là Thứ Hai "星期一". Chọn Đúng (✓).'},
            {'id': 18, 'type': 'tf', 'text': 'Câu 18. xuéxiào / 学校 (Hình ảnh mô tả: Ngôi trường khang trang có học sinh đi vào)', 'correct': 'Sai (✗)', 'explanation': 'Mặc dù hình ảnh giống trường học, đáp án gốc từ Nhà xuất bản phán đoán câu này là Sai (✗).'},
            {'id': 19, 'type': 'tf', 'text': 'Câu 19. qǐng zuò / 请坐 (Hình ảnh mô tả: Người mặc comple kéo ghế mời ngồi)', 'correct': 'Đúng (✓)', 'explanation': 'Động tác kéo ghế mời ngồi hoàn toàn khớp với cụm từ "请坐". Chọn Đúng (✓).'},
            {'id': 20, 'type': 'tf', 'text': 'Câu 20. xuéxí / 学习 (Hình ảnh mô tả: Cậu bé đọc sách học bài chăm chỉ)', 'correct': 'Đúng (✓)', 'explanation': 'Hình ảnh cậu bé tự học bài chăm chỉ khớp hoàn toàn với động từ "学习". Chọn Đúng (✓).'},
            # Phần 2 (Câu 21-25): Phối hợp câu hỏi - câu trả lời
            {'id': 21, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 21. 他是哪国人？ / Tā shì nǎ guó rén? \n- Lựa chọn: A: 她叫玛丽。 | B: 他是我的朋友。 | C: 他是法国人。 | D: 我姓王。 | E: 我学习英语。', 'correct': 'C', 'explanation': 'Hỏi quốc tịch anh ấy: ghép với câu "Anh ấy là người Pháp" (他是法国人。 - C).'},
            {'id': 22, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 22. 她叫什么名字？ / Tā jiào shénme míngzi? \n- Lựa chọn: A: 她叫玛丽。 | B: 他是我的朋友。 | C: 他是法国人。 | D: 我姓王。 | E: 我学习英语。', 'correct': 'A', 'explanation': 'Hỏi tên cô ấy: ghép với câu "Cô ấy tên là Mary" (她叫玛丽。 - A).'},
            {'id': 23, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 23. 你学习什么？ / Nǐ xuéxí shénme? \n- Lựa chọn: A: 她叫玛丽。 | B: 他是我的朋友。 | C: 他是法国人. | D: 我姓王。 | E: 我学习英语。', 'correct': 'E', 'explanation': 'Hỏi bạn học gì: ghép với câu "Tôi học tiếng Anh" (我学习英语。 - E).'},
            {'id': 24, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 24. 他是谁？ / Tā shì shuí? \n- Lựa chọn: A: 她叫玛丽。 | B: 他是我的朋友。 | C: 他是法国人. | D: 我姓王。 | E: 我学习英语。', 'correct': 'B', 'explanation': 'Hỏi anh ấy là ai: ghép với câu "Anh ấy là bạn của tôi" (他是我的朋友。 - B).'},
            {'id': 25, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 25. 请问，您贵姓？ / Qǐngwèn, nín guìxìng? \n- Lựa chọn: A: 她叫玛丽。 | B: 他是我的朋友。 | C: 他是法国人. | D: 我姓王。 | E: 我学习英语。', 'correct': 'D', 'explanation': 'Hỏi họ lịch sự: ghép với câu "Tôi họ Vương" (我姓王。 - D).'},
            # Phần 3 (Câu 26-30): Điền từ vào chỗ trống
            {'id': 26, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 26. 我学习汉语，汉语不（  ）难。 \n[A: 叫 / jiào | B: 太 / tài | C: 美国 / Měiguó | D: 名字 / míngzi | E: 的 / de | F: 学校 / xuéxiào]', 'correct': 'B', 'explanation': 'Điền phó từ chỉ mức độ "太" để tạo nghĩa: "tiếng Hán không khó lắm".'},
            {'id': 27, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 27. 他是我的朋友，他是（  ）人。 \n[A: 叫 / jiào | B: 太 / tài | C: 美国 / Měiguó | D: 名字 / míngzi | E: 的 / de | F: 学校 / xuéxiào]', 'correct': 'C', 'explanation': 'Điền danh từ tên nước "美国" (Mỹ) để bổ nghĩa cho "人": "Anh ấy là người Mỹ".'},
            {'id': 28, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 28. 这是张老师，我（  ）汉语老师。 \n[A: 叫 / jiào | B: 太 / tài | C: 美国 / Měiguó | D: 名字 / míngzi | E: 的 / de | F: 学校 / xuéxiào]', 'correct': 'E', 'explanation': 'Điền trợ từ kết cấu "的" để biểu thị quan hệ sở hữu: "Đây là cô giáo Trương, giáo viên tiếng Trung của tôi".'},
            {'id': 29, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 29. 女：你（  ）什么名字？ 男：我叫张东。 \n[A: 叫 / jiào | B: 太 / tài | C: 美国 / Měiguó | D: 名字 / míngzi | E: 的 / de | F: 学校 / xuéxiào]', 'correct': 'A', 'explanation': 'Điền động từ "叫" (gọi là) dùng để hỏi tên: "Bạn tên là gì?".'},
            {'id': 30, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 30. 男：明天你去公园吗？ 女：不去, 我去（  ）。 \n[A: 叫 / jiào | B: 太 / tài | C: 美国 / Měiguó | D: 名字 / míngzi | E: 的 / de | F: 学校 / xuéxiào]', 'correct': 'F', 'explanation': 'Điền từ chỉ địa điểm "学校" (trường học) sau động từ đi "去": "Không đi, mình đến trường".'}
        ]
    },
    'bai_6': {
        'title': 'BÀI 6: ĐÂY LÀ THẦY GIÁO VƯƠNG (BÀI ÔN TẬP 1) / 这是王老师 (复习一)',
        'listening': [
            # Phần 1 (Câu 1-5): Phán đoán đúng/sai
            {'id': 1, 'type': 'tf', 'text': 'Câu 1. 明天见 / Míngtiān jiàn (Hình một nhóm học sinh đeo ba lô đang đi cùng nhau)', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '明天见 (Míngtiān jiàn - Hẹn gặp lại ngày mai)', 'explanation': 'Học sinh đi học về chào nhau "Hẹn gặp ngày mai", hình ảnh và nghĩa của từ hoàn toàn phù hợp.'},
            {'id': 2, 'type': 'tf', 'text': 'Câu 2. 星期六 / Xīngqīliù (Hình các khối chữ gỗ xếp thành chữ "SUNDAY")', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '星期六 (Xīngqīliù - Thứ Bảy)', 'explanation': '"Sunday" là Chủ Nhật, trong khi audio phát "星期六" (Thứ Bảy). Phán đoán Sai (×).'},
            {'id': 3, 'type': 'tf', 'text': 'Câu 3. 喝茶 / Hē chá (Hình một cô gái đang uống nước từ chiếc ly)', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '喝茶 (Hē chá - Uống trà)', 'explanation': 'Hình ảnh cô gái uống nước lọc thông thường không giống uống trà, đáp án chuẩn của sách là Sai (✗).'},
            {'id': 4, 'type': 'tf', 'text': 'Câu 4. 去公园 / Qù gōngyuán (Hình một người phụ nữ đang đẩy xe mua sắm trong siêu thị)', 'audio_part': 1, 'correct': 'Sai (✗)', 'script': '去公园 (Qù gōngyuán - Đi công viên)', 'explanation': 'Hình ảnh người phụ nữ đang đi siêu thị mua sắm chứ không phải công viên. Phán đoán Sai (✗).'},
            {'id': 5, 'type': 'tf', 'text': 'Câu 5. 三个人 / Sān gè rén (Hình ba bạn học sinh đang cầm sách cùng nhau học tập)', 'audio_part': 1, 'correct': 'Đúng (✓)', 'script': '三个人 (Sān gè rén - Ba người)', 'explanation': 'Hình ảnh có chính xác 3 người đang học bài nhóm. Phán đoán Đúng (✓).'},
            # Phần 2 (Câu 6-10): Nghe đối thoại, nối hình
            {'id': 6, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 6: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'F', 'script': '男：今天星期几？\n女：今天星期三。\n(Nam: Hôm nay thứ mấy?\nNữ: Hôm nay là thứ Tư.)', 'explanation': 'Hội thoại hỏi thứ mấy và trả lời thứ tư (星期三), khớp tờ lịch thứ Tư ở hình F.'},
            {'id': 7, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 7: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'A', 'script': '男：妈，我去学校了。再见！\n女：好，再见！\n(Nam: Mẹ ơi con đi học đây. Tạm biệt mẹ!\nNữ: Được, tạm biệt con!)', 'explanation': 'Hội thoại chào tạm biệt mẹ để đi học của cậu bé, khớp hình A.'},
            {'id': 8, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 8: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'B', 'script': '女：您好，您想喝点儿什么？\n男：一杯茶，谢谢。\n(Nữ: Kính chào quý khách, quý khách muốn dùng thức uống gì?\nNam: Cho tôi một ly trà, cảm ơn.)', 'explanation': 'Hội thoại gọi trà của khách hàng và người phục vụ bàn, khớp hình B.'},
            {'id': 9, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 9: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'D', 'script': '男：她是谁？\n女：她是我的汉语老师。\n(Nam: Cô ấy là ai?\nNữ: Cô ấy là giáo viên tiếng Hán của tôi.)', 'explanation': 'Giới thiệu giáo viên tiếng Hán của tôi (汉语老师), khớp với hình cô giáo đứng cạnh bảng đen hình D.'},
            {'id': 10, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 10: Nghe đối thoại và chọn hình ảnh phù hợp (A - F)', 'audio_part': 2, 'correct': 'E', 'script': '男：这两个人是谁？\n女：这是我爸爸和妈妈。\n(Nam: Hai người này là ai?\nNữ: Đây là bố và mẹ tôi.)', 'explanation': 'Hội thoại giới thiệu bố mẹ của mình, khớp với cặp vợ chồng cao tuổi ở hình E.'},
            # Phần 3 (Câu 11-15): Nghe và chọn đáp án đúng nhất
            {'id': 11, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 11: Chọn đáp án đúng cho câu hỏi: 今天星期几？ (Hôm nay thứ mấy?) \n- A: 星期五 / xīngqīwǔ \n- B: 星期六 / xīngqīliù \n- C: 星期天 / xīngqītiān', 'audio_part': 3, 'correct': 'C', 'script': '明天星期一，我去学校。\n问：今天星期几？\n(Ngày mai thứ hai, tôi đi học.\nHỏi: Hôm nay thứ mấy?)', 'explanation': 'Vì ngày mai là thứ Hai (星期一), nên hôm nay bắt buộc phải là Chủ Nhật (星期天). Chọn C.'},
            {'id': 12, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 12: Chọn đáp án đúng cho câu hỏi: 那个人是谁？ (Người đó là ai?) \n- A: 李红 / Lǐ Hóng \n- B: 他的老师 / tā de lǎoshī \n- C: 李红的妈妈 / Lǐ Hóng de māma', 'audio_part': 3, 'correct': 'B', 'script': '这个人不是李红的妈妈，她是我的老师。\n问：那个人是谁？\n(Người này không phải mẹ của Lý Hồng, cô ấy là giáo viên của tôi.\nHỏi: Người đó là ai?)', 'explanation': 'Audio bác bỏ việc người này là mẹ Lý Hồng, và khẳng định cô ấy là giáo viên của tôi (我的老师). Chọn B.'},
            {'id': 13, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 13: Chọn đáp án đúng cho câu hỏi: 他们明天在哪儿见面？ (Ngày mai họ gặp nhau ở đâu?) \n- A: 学校 / xuéxiào \n- B: 公园 / gōngyuán \n- C: 银行 / yínháng', 'audio_part': 3, 'correct': 'A', 'script': '我们明天在学校见面。\n问：他们明天在哪儿见面？\n(Ngày mai chúng ta gặp nhau ở trường học.\nHỏi: Họ gặp nhau ở đâu vào ngày mai?)', 'explanation': 'Nhân vật nói sẽ gặp nhau ở trường học (学校). Chọn A.'},
            {'id': 14, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 14: Chọn đáp án đúng cho câu hỏi: 谁是老师？ (Ai là giáo viên?) \n- A: 他爸爸 / tā bàba \n- B: 他朋友 / tā péngyou \n- C: 彼の老师 / tā de lǎoshī', 'audio_part': 3, 'correct': 'B', 'script': '这是我朋友，她是小学老师。\n问：谁是老师？\n(Đây là bạn của tôi, cô ấy là giáo viên tiểu học.\nHỏi: Ai là giáo viên?)', 'explanation': 'Nhân vật giới thiệu bạn mình (我朋友) là giáo viên tiểu học. Chọn B.'},
            {'id': 15, 'type': 'mc', 'options': ['A', 'B', 'C'], 'text': 'Câu 15: Chọn đáp án đúng cho câu hỏi: 他想喝什么？ (Anh ấy muốn uống gì?) \n- A: 茶 / chá \n- B: 咖啡 / kāfēi \n- C: 水 / shuǐ', 'audio_part': 3, 'correct': 'A', 'script': '他想喝茶，你呢？\n问：他想喝什么？\n(Anh ấy muốn uống trà, còn cậu?\nHỏi: Anh ấy muốn uống gì?)', 'explanation': 'Nhân vật nam nói rõ "Anh ấy muốn uống trà" (想喝茶). Chọn A.'}
        ],
        'reading': [
            # Phần 1 (Câu 16-20): Xem từ vựng phán đoán hình đúng sai
            {'id': 16, 'type': 'tf', 'text': 'Câu 16. kāfēi / 咖啡 (Hình ảnh mô tả: Một chiếc tách cà phê bốc khói đặt trên đĩa)', 'correct': 'Đúng (✓)', 'explanation': 'Tách cà phê bốc khói rất đặc trưng và khớp hoàn toàn với "咖啡". Chọn Đúng (✓).'},
            {'id': 17, 'type': 'tf', 'text': 'Câu 17. qù / 去 (Hình ảnh mô tả: Một người đang ngồi thư giãn trên chiếc ghế văn phòng xoay)', 'correct': 'Sai (✗)', 'explanation': 'Hành động ngồi thư giãn trên ghế không biểu đạt ý nghĩa của động từ đi "去". Chọn Sai (✗).'},
            {'id': 18, 'type': 'tf', 'text': 'Câu 18. sān / 三 (Hình ảnh mô tả: 3 quả táo đỏ mọng nước)', 'correct': 'Đúng (✓)', 'explanation': 'Có chính xác 3 quả táo đỏ tương ứng với số 3 "三". Chọn Đúng (✓).'},
            {'id': 19, 'type': 'tf', 'text': 'Câu 19. zàijiàn / 再见 (Hình ảnh mô tả: Hai người mặc đồ công sở bắt tay chào hỏi nhau mỉm cười)', 'explanation': 'Hành động bắt tay khi mới gặp/chào hỏi không biểu thị ý tạm biệt "再见". Chọn Sai (✗).', 'correct': 'Sai (✗)'},
            {'id': 20, 'type': 'tf', 'text': 'Câu 20. shū / 书 (Hình ảnh mô tả: Một quyển sách dày có ghi chữ "ALWAYS WELCOME")', 'correct': 'Đúng (✓)', 'explanation': 'Hình ảnh quyển sách dày khớp hoàn toàn với danh từ "书". Chọn Đúng (✓).'},
            # Phần 2 (Câu 21-25): Phối hợp câu hỏi - câu trả lời
            {'id': 21, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 21. 你喝点儿什么？ / Nǐ hē diǎnr shénme? \n- Lựa chọn: A: 我去邮局。 | B: 这是英文杂志。 | C: 今天星期四。 | D: 我喝咖啡。 | E: 那是我妈妈的书。', 'correct': 'D', 'explanation': 'Hỏi về đồ uống: ghép với câu "Tôi uống cà phê" (我喝咖啡。 - D).'},
            {'id': 22, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 22. 你去哪儿？ / Nǐ qù nǎr? \n- Lựa chọn: A: 我去邮局。 | B: 这是英文杂志。 | C: 今天星期四。 | D: 我喝咖啡。 | E: 那是我妈妈的书。', 'correct': 'A', 'explanation': 'Hỏi về địa điểm đi đâu: ghép với câu "Tôi đi bưu điện" (我去邮局。 - A).'},
            {'id': 23, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 23. 这是什么杂志？ / Zhè shì shénme zázhì? \n- Lựa chọn: A: 我去邮局。 | B: 这是英文杂志。 | C: 今天星期四。 | D: 我喝咖啡。 | E: 那是我妈妈的书。', 'correct': 'B', 'explanation': 'Hỏi về tạp chí gì: ghép với câu "Đây là tạp chí tiếng Anh" (这是英文杂志。 - B).'},
            {'id': 24, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 24. 今天星期几？ / Jīntiān xīngqī jǐ? \n- Lựa chọn: A: 我去邮局。 | B: 这是英文杂志。 | C: 今天星期四。 | D: 我喝咖啡。 | E: 那是我妈妈的书。', 'correct': 'C', 'explanation': 'Hỏi về thứ ngày: ghép với câu "Hôm nay là Thứ Năm" (今天星期四。 - C).'},
            {'id': 25, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E'], 'text': 'Câu 25. 那是谁的书？ / Nà shì shuí de shū? \n- Lựa chọn: A: 我去邮局。 | B: 这是英文杂志。 | C: 今天星期四。 | D: 我喝咖啡。 | E: 那是我妈妈的书。', 'correct': 'E', 'explanation': 'Hỏi về chủ sở hữu sách: ghép với câu "Đó là sách của mẹ tôi" (那是我妈妈的书。 - E).'},
            # Phần 3 (Câu 26-30): Điền từ vào chỗ trống
            {'id': 26, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 26. 这是（  ）的信？ \n[A: 忙 / máng | B: 谁 / shuí | C: 学校 / xuéxiào | D: 名字 / míngzi | E: 进 / jìn | F: 星期天 / xīngqītiān]', 'correct': 'B', 'explanation': 'Chọn đại từ nghi vấn chỉ người "谁" (ai): "Đây là thư của ai?".'},
            {'id': 27, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 27. 我妈妈是老师, 她很（  ）。 \n[A: 忙 / máng | B: 谁 / shuí | C: 学校 / xuéxiào | D: 名字 / míngzi | E: 进 / jìn | F: 星期天 / xīngqītiān]', 'correct': 'A', 'explanation': 'Chọn tính từ "忙" (bận rộn): "Mẹ tôi là giáo viên, mẹ rất bận".'},
            {'id': 28, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 28. 昨天（  ）, 我去公园。 \n[A: 忙 / máng | B: 谁 / shuí | C: 学校 / xuéxiào | D: 名字 / míngzi | E: 进 / jìn | F: 星期天 / xīngqītiān]', 'correct': 'F', 'explanation': 'Chọn danh từ thời gian "星期天" (Chủ Nhật): "Hôm qua là Chủ Nhật, tôi đi công viên".'},
            {'id': 29, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 29. 女：你去哪儿？ | 男：我去（  ）。 \n[A: 忙 / máng | B: 谁 / shuí | C: 学校 / xuéxiào | D: 名字 / míngzi | E: 进 / jìn | F: 星期天 / xīngqītiān]', 'correct': 'C', 'explanation': 'Chọn địa điểm phù hợp "学校" (trường học): "Em đi đâu? - Em đến trường".'},
            {'id': 30, 'type': 'mc', 'options': ['A', 'B', 'C', 'D', 'E', 'F'], 'text': 'Câu 30. 男：你好！请（  ）！| 女：你的信。 \n[A: 忙 / máng | B: 谁 / shuí | C: 学校 / xuéxiào | D: 名字 / míngzi | E: 进 / jìn | F: 星期天 / xīngqītiān]', 'correct': 'E', 'explanation': 'Chọn động từ "进" (vào): "Chào anh! Xin mời vào! - Thư của anh này".'}
        ]
    }
}

# ==========================================================
# 3. TIÊU ĐỀ CHÍNH & PHẦN GIAO DIỆN CHUNG
# ==========================================================
st.markdown("<h1 class='main-title'>BÀI TẬP GIÁO TRÌNH HÁN NGỮ (1)</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>Chúc các bạn làm bài vui và hiệu quả nha!</h3>", unsafe_allow_html=True)

# Lấy tên học sinh lưu vào session_state toàn cục
student_name = st.sidebar.text_input("📝 Họ và tên học sinh (Bắt buộc):", value=st.session_state.get("student_name", ""))
st.session_state.student_name = student_name

# Thiết lập tabs: Bài mới nhất luôn ở bên trái ngoài cùng (Bài 8 -> Bài 7 -> Bài 6)
tabs = st.tabs(["📚 BÀI 8", "📚 BÀI 7", "📚 BÀI 6"])

# ==========================================================
# 4. VÒNG LẶP RENDER TỪNG TAB BÀI HỌC
# ==========================================================
lessons_mapping = [('bai_8', tabs[0]), ('bai_7', tabs[1]), ('bai_6', tabs[2])]

for lesson_id, tab in lessons_mapping:
    with tab:
        lesson_data = QUESTIONS[lesson_id]
        st.markdown(f"<div class='lesson-banner'>{lesson_data['title']}</div>", unsafe_allow_html=True)
        
        # Biến trạng thái nộp bài của bài cụ thể
        is_submitted = st.session_state[f"submitted_{lesson_id}"]
        scores = st.session_state[f"scores_{lesson_id}"]
        
        # --------------------------------------------------
        # A. PHẦN NGHE (15 CÂU)
        # --------------------------------------------------
        st.subheader("I. 听力 / PHẦN NGHE (15 câu)")
        
        # Audio cho Phần 1 (Câu 1-5)
        st.markdown("**🔊 Phần 1 (Câu 1 - 5):** Nghe từ/ngữ và phán đoán đúng (✓) / sai (✗)")
        audio_file_1 = f"B{lesson_id.split('_')[1]}-1.mp3"
        try:
            st.audio(audio_file_1, format="audio/mp3")
        except Exception:
            st.warning(f"Chưa tìm thấy file âm thanh {audio_file_1} trong thư mục. Vui lòng thêm file để học sinh nghe.")
        
        for q in lesson_data['listening'][0:5]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown(f"<div class='quiz-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q['text']}**")
            
            # Gán giá trị mặc định của Widget từ session_state hiện tại để tránh rerun bị reset
            selected_option = st.radio(
                "Lựa chọn của bạn:",
                ["Chưa chọn", "Đúng (✓)", "Sai (✗)"],
                index=["Chưa chọn", "Đúng (✓)", "Sai (✗)"].index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            # Lưu lại trạng thái
            st.session_state[q_key] = selected_option
            
            # Nếu đã nộp bài, hiện kết quả câu đó ngay
            if is_submitted:
                is_correct = (selected_option == q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Script Nghe & Giải thích"):
                    st.markdown(f"**Script nghe:**\n{q['script']}")
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # Audio cho Phần 2 (Câu 6-10)
        st.markdown("**🔊 Phần 2 (Câu 6 - 10):** Nghe hội thoại và ghép hình")
        audio_file_2 = f"B{lesson_id.split('_')[1]}-2.mp3"
        try:
            st.audio(audio_file_2, format="audio/mp3")
        except Exception:
            st.warning(f"Chưa tìm thấy file âm thanh {audio_file_2} trong thư mục.")
            
        for q in lesson_data['listening'][5:10]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q['text']}**")
            
            selected_option = st.selectbox(
                "Nối với hình (A - F):",
                ["Chưa chọn"] + q['options'],
                index=(["Chưa chọn"] + q['options']).index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            st.session_state[q_key] = selected_option
            
            if is_submitted:
                is_correct = (selected_option == q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Script Nghe & Giải thích"):
                    st.markdown(f"**Script nghe:**\n{q['script']}")
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # Audio cho Phần 3 (Câu 11-15)
        st.markdown("**🔊 Phần 3 (Câu 11 - 15):** Nghe câu hỏi và chọn đáp án chính xác")
        audio_file_3 = f"B{lesson_id.split('_')[1]}-3.mp3"
        try:
            st.audio(audio_file_3, format="audio/mp3")
        except Exception:
            st.warning(f"Chưa tìm thấy file âm thanh {audio_file_3} trong thư mục.")
            
        for q in lesson_data['listening'][10:15]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
            st.markdown(q['text'])
            
            selected_option = st.radio(
                "Chọn đáp án đúng (A/B/C):",
                ["Chưa chọn"] + q['options'],
                index=(["Chưa chọn"] + q['options']).index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            st.session_state[q_key] = selected_option
            
            if is_submitted:
                is_correct = (selected_option == q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Script Nghe & Giải thích"):
                    st.markdown(f"**Script nghe:**\n{q['script']}")
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # --------------------------------------------------
        # B. PHẦN ĐỌC (15 CÂU)
        # --------------------------------------------------
        st.subheader("II. 阅读 / PHẦN ĐỌC (15 câu)")
        
        # Phần Đọc 1 (Câu 16-20)
        st.markdown("**📖 Phần 1 (Câu 16 - 20):** Xem từ ngữ và phán đoán đúng (✓) / sai (✗)")
        for q in lesson_data['reading'][0:5]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q['text']}**")
            
            selected_option = st.radio(
                "Lựa chọn của bạn:",
                ["Chưa chọn", "Đúng (✓)", "Sai (✗)"],
                index=["Chưa chọn", "Đúng (✓)", "Sai (✗)"].index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            st.session_state[q_key] = selected_option
            
            if is_submitted:
                is_correct = (selected_option == q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Giải thích chi tiết"):
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # Phần Đọc 2 (Câu 21-25)
        st.markdown("**📖 Phần 2 (Câu 21 - 25):** Phối hợp câu hỏi và câu trả lời")
        for q in lesson_data['reading'][5:10]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q['text']}**")
            
            selected_option = st.selectbox(
                "Nối đáp án đúng:",
                ["Chưa chọn"] + q['options'],
                index=(["Chưa chọn"] + q['options']).index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            st.session_state[q_key] = selected_option
            
            if is_submitted:
                is_correct = (selected_option == q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Giải thích chi tiết"):
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # Phần Đọc 3 (Câu 26-30)
        st.markdown("**📖 Phần 3 (Câu 26 - 30):** Điền từ thích hợp vào khoảng trống")
        for q in lesson_data['reading'][10:15]:
            q_key = f"ans_{lesson_id}_{q['id']}"
            if q_key not in st.session_state:
                st.session_state[q_key] = "Chưa chọn"
                
            st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q['text']}**")
            
            selected_option = st.selectbox(
                "Chọn từ điền trống (A - F):",
                ["Chưa chọn"] + q['options'],
                index=(["Chưa chọn"] + q['options']).index(st.session_state[q_key]),
                key=f"widget_{lesson_id}_{q['id']}",
                disabled=is_submitted
            )
            st.session_state[q_key] = selected_option
            
            if is_submitted:
                is_correct = (selected_option == q['correct'])
                if is_correct:
                    st.success("🎉 Chính xác!")
                else:
                    st.error(f"❌ Chưa đúng! Đáp án đúng: **{q['correct']}**")
                with st.expander("📖 Xem Giải thích chi tiết"):
                    st.markdown(f"**Giải thích:** {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)

        # --------------------------------------------------
        # C. NÚT NỘP BÀI VÀ QUY TRÌNH CHẤM ĐIỂM
        # --------------------------------------------------
        st.write("---")
        if not is_submitted:
            if st.button("🚀 Nộp bài tập này", key=f"submit_btn_{lesson_id}"):
                if not student_name.strip():
                    st.error("⚠️ Bạn ơi, vui lòng nhập 'Họ và tên' ở thanh bên (Sidebar) trước khi nộp bài nhé!")
                else:
                    # Tính điểm
                    listening_score = 0
                    for q in lesson_data['listening']:
                        ans = st.session_state.get(f"ans_{lesson_id}_{q['id']}", "Chưa chọn")
                        if ans == q['correct']:
                            listening_score += 1
                            
                    reading_score = 0
                    for q in lesson_data['reading']:
                        ans = st.session_state.get(f"ans_{lesson_id}_{q['id']}", "Chưa chọn")
                        if ans == q['correct']:
                            reading_score += 1
                            
                    total_score = listening_score + reading_score
                    
                    st.session_state[f"scores_{lesson_id}"] = {
                        'listening': listening_score,
                        'reading': reading_score,
                        'total': total_score
                    }
                    st.session_state[f"submitted_{lesson_id}"] = True
                    
                    # Gửi Webhook tới Google Sheet
                    payload = {
                        "timestamp": (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
                        "student_name": student_name,
                        "lesson_title": lesson_data['title'],
                        "listening_score": f"{listening_score}/15",
                        "reading_score": f"{reading_score}/15",
                        "total_score": f"{total_score}/30"
                    }
                    
                    webhook_success = False
                    if WEBHOOK_URL and "YOUR_MACRO_ID" not in WEBHOOK_URL:
                        try:
                            res = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=10)
                            if res.status_code == 200:
                                webhook_success = True
                        except Exception:
                            pass
                    
                    # Hiện kết quả thành công cho học sinh
                    st.success("🎉 Chúc mừng bạn đã làm xong bài tập nha! Điểm đã được gửi về cho cô Bảo Ngọc!")
                    st.balloons()
                    
                    if not webhook_success:
                        st.warning("⚠️ Hệ thống chưa đồng bộ được với Google Sheet, bạn vui lòng chụp màn hình kết quả này gửi cho cô nhé!")
                        
                    # Rerun để hiển thị chi tiết đáp án và giải thích
                    st.rerun()
        else:
            # Hiển thị điểm số đã lưu khi đã nộp bài
            st.info(f"📍 Bạn đã nộp bài tập này rồi!")
            st.markdown(f"### 🏆 Kết quả của bạn:")
            st.markdown(f"👤 **Học sinh**: {student_name}")
            st.markdown(f"🎧 **Điểm phần nghe**: `{scores['listening']}/15`")
            st.markdown(f"📖 **Điểm phần đọc**: `{scores['reading']}/15`")
            st.markdown(f"🌟 **Tổng điểm**: `{scores['total']}/30`")
            
            if st.button("🔄 Làm lại bài tập này", key=f"reset_btn_{lesson_id}"):
                # Reset answers and submission status
                st.session_state[f"submitted_{lesson_id}"] = False
                st.session_state[f"scores_{lesson_id}"] = None
                for q in lesson_data['listening'] + lesson_data['reading']:
                    st.session_state[f"ans_{lesson_id}_{q['id']}"] = "Chưa chọn"
                st.rerun()

# ==========================================================
# 5. FOOTER ỨNG DỤNG
# ==========================================================
st.markdown("<div class='footer'>❤️ Giáo viên phụ trách: 黄宝玉老师 (Cô Bảo Ngọc) ❤️</div>", unsafe_allow_html=True)
