# data/concepts.py

EVENTS = [
    {
        "id": "E_XayDungCNXH_LienXo_1922_1945",
        "label": "Liên Xô xây dựng CNXH (1922-1945)",
        "aliases": "Thành tựu Liên Xô|Xây dựng chủ nghĩa xã hội ở Liên Xô|Liên Xô 1922-1945",
        "where": "L_LienXo", "when": "P_1922_1945",
        "context": "Tháng 12/1922, Liên bang Cộng hòa XHCN Xô viết (Liên Xô) chính thức thành lập.",
        "achievements": """
        + Về kinh tế: Năm 1937, Liên Xô đã trở thành cường quốc công nghiệp đứng đầu châu Âu và thứ 2 thế giới.
        + Về xã hội: Các giai cấp bóc lột bị xoá bỏ, chỉ còn công nhân, nông dân tập thể và trí thức.
        + Về văn hóa-giáo dục: xoá nạn mù chữ, hoàn thành phổ cập THCS ở thành phố.""",
        
        "limitations": """
        - Chưa chú trọng đúng mức đến nông nghiệp và công nghiệp nhẹ.
        - Vi phạm nguyên tắc tự nguyện trong tập thể hóa."""
    },
    {
        "id": "E_ThanhLapQuocTeCongSan",
        "label": "Sự thành lập Quốc tế Cộng sản",
        "aliases": "Quốc tế Cộng sản|Quốc tế thứ ba|Comintern|Thành lập Quốc tế thứ 3",
        "where": "L_Moscow", "when": "P_1918_1923",
        "who_weighted": [("Pe_Lenin", 10)],
        "org_weighted": [("O_Comintern", 10), ("O_Bolshevik", 8)],
        "cause": "Phong trào cách mạng thế giới dâng cao, cần tổ chức quốc tế thống nhất để lãnh đạo.",
        "content": "Thành lập 3/1919 tại Mát-xcơ-va. Đề ra đường lối cho cách mạng thế giới.",
        "result": "Trở thành bộ tham mưu của phong trào công nhân toàn cầu. Tự giải tán năm 1943."
    },
    {
        "id": "E_KhungHoangKinhTe_1929_1933",
        "label": "Đại suy thoái kinh tế 1929-1933",
        "aliases": "Đại suy thoái|Khủng hoảng kinh tế 1929-1933|Khủng hoảng thừa 1929-1933|Khủng hoảng kinh tế thế giới",
        "where": "L_My", "when": "P_1929_1933",
        "context": "Giai đoạn 1924-1929, kinh tế tư bản phát triển phồn vinh, sản xuất ồ ạt.",
        "cause": "Sản xuất ồ ạt, sức mua không tăng tương ứng -> Khủng hoảng thừa.",
        "content": "Bùng nổ 10/1929 ở Mỹ rồi lan ra toàn thế giới tư bản. Đình đốn công nghiệp, tài chính.",
        "result": "Hàng triệu người thất nghiệp. Dẫn đến sự xuất hiện của chủ nghĩa phát xít ở Đức, Italia, Nhật.",
        "concepts_weighted": [("C_KhungHoangKinhTe", 10)]
    },
    {
        "id": "E_PhatXitHoa_ChauAu_1929_1933",
        "label": "Châu Âu hình thành chủ nghĩa phát xít",
        "aliases": "Phát xít hóa châu Âu|Chủ nghĩa phát xít ở châu Âu|Sự hình thành phe Phát xít",
        "where": "L_Europe", "when": "P_1929_1933",
        "who_weighted": [("Pe_Hitler", 10), ("Pe_Mussolini", 9)],
        "org_weighted": [("O_DangQuocXa", 10), ("O_PhePhatXit", 9)],
        "cause": "Khủng hoảng 1929-1933. Các nước thiếu thuộc địa (Đức, Ý) muốn dùng vũ lực chia lại thế giới.",
        "content": "Ý: Mussolini lập độc tài (1925). Đức: Hitler làm Quốc trưởng (1934), tái vũ trang.",
        "result": "Hình thành liên minh phát xít Đức-Ý (1936), đẩy nhân loại đến bờ vực chiến tranh.",
        "concepts_weighted": [("C_ChuNghiaPhatXit", 10), ("C_PhatXitHoa", 10)]
    },
    {
        "id": "E_NhatBan_PhatXitHoa_1933_1945",
        "label": "Nhật Bản phát xít hóa và bành trướng",
        "aliases": "Phát xít Nhật|Nhật Bản phát xít hóa|Quân phiệt Nhật|Nhật Bản xâm lược",
        "where": "L_NhatBan", "when": "P_1933_1939",
        "cause": "Khủng hoảng 1929-1933. Giới quân phiệt muốn mở rộng lãnh thổ.",
        "content": "Quân phiệt hóa bộ máy nhà nước. Xâm chiếm Mãn Châu (1931), mở rộng xâm lược Trung Quốc (1937).",
        "result": "Trở thành lò lửa chiến tranh ở châu Á - Thái Bình Dương.",
        "concepts_weighted": [("C_PhatXitHoa", 10),("C_ChuNghiaPhatXit", 10), ("C_ChienTranhPhiNghia", 9)]
    },
    {
        "id": "E_WWII_NguyenNhan_TongQuat",
        "label": "Nguyên nhân bùng nổ CTTG 2",
        "aliases": "Chiến tranh thế giới lần thứ 2|Nguyên nhân Chiến tranh thế giới thứ hai|Nguyên nhân CTTG 2|Tại sao CTTG 2 bùng nổ",
        "where": "L_Europe", "when": "P_1933_1939",
        "cause_deep": "Kinh tế tư bản phát triển không đều. Khủng hoảng 1929-1933 tạo điều kiện cho phát xít nắm quyền.",
        "cause_direct": "Chính sách thỏa hiệp, nhượng bộ của phương Tây nhằm chĩa mũi nhọn vào Liên Xô đã dung túng phát xít.",
        "concepts_weighted": [("C_HeThongVersaillesWashington", 9), ("C_ChinhSachThoaHiep", 10), ("C_ChuNghiaPhatXit", 10)]
    },
    {
        "id": "E_WWII_GiaiDoan1_1939_1941",
        "label": "CTTG 2 bùng nổ và lan rộng (1939-1941)",
        "aliases": "Chiến tranh thế giới lần thứ 2|Giai đoạn 1 CTTG 2|Chiến tranh thế giới thứ hai 1939-1941|CTTG 2 bùng nổ|Giai đoạn 1 Chiến tranh thế giới thứ 2",
        "where": "L_Europe", "when": "P_WWII_GiaiDoan1",
        "org_weighted": [("O_PhePhatXit", 10),
                         ("O_QuanPhietNhat", 9)],
        "content": "9/1939: Đức đánh Ba Lan. 5/1940: Đánh Tây Âu. 6/1941: Tấn công Liên Xô. 12/1941: Nhật tấn công Trân Châu Cảng.",
        "result": "Chiến tranh lan rộng toàn thế giới. Phát xít tạm thời chiếm ưu thế."
    },
    {
        "id": "E_WWII_GiaiDoan2_1942_1945",
        "label": "Đồng minh phản công và kết thúc chiến tranh trong Chiến tranh Thế giới lần thứ 2",
        "aliases": "Chiến tranh thế giới lần thứ 2|Giai đoạn 2 CTTG 2|Đồng minh phản công|Chiến tranh kết thúc|CTTG 2 kết thúc|Giai đoạn 2 Chiến tranh Thế Giới lần thứ 2",
        "where": "L_Europe", "when": "P_WWII_GiaiDoan2",
        "org_weighted": [("O_LienHopQuoc_WW2", 10), 
                         ("O_PhePhatXit", 10),
                         ("O_QuanPhietNhat", 10)],
        "content": "Trận Xta-lin-grát (11/1942-2/1943) tạo bước ngoặt. Đổ bộ Noóc-măng-đi (6/1944). Chiến dịch Béc-lin (5/1945). Mỹ ném bom nguyên tử (8/1945).",
        "result": "Đức, Ý, Nhật đầu hàng không điều kiện. Chiến tranh kết thúc 15/8/1945."
    },
    {
        "id": "E_WWII_HauQua_YNGhia",
        "label": "Hậu quả và Ý nghĩa lịch sử của CTTG 2",
        "aliases": "Chiến tranh thế giới lần thứ 2|Hậu quả CTTG 2|Ý nghĩa Chiến tranh thế giới thứ hai|Hậu quả chiến tranh thế giới thứ hai",
        "where": "L_Europe", "when": "P_WWII_GiaiDoan2",
        "achievements": "Tính chính nghĩa của Đồng minh đánh bại phát xít. Cứu nhân loại khỏi thảm họa diệt vong.",
        "limitations": "Hậu quả tàn khốc: 60 triệu người chết, 90 triệu người bị thương, thiệt hại 4000 tỉ USD.",
        "result": "Làm thay đổi tương quan lực lượng tư bản, tạo điều kiện cho hệ thống XHCN ra đời và phong trào GPDT phát triển.",
        "concepts_weighted": [("C_ChienTranhPhiNghia", 8), ("C_ChienTranhChinhNghia", 8)]
    }
]



