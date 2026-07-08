# data/ch5/events_ch5_bai20.py

EVENTS = [
    # ================= GIAI ĐOẠN ĐƠN CỰC (1991 - 2000) =================
    {
        "id": "E_CH5_DonCuc_HinhThanh",
        "label": "Xu hướng đơn cực cuối thế kỷ XX",
        "where": "L_Global", "when": "P_1991_2000",
        "org_weighted": [("L_My", 10)],
        "cause_direct": "Sự sụp đổ của Liên Xô và trật tự hai cực I-an-ta.",
        "content": "Thế giới định hình theo xu hướng đơn cực, Mỹ là siêu cường duy nhất. Các cường quốc khác chưa phát sinh bất đồng gay gắt.",
        "concepts_weighted": [("C_TratTuDonCuc", 10)]
    },

    # ================= CÁC CÚ SỐC ĐẦU THẾ KỶ XXI (LÀM SUY YẾU MỸ) =================
    {
        "id": "E_CH5_KhungBo11_9",
        "label": "Sự kiện khủng bố 11/9/2001",
        "aliases": "Sự kiện 11/9",
        "where": "L_My", "when": "P_Tu2001",
        "org_weighted": [("O_AlQaeda", 10)],
        "content": "Al-Qaeda tấn công tháp đôi Thương mại và Bộ Quốc phòng Mỹ, gây thiệt hại nặng nề.",
        "result": "Mỹ lấy cớ chống khủng bố để phát động chiến tranh can thiệp vào Afghanistan và Iraq, phản ánh tham vọng thiết lập trật tự đơn cực."
    },
    {
        "id": "E_CH5_KhungHoangTaiChinh2008",
        "label": "Khủng hoảng tài chính 2008-2009",
        "where": "L_Global", "when": "P_Tu2001",
        "org_weighted": [("L_My", 10)],
        "content": "Khủng hoảng kinh tế toàn cầu bùng nổ.",
        "result": "Làm suy giảm đáng kể sức mạnh kinh tế - quân sự của Mỹ, thúc đẩy sự cáo chung của xu hướng đơn cực."
    },

    # ================= XU HƯỚNG ĐA CỰC (Từ thập niên 2010s) =================
    {
        "id": "E_CH5_DaCuc_HinhThanh",
        "label": "Xu hướng đa cực đầu thế kỷ XXI",
        "where": "L_Global", "when": "P_Tu2001",
        "content": """+ Trung Quốc: Trỗi dậy mạnh mẽ, thực hiện chiến lược 'Vành đai, con đường'.
+ Nga: Khôi phục vị thế, chống lại sự mở rộng về phía Đông của NATO.
+ EU, Nhật Bản, Ấn Độ: Tham gia vào quá trình cạnh tranh quyền lực.""",
        "achievements": "Xu hướng đa cực dần được thể hiện rõ với nhiều trung tâm cạnh tranh, chấm dứt thời kỳ Mỹ 'một mình một ngựa'.",
        "concepts_weighted": [("C_TratTuDaCuc", 10), ("C_VanhDaiConDuong", 8)]
    }
]