# data/events_documents.py

DOCUMENTS = [
    {
        "id": "D_NEP_1921",
        "label": "Chính sách kinh tế mới 1921 (NEP)",
        "aliases": "Chính sách kinh tế mới|NEP|Chính sách NEP|Kinh tế mới|Chế độ thuế lương thực",
        "where": "L_Nga", "when": "P_1918_1923",
        "who_weighted": [("Pe_Lenin", 10)], 
        "org_weighted": [("O_Bolshevik", 9)],
        "context": "Sau CM tháng Mười (1917), Nga Xô viết dùng 'Cộng sản thời chiến' để chống thù trong giặc ngoài.",
        "cause": "Chiến tranh kết thúc. Chính sách 'Cộng sản thời chiến' kìm hãm kinh tế, gây khủng hoảng.",
        "content": "Thay trưng thu bằng thuế lương thực; tự do buôn bán; tư nhân mở xí nghiệp nhỏ; gọi vốn nước ngoài.",
        "result": "Nước Nga Xô viết phục hồi kinh tế, đời sống nhân dân cải thiện.",
        "concepts_weighted": [("C_KinhTeThiTruong", 10)] 
    },
    {
        "id": "D_NewDeal_1932",
        "label": "Chính sách mới (New Deal)",
        "aliases": "Chính sách mới|New Deal|Thỏa thuận mới|Chính sách của Ru-dơ-ven",
        "where": "L_My", "when": "P_1929_1933",
        "who_weighted": [("Pe_Roosevelt", 10)],
        "context": "Nước Mỹ lâm vào Đại suy thoái kinh tế 1929-1933.",
        "cause": "Khủng hoảng tàn phá nền kinh tế, hàng triệu người thất nghiệp, nguy cơ sụp đổ tư bản chủ nghĩa.",
        "content": "Nhà nước can thiệp mạnh vào kinh tế, ban hành các đạo luật phục hồi sản xuất, giải quyết thất nghiệp.",
        "result": "Cứu vãn nền kinh tế, duy trì chế độ dân chủ tư sản, không bị phát xít hóa.",
        "concepts_weighted": [("C_KhungHoangKinhTe", 8), ("C_SuCanThiepCuaNhaNuoc", 10)]
    },
    {
        "id": "D_TuyenNgonLienHopQuoc_1942",
        "label": "Tuyên ngôn Liên hợp quốc chống phát xít",
        "aliases": "Tuyên ngôn Liên hợp quốc|Tuyên ngôn chống phát xít|Tuyên ngôn 1/1/1942",
        "where": "L_Washington", "when": "P_WWII_GiaiDoan2",
        "org_weighted": [("O_LienHopQuoc_WW2", 10)],
        "context": "Phe phát xít bành trướng mạnh mẽ trên toàn cầu.",
        "cause": "Cần tập hợp lực lượng của các quốc gia để tiêu diệt chủ nghĩa phát xít.",
        "content": "Ký ngày 1/1/1942 bởi 26 quốc gia (đứng đầu là Liên Xô, Mỹ, Anh).",
        "result": "Khối Đồng minh chính thức ra đời, tạo sức mạnh tổng hợp phản công.",
        "concepts_weighted": [("C_ChienTranhChinhNghia", 10)]
    }
]

MOVEMENTS = [
    {
        "id": "M_CachMang_ChauAu_1918_1923",
        "label": "Phong trào cách mạng ở châu Âu (1918-1923)",
        "aliases": "Cách mạng châu Âu|Phong trào cách mạng 1918-1923|Cách mạng 1918-1923|Phong trào cách mạng ở các nước tư bản châu Âu",
        "where": "L_Europe", "when": "P_1918_1923",
        "cause": "Do hậu quả nặng nề của Chiến tranh thế giới thứ nhất và tác động của Cách mạng tháng Mười Nga năm 1917, vào những năm 1918-1923, một phong trào cách mạng đã bùng nổ ở hầu khắp các nước tư bản châu Âu.",
        "content": "Nhân dân Béc-lin lật đổ quân chủ (11/1918). Bãi công lớn ở Anh, Pháp.",
        "result": "Dẫn đến sự thành lập hàng loạt Đảng Cộng sản (Đức, Pháp, Anh, Italia).",
        "concepts_weighted": [("C_KhuynhHuongVoSan", 10)]
    },
    {
        "id": "M_NguTu_1919",
        "label": "Phong trào Ngũ Tứ",
        "aliases": "Ngũ Tứ|Phong trào mùng 4 tháng 5|Cách mạng Ngũ Tứ",
        "where": "L_BacKinh", "when": "P_1918_1923",
        "cause": "Chống lại âm mưu xâu xé Trung Quốc của các đế quốc.",
        "content": "Bùng nổ 4/5/1919, lôi cuốn công nhân, trí thức tham gia.",
        "result": "Lan rộng cả nước, thúc đẩy sự ra đời của Đảng Cộng sản Trung Quốc (1921).",
        "concepts_weighted": [("C_KhuynhHuongVoSan", 8)]
    },
    {
        "id": "M_DauTranh_AnDo_Interwar",
        "label": "Phong trào đấu tranh giành độc lập ở Ấn Độ",
        "aliases": "Cách mạng Ấn Độ|Phong trào giải phóng dân tộc Ấn Độ|Đấu tranh giành độc lập Ấn Độ",
        "where": "L_AnDo", "when": "P_1918_1939",
        "who_weighted": [("Pe_Gandhi", 10)],
        "org_weighted": [("O_DangQuocDai", 9), ("O_DangCongSan_AnDo", 7)],
        "content": "Dưới sự lãnh đạo của Gan-đi, nhân dân đấu tranh đòi độc lập, tẩy chay hàng hoá của Anh.",
        "concepts_weighted": [("C_KhuynhHuongTuSan", 8), ("C_GiaiPhongDanToc", 10)]
    },
    {
        "id": "M_GiaiPhongDanToc_DongNamA_1918_1945",
        "label": "Phong trào GPDT Đông Nam Á",
        "aliases": "Giải phóng dân tộc Đông Nam Á|Cách mạng Đông Nam Á|Phong trào đấu tranh Đông Nam |Phong trào giải phóng dân tộc ở Đông Nam Á",
        "where": "L_DongNamA", "when": "P_1918_1945",
        "who_weighted": [("Pe_Sukarno", 8)],
        "org_weighted": [("O_DangDanToc_Indonesia", 8), ("O_VNQDD", 6)],
        "cause": "Ách thống trị bóc lột của chủ nghĩa thực dân phương Tây.",
        "content": "Phát triển theo 2 khuynh hướng (vô sản và tư sản). Lập mặt trận chống Nhật trong WWII.",
        "result": "Chớp thời cơ Nhật đầu hàng, Indonesia và Việt Nam giành độc lập (8/1945).",
        "concepts_weighted": [("C_GiaiPhongDanToc", 10), ("C_KhuynhHuongVoSan", 8), ("C_KhuynhHuongTuSan", 8)]
    }
]



