function createForm() {
  var form = FormApp.create("Phieu cham do kho cau hoi Lich su 9");

  form.setTitle("Phieu cham do kho cau hoi Lich su 9");
  form.setDescription(
    "Cam on thay/co tham gia cham do kho!\n\n" +
    "Voi MOI cau hoi, doc de + 4 phuong an (dap an dung duoc ghi trong ngoac), " +
    "roi danh gia DO KHO doi voi hoc sinh lop 9 trung binh: De / Trung binh / Kho.\n\n" +
    "Tong cong co khoang 120 cau."
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(true);
  form.setShowLinkToRespondAgain(false);

  form.addTextItem()
    .setTitle("Ho ten giao vien")
    .setRequired(true);

  form.addTextItem()
    .setTitle("Truong / don vi cong tac")
    .setRequired(false);


  // --- SECTION: Nhóm 1 (câu 1–30) ---
  form.addPageBreakItem()
    .setTitle("Nhóm 1 (câu 1–30)");
  form.addMultipleChoiceItem()
    .setTitle("Trong những năm 5060 của thế kỉ XX nền kinh tế Kiên Xô phát triển mạnh\nA. chiếm 20 sản lượng nông nghiệp toàn thế giới | B. chiếm 25 sản lượng điện toàn thế giới | C. chiếm 20 sản lượng công nghiệp toàn thế giới (DAP AN DUNG) | D. chiếm 30 sản lượng than toàn thế giới")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Đâu không phải là kết quả của công cuộc xây dựng cơ sở vật chất kĩ thuật của CNXH ở Liên Xô giai đoạn 1950  1973\nA. Trở thành cường quốc công nghiệp đứng thứ hai thế giới | B. Sản xuất công nghiệp tăng bình quân 96 hàng năm | C. Sản lượng công nghiệp chiếm 20 toàn thế giới | D. Trở thành cường quốc công nghiệp đứng đầu thế giới (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Công cuộc xây dựng chủ nghĩa xã hội của các nước Đông Âu đã mắc phải sai lầm nghiêm trọng nào\nA. Rập khuôn theo mô hình CNXH ở Liên Xô (DAP AN DUNG) | B. Thực hiện chế độ bao cấp về kinh tế | C. Tập thể hóa nông nghiệp | D. Ưu tiên phát triển công nghiệp nặng")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Ngay sau khi Chiến tranh thế giới thứ hai kết thúc những nước nào ở khu vực Đông Nam Á giành được độc lập sớm nhất\nA. Inđônêxia Lào Thái La | B. Việt Nam Myanma Lào | C. Philippin Thái Lan Singapo | D. Inđônêxia Việt Nam Lào (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Từ cuối những năm 70 của thế kỉ XX ở châu Phi chế độ phân biệt chủng tộc tập trung ở các quốc gia nào\nA. Rôđêdia Tây Nam Phi Cộng hòa Nam Phi (DAP AN DUNG) | B. Ăng gô la Rôđêdia Cộng hòa Nam Phi | C. Tây Nam Phi Rôđêdia Mô dăm bích | D. Tây Nam Phi Cộng hòa Nam Phi Mô dăm bích")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Điểm khác biệt lớn nhất của phong trào giải phóng dân tộc sau chiến tranh thế giới thứ hai so với giai đoạn trước là\nA. lực lượng tham gia | B. lãnh đạo | C. kẻ thù | D. kết quả (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Điểm nổi bật của tình hình kinh tế Trung Quốc trong những năm 1978 đến năm 1998 là gì\nA. Phát triển nhanh chóng tốc độ tăng trưởng cao nhất thế giới (DAP AN DUNG) | B. Kinh tế đã phục hồi ngang bằng so với thời kì trước Cách mạng văn hóa | C. Phát triển thần kì trở thành trung tâm kinh tế lớn thứ 2 thế giớ | D. Tăng trưởng chậm do không đổi mới khoa học công nghệ")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Từ những năm 90 của thế kỳ XX đến nay ASEAN đã chuyển trọng tâm hoạt động sang hợp tác trên lĩnh vực\nA. giáo dục | B. kinh tế (DAP AN DUNG) | C. quân sự | D. du lịch")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Ý nào sau đây không chứng minh cho nhận định Từ đầu những năm 90 của thế kỉ XX một chương mới đã mở ra trong lịch sử khu vực Đông Nam Á\nA. ASEAN vươn lên trở thành tổ chức liên kết khu vực lớn nhất hành tinh (DAP AN DUNG) | B. Nền hòa bình đã được xác lập ở khu vực | C. Các nước trong khu vực đều tham gia vào tổ chức ASEAN | D. ASEAN chuyển trọng tâm hoạt động sang hợp tác kinh tế")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Sự kiện nào được xem là mốc mở đầu cho phong trào giải phóng dân tộc ở châu Phi\nA. Năm châu Phi | B. Cuộc đấu tranh của Angiêri | C. Cuộc nổi dậy của nhân dân Libi | D. Cuộc binh biến của sĩ quan Ai Cập (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Chế độ Apácthai Là sự phân biệt con người dựa trên\nA. tôn giáo | B. chủng tộc màu da (DAP AN DUNG) | C. tài sản | D. vùng miền")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào dưới đây không phải là những thách thức mà nhân dân châu Phi phải đối mặt trong công cuộc xây dựng và phát triển đất nước hiện nay\nA. Bùng nổ dân số dân trí thấp | B. Tình trạng đói nghèo nợ nần và phụ thuộc nước ngoài | C. Ách thống trị hà khắc phản động của thực dân phương Tây (DAP AN DUNG) | D. Các cuộc nội chiến do xung đột sắc tộc")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nguyên nhân nào không tạo điều kiện cho nền kinh tế Mỹ phát triển mạnh sau chiến tranh thế giới thứ hai\nA. Tiến hành chiến tranh xâm lược và nô dịch các nước (DAP AN DUNG) | B. Bán vũ khí cho các nước tham chiế | C. Tập trung sản xuất và tập trung tư bản cao | D. Không bị chiến tranh tàn phá")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nguyên nhân cơ bản nhất thúc đẩy nền kinh tế Mỹ phát triển nhanh chóng sau chiến tranh thế giới thứ hai là\nA. Áp dụng thành tựu khoa học kĩ thuật vào sản xuất (DAP AN DUNG) | B. Bán vũ khí cho các bên tham chiến | C. Tập trung sản xuất và tập trung tư bản cao | D. Tài nguyên thiên nhiên phong phú")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Điểm giống nhau trong chính sách đối ngoại của các đời tổng thống Mỹ trong những năm 1945  1991 là gì\nA. Muốn xác lập một trật tự thế giới mới có lợi cho Mỹ (DAP AN DUNG) | B. Thiết lập chủ nghĩa thực dân cũ ở Mĩ Latinh | C. Viện trợ giúp đỡ các nước xã hội chủ nghĩa | D. Ủng hộ phong trào cách mạng thế giới")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Năm 2013 Chủ tịch nước Trương Tấn Sang và Tổng thống Hoa Kỳ B Obama đã đưa mối quan hệ hợp tác Việt  Mĩ lên tầm cao mới đó là quan hệ\nA. hợp tác chiến lược | B. đối tác toàn diện (DAP AN DUNG) | C. chiến lược toàn cầu | D. đối tác chiến lược")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Vai trò quan trọng nhất của tổ chức Liên hợp quốc là gì\nA. Giải quyết các tranh chấp bằng hòa bình | B. Giúp đỡ các quốc gia phát triển kinh tế xã hội | C. Duy trì hòa bình an ninh thế giới (DAP AN DUNG) | D. Phát triển quan hệ hữu nghị giữa các quốc gia")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Đâu là nhân tố quyết định đến sự phát triển của một quốc gia nửa sau thế kỉ XX\nA. Sức mạnh chính trị quân sự | B. Sức mạnh quân sự | C. Sức mạnh kĩ thuật | D. Sức mạnh khoa học kĩ thuật (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Đâu không phải là mục đích của thực dân Pháp khi thực hiện các chính sách văn hóa  giáo dục nô dịch ở Việt Nam\nA. Xây dựng nền văn hóa tiến bộ ở Việt Nam (DAP AN DUNG) | B. Gây ra tâm lý tự ti cho nhân dân Việt Nam | C. Reo rắc ảo tưởng hòa bình hợp tác | D. Đề cao công lao khai hóa của thực dân Pháp")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào dưới đây không phản ánh đúng những tác động tích cực trong cuộc khai thác thuộc địa lần thứ 2 của Pháp ở Việt Nam\nA. Góp phần làm thay đổi bộ mặt kinh tế ở một số địa phương Hà Nội | B. Bổ sung thêm các lực lượng yêu nước mới công nhân tiểu tư sản | C. Quan hệ sản xuất phong kiến bị thay thể bởi quan hệ sản xuất tư bản (DAP AN DUNG) | D. Tạo điều kiện dẫn đến sự ra đời của con đường cứu nước khuynh hướng vô sản")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Một trong những nguyên nhân thất bại của phong trào yêu nước theo khuynh hướng dân chủ tư sản ở Việt Nam từ sau Chiến tranh thế giới thứ nhất đến đầu năm 1930 là do giai cấp tư sản\nA. chỉ sử dụng phương pháp đấu tranh ôn hòa | B. nhỏ yếu về kinh tế và non kém về chính trị (DAP AN DUNG) | C. chưa được giác ngộ về chính trị | D. chỉ đấu tranh đòi quyền lợi giai cấp")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Con đường cứu nước của Nguyễn Ái Quốc có điểm gì mới so với Phan Bội Châu là đi sang\nA. châu Mĩ tìm đường cứu nước | B. phương Đông tìm đường cứu nước | C. châu Phi tìm đường cứu nước | D. phương Tây tìm đường cứu nước (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nguyên nhân khách quan dẫn đến sự thất bại của khởi nghĩa Yên Bái 1930\nA. Pháp nhận viện trợ từ Mỹ đủ sức đàn áp cuộc đấu tranh đơn độc | B. Pháp suy yếu không đủ sức đàn áp cuộc đấu tranh đơn độc | C. Pháp còn mạnh đủ sức đàn áp cuộc đấu tranh đơn độc (DAP AN DUNG) | D. Pháp cũng Mỹ và 1 số quốc gia khác đàn áp cuộc đấu tranh đơn độc")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Cương lĩnh chính trị đầu tiên của Đảng Cộng sản Việt Nam bao gồm nhiều văn kiện ngoại trừ\nA. Chính cương vắn tắt | B. Điều lệ tóm tắt | C. Bản án chế độ thực dân Pháp (DAP AN DUNG) | D. Sách lược vắn tắt")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nhận xét nào sau đây không đúng khi đánh giá về nhiệm vụ cách mạng được xác định trong Cương lĩnh chính trị năm 1930\nA. Phù hợp với tình hình xã hội Việt Nam | B. Bao gồm nhiệm vụ dân tộc dân chủ | C. Nhiệm vụ dân tộc dân chủ đặt ngang nhau (DAP AN DUNG) | D. Nhiệm vụ dân tộc được nhấn mạnh hơn")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Để giải quyết hậu quả của cuộc khủng hoảng kinh tế 19291933 thực dân Pháp đã thực hiện biện pháp gì\nA. Trút gánh nặng sang các nước thuộc địa | B. Tăng cường bóc lột nhân dân lao động ở Pháp và các nước thuộc địa (DAP AN DUNG) | C. Tăng cường bóc lột nhân dân Đông Dương | D. Tăng cường bóc lột nhân dân lao động Pháp")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Phong trào cách mạng 19301931 phát triển lên đến đỉnh cao ở địa phương nào\nA. Nam Định | B. Hà Nội | C. Nghệ An Hà Tĩnh (DAP AN DUNG) | D. Sài Gòn")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Mục tiêu đấu tranh của phong trào 1930 1931 là gì\nA. đòi tự do dân chủ cơm áo và hòa bình (DAP AN DUNG) | B. chống chế độ phản động thuộc địa chống phát xít chống chiến tranh | C. chống phong kiến giành ruộng đất cho dân cày | D. chống đế quốc chống phong kiến giành độc lập dân tộc và ruộng đất cho dân cày")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Căn cứ vào đâu để khẳng định Xô Viết Nghệ  Tĩnh thật sự là chính quyền cách mạng của quần chúng dưới sự lãnh đạo của Đảng\nA. Thời gian tồn tại của chính quyền Xô Việt Nghệ Tĩnh | B. Quy mô của chính quyền Xô Viết | C. Tổ chức bộ máy chính quyền | D. Các chính sách của chính quyền Xô Viết (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nhiệm vụ hàng đầu của cách mạng Việt Nam thời kì 1939  1945 là gì\nA. Đánh đổ đế quốc phát xít xâm lược giành độc lập dân tộc (DAP AN DUNG) | B. Lật đổ chế độ phong kiến giành ruộng đất cho dân cày | C. Lật đổ chế độ phản động thuộc địa cải thiện dân sinh | D. Đánh đổ các giai cấp bóc lột giành quyền tự do dân chủ")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);

  // --- SECTION: Nhóm 2 (câu 31–60) ---
  form.addPageBreakItem()
    .setTitle("Nhóm 2 (câu 31–60)");
  form.addMultipleChoiceItem()
    .setTitle("Nhiệm vụ hàng đầu của cách mạng Việt Nam được xác định tại Hội nghị lần thứ 8 Ban chấp hành Trung ương Đảng Cộng sản Đông Dương 51941 là gì\nA. Chống Pháp để giành độc lập dân tộc | B. Độc lập dân tộc và ruộng đất dân cày | C. Giải phóng cho được các dân tộc Đông Dương ra khỏi ách Pháp Nhật (DAP AN DUNG) | D. Tiến hành thổ địa cách mạng")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây không phải là ý nghĩa của cao trào kháng Nhật cứu nước\nA. Tập dượt quần chúng đấu tranh | B. Thúc đẩy thời cơ cách mạng chín muồi | C. Lực lượng cách mạng được củng cố phát triển vượt bậc | D. Báo hiệu thời cơ để Tổng khởi nghĩa giành chính quyền đã đến (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Tên gọi Đội Việt Nam tuyên truyền giải phóng quân có ý nghĩa như thế nào\nA. Quân sự quan trọng hơn chính trị | B. Chỉ chú trọng hoạt động quân sự | C. Chỉ coi trọng hoạt động chính trị | D. Chính trị quan trọng hơn quân sự (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây không thể hiện đúng vai trò của Hồ Chí Minh trong cách mạng tháng Tám 1945\nA. Hoàn thiện quá trình chuyển hướng chỉ đạo chiến lược cách mạng | B. Đưa ra chủ trương hòa để tiến kí Hiệp định Sơ bộ với Pháp (DAP AN DUNG) | C. Trực tiếp lãnh đạo nhân dân Việt Nam giành chính quyền | D. Xây dựng phát triển lực lượng chuẩn bị cho cách mạng tháng Tám")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Thời cơ ngàn năm có một để nhân dân Việt Nam tổng khởi nghĩa giành chính quyền năm 1945 kết thúc khi\nA. thực dân Pháp bắt đầu nổ súng xâm lược trở lại Việt Nam | B. Nhật cùng thực dân Anh chống phá chính quyền cách mạng | C. quân Đồng minh vào Đông Dương giải giáp quân đội Nhật (DAP AN DUNG) | D. Nhật giao Đông Dương cho quân Trung Hoa Dân quốc")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào không phản ánh đúng về vai trò của Mặt trận Việt Minh từ khi thành lập đến Cách mạng tháng Tám năm 1945\nA. Phối kết hợp với lực lượng Đồng minh tham gia giành chính quyền (DAP AN DUNG) | B. Tham gia xây dựng lực lượng vũ trang và tập dượt quần chúng đấu tranh | C. Cùng với Đảng lãnh đạo nhân dân cả nước khởi nghĩa giành chính quyền | D. Góp phần xây dựng lực lượng chính trị hùng hậu cho việc giành chính quyền")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Khó khăn lớn nhất của nước Việt Nam Dân chủ Cộng hòa sau cách mạng tháng Tám năm 1945 là gì\nA. Ngoại xâm và nội phản (DAP AN DUNG) | B. Kinh tế tài chính kiệt quệ | C. Chính quyền cách mạng non trẻ | D. Văn hóa lạc hậu")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung đường lối kháng chiến chống thực dân Pháp 19461954 của Đảng và Chính phủ nước Việt Nam Dân chủ Cộng hòa là gì\nA. Toàn dân toàn diện trường kì tự lực cánh sinh và tranh thủ sự ủng hộ quốc tế (DAP AN DUNG) | B. Tự lực cánh sinh và tranh thủ sự ủng hộ quốc tế | C. Trường kìtự lực cánh sinh và tranh thủ sự ủng hộ quốc tế | D. Toàn diện tự lực cánh sinh và tranh thủ sự ủng hộ quốc tế")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Chiến thắng Việt Bắc năm 1947 của quân dân Việt Nam đã buộc thực dân Pháp phải chuyển từ chiến lược đánh nhanh thắng nhanh sang\nA. phòng ngự | B. đánh phân tán | C. đánh lâu dài (DAP AN DUNG) | D. đánh tiêu hao")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Đâu không phải là những biện pháp được Pháp thực hiện trước khi kế hoạch Nava bị đảo lộn\nA. Mở các cuộc tiến công vào Ninh Bình Thanh Hóa để phá kế hoạch tiến công của ta | B. Tập trung 44 tiểu đoàn quân cơ động ở đồng bằng Bắc Bộ | C. Tập trung lực lượng xây dựng tập đoàn cứ điểm Điện Biên Phủ (DAP AN DUNG) | D. Tăng cường viện binh cho Đông Đương")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Cuộc tiến công chiến lược Đông Xuân 19531954 đã khoét sâu vào điểm yếu nào của kế hoạch Nava\nA. tính phi nghĩa của cuộc chiến tranh Đông Dương của thực dân Pháp | B. không thể tăng thêm quân số để xây dựng lực lượng mạnh | C. thời gian để xây dựng lực lượng chuyển bại thành thắng quá ngắn 18 tháng | D. mâu thuẫn giữa tập trung và phân tán lực lượng (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Mĩ chính thức tiến hành cuộc chiến tranh phá hoại miền Bắc lần thứ nhất trong khi đang thực hiện chiến lược chiến tranh nào ở miền Nam Việt Nam\nA. Chiến tranh cục bộ | B. Đông Dương hóa chiến tranh | C. Chiến tranh đặc biệt (DAP AN DUNG) | D. Việt Nam hóa chiến tranh")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào trong Hiệp định Pari 1973 có tác động tích cực đến sự thay đổi so sánh lực lượng giữa cách mạng Việt Nam và Mĩ ở mn Việt Nam\nA. Hoa Kì cam kết góp phần vào hàn gắn vết thương chiến tranh ở Việt Nam | B. Hoa Kì công nhận các quyền dân tộc cơ bản của Việt Nam và rút quân về nước (DAP AN DUNG) | C. Các bên tham chiến thực hiện chuyển quân chuyển giao khu vực chiếm đóng | D. Để cho nhân dân miền Nam tự quyết định tương lai chính trị của mình")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Chiến dịch Điện Biên Phủ năm 1954 và trận Điện Biên Phủ trên không năm 1972 của quân dân Việt Nam đều\nA. là những thắng lợi quân sự quyết định dẫn tới kí kết một hiệp định hòa bình (DAP AN DUNG) | B. đánh dấu cuộc chiến đấu chống ngoại xâm của nhân dân Việt Nam đã kết thúc | C. có chung địa bàn mở chiến dịch là ở các đô thị phía Bắc vĩ tuyến 17 | D. có chung đối tượng cách mạng là thực dân Pháp xâm lược")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Chiến dịch Điện Biên Phủ 1954 và chiến dịch Hồ Chí Minh 1975 đều\nA. là cơ sở để đi đến kí kết các hiệp định hòa bình | B. là những trận quyết chiến chiến lược (DAP AN DUNG) | C. có sự điều chỉnh phương châm tác chiến | D. có địa bàn tác chiến là khu vực đô thị")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Điểm khác nhau trong hành động khiêu khích của tập đoàn Pônpốt và Trung Quốc trong cuộc đấu tranh bảo vệ biên giới phía Bắc và phía Tây Nam là gì\nA. Huy động quân đội mở cuộc chiến tranh | B. Lấn chiếm lãnh thổ Việt Nam | C. Cắt viện trợ rút chuyên gia (DAP AN DUNG) | D. Khiêu khích quân sự dọc biên giới")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào dưới đây không phản ánh đúng mục tiêu của Đảng cộng Sản Việt Nam đề ra trong kế hoạch 5 năm 1996  2000\nA. Tăng trưởng kinh tế chậm nhưng chắc (DAP AN DUNG) | B. Tăng trưởng kinh tế nhanh | C. Bảo đảm an ninh quốc phòng | D. Cải thiện đời sống nhân dân")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Đâu không phải là nội dung của Ba chương trình kinh tế được thực hiện trong kế hoạch 5 năm 19861990\nA. Hàng xuất khẩu | B. Hàng tiêu dùng | C. Lương thực thực phẩm | D. Hàng nhập khẩu (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nhân tố hàng đầu quyết định mọi thắng lợi của cách mạng Việt Nam từ năm 1930 đến năm 2000 là gì\nA. Sự đoàn kết đồng lòng giữa Đảng và nhân dân | B. Tinh thần yêu nước của nhân dân Việt Nam | C. Sự ủng hộ của quốc tế | D. Sự lãnh đạo của Đảng với đường lối đúng đắn (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Một trong những mục tiêu của hội đồng tương trợ kinh tế (SEV) khi thành lập là:\nA. chống lại sự bao vây cấm vận về kinh tế của Mỹ và các nước Tây Âu. | B. tăng cường hợp tác giúp đỡ lẫn nhau giữa các nước xã hội chủ nghĩa. (DAP AN DUNG) | C. viện trợ, giúp đỡ Liên Xô khôi phục kinh tế sau chiến tranh. | D. viện trợ kinh tế cho các nước Đông Âu khôi phục kinh tế sau chiến tranh.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Sự ra đời của nước Cộng hòa Nhân dân Trung Hoa (1949) có ý nghĩa như thế nào đối với Trung Quốc?\nA. Hoàn thành cuộc cách mạng dân chủ ở Trung Quốc | B. Chấm dứt sự nô dịch và thống trị của chủ nghĩa thực dân cũ ở Trung Quốc | C. Lật đổ chế độ quân chủ chuyên chế tồn tại hàng ngàn năm ở Trung Quốc. | D. Chấm dứt hơn 100 năm nô dịch và thống trị của đế quốc, xóa bỏ tàn dư phong kiến, mở ra kỉ nguyên độc lập, tự do, đi lên xã hội chủ nghĩa (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Từ việc bản “Yêu sách của nhân dân An Nam” không được Hội nghị Vécxai (1919) chấp nhận, Nguyễn Ái Quốc rút ra kết luận: muốn được giải phóng, các dân tộc (thuộc địa)\nA. chỉ có thể trông cậy vào lực lượng của bản thân mình. (DAP AN DUNG) | B. chỉ có thể đi theo con đường cách mạng vô sản. | C. phải dựa vào sự giúp đỡ của các nước xã hội chủ nghĩa. | D. phải liên hệ mật thiết với phong trào công nhân quốc tế.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Đại thắng mùa xuân 1975 đã đưa Việt Nam bước vào thời kì\nA. độc lập, tự do, cả nước đi lên tư bản chủ nghĩa. | B. Độc lập, thống nhất, cả nước đi lên chủ nghĩa xã hội (DAP AN DUNG) | C. hòa bình và thống nhất. | D. hòa bình, tự do, tiến lên xây dựng chủ nghĩa xã hội.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nhiệm vụ khôi khục kinh tế, xây dựng chủ nghĩa xã hội đặt ra yêu cầu bức thiết gì đối với các nước Cộng hoà Xô viết (1918-1921)?\nA. Thay Chính sách kinh tế mới bằng Chính sách cộng sản thời chiến. | B. Thay đổi thể chế để phát huy hơn nữa sức mạnh tổng hợp. | C. Liên minh chặt chẽ hơn nữa để thành lập nhà nước thống nhất. (DAP AN DUNG) | D. Mở rộng hơn nữa quan hệ đối ngoại để tìm kiếm đồng minh.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Chiến thắng nào sau đây của nhân dân Liên Xô đã làm phá sản chiến lược “Chiến tranh chớp nhoáng” của Hitle?\nA. Chiến thắng ở Noócmăngđi. | B. Chiến thắng Xtalingơrat | C. Chiến thắng Mátxcơva (DAP AN DUNG) | D. Chiến thắng Cuốcxcơ.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Trên đường truy quét phát xít Đức đến sào huyệt cuối cùng (1944), Hồng quân Liên Xô không giúp đỡ quốc gia nào được giải phóng?\nA. Ba Lan. | B. Bungari. | C. Runmani. | D. Pháp. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Sự bùng nổ của cuộc khởi nghĩa Yên Bái (9/2/1930) xuất phát từ nguyên nhân trực tiếp nào sau đây?\nA. Những tác động mạnh mẽ trong sự ra đời của Đảng Cộng sản. | B. Thực dân Pháp khủng bố sau vụ ám sát trùm mộ phu Ba-danh. (DAP AN DUNG) | C. Những thành công của phong trào Xô viết Nghệ - Tĩnh. | D. Những di chứng của cuộc khủng hoảng kinh tế thế giới 1929 - 1933.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây phản ánh điểm khác nhau căn bản trong hoạt động của Hội Việt Nam Cách mạng Thanh niên với Việt Nam Quốc dân Đảng?\nA. Chuẩn bị những tiền đề cho sự ra đời của Đảng vô sản. (DAP AN DUNG) | B. Tăng cường tổ chức quần chúng đấu tranh vũ trang. | C. Tập trung phát triển lực lượng cách mạng ở Bắc Kì. | D. Thường xuyên tiến hành những vụ ám sát cá nhân.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nguyên nhân chủ yếu nào thúc đẩy Nguyễn Tất Thành ra đi tìm đường cứu nước, giải phóng dân tộc năm 1911?\nA. Yêu cầu khách quan của cách mạng Việt Nam. (DAP AN DUNG) | B. Đã nhận thức được về “bạn và thù” của cách mạng. | C. Hạn chế của các con đường cứu nước trước đó. | D. Sự thất bại của khuynh hướng cứu nước phong kiến.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Đại hội Quốc dân họp ở Tân Trào (16/8/1945) đã quyết định thành lập\nA. Uỷ ban Lâm thời Khu giải phóng. | B. Uỷ ban Khởi nghĩa toàn quốc. | C. Uỷ ban Dân tộc giải phóng Việt Nam. (DAP AN DUNG) | D. Chính phủ Liên hiệp quốc dân.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);

  // --- SECTION: Nhóm 3 (câu 61–90) ---
  form.addPageBreakItem()
    .setTitle("Nhóm 3 (câu 61–90)");
  form.addMultipleChoiceItem()
    .setTitle("Trong thời kì Chiến tranh lạnh, Mỹ ủng hộ quốc gia nào sau đây?\nA. Cộng hòa Dân chủ Đức. | B. Cộng hòa Nhân dân Trung Hoa. | C. Cộng hòa Liên bang Đức. (DAP AN DUNG) | D. Cộng hòa Cuba.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Trong thời kỳ Chiến tranh lạnh, Liên Xô đã\nA. đưa quân đội sang giúp Việt Nam đánh thắng quân Pháp. | B. giúp Việt Nam thoát khỏi thế bao vây, cấm vận của Mỹ. | C. ủng hộ công cuộc xây dựng chủ nghĩa xã hội ở Việt Nam. (DAP AN DUNG) | D. giúp đỡ Việt Nam phát triển các loại vũ khí hạt nhân.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Hệ quả công cuộc cải cách về kinh tế của Liên Xô trong những năm 80 của thế kỉ XX là gì?\nA. Nền kinh tế vẫn trượt dài trên khủng hoảng. (DAP AN DUNG) | B. Nhà nước nắm độc quyền về kinh tế. | C. Đưa nền kinh tế thoái khỏi khủng hoảng. | D. Khôi phục và phát triển mạnh mẽ nền kinh tế.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Sau Chiến tranh thế giới thứ hai, về mặt quân, Mỹ đạt được ưu thế vượt trội nào sau đây so với các nước tư bản khác?\nA. Giành thắng lợi trong xung đột với Liên Xô. | B. Đặt được các căn cứ quân sự trên toàn thế giới. | C. Chế tạo thành công hệ thống phòng chống tên lửa. | D. Quân đội mạnh và độc quyền về vũ khí nguyên tử. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Đến những năm 90 của thế kỉ XX, tình hình chính trị khu vực Đông Nam Á cải thiện rõ rệt sau sự kiện nào?\nA. Việt Nam, Lào, Cam-pu-chia thoát khỏi ách thống trị của Mỹ. | B. Hiệp định hòa bình về Cam-pu-chia được kí kết tại Pa-ri. (DAP AN DUNG) | C. Chủ nghĩa xã hội ở Liên Xô và Đông Âu sụp đổ. | D. Xu thế toàn cầu hóa diễn ra ngày càng mạnh mẽ.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Trong những năm 1954 - 1956, Mĩ dựng lên chính quyền tay sai đứng đầu là Ngô Đình Diệm ở miền Nam Việt Nam nhằm mục đích nào sau đây?\nA. Biến miền Nam Việt Nam thành thuộc địa kiểu cũ. | B. Ngăn chặn sự chi viện từ miền Bắc vào miền Nam. | C. Chống lại cách mạng và nhân dân Việt Nam. (DAP AN DUNG) | D. Phá hoại chủ nghĩa xã hội của Việt Nam.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Cuộc hành quân lớn nhất của Mĩ trong cuộc phản công chiến lược mùa khô 1966 - 1967 là tấn công vào\nA. Phan Rang. | B. Buôn Ma Thuột. | C. Vạn Tường. | D. Dương Minh Châu. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây không phản ánh đúng kết quả cuộc đấu tranh bảo vệ biên giới Tây Nam của quân dân Việt Nam (1975 - 1978)?\nA. Bảo vệ vững chắc chủ quyền lãnh thổ của quốc gia. | B. Quân Pôn Pốt xâm phạm lãnh thổ Việt Nam. (DAP AN DUNG) | C. Tạo điều kiện cho cách mạng Cam-pu-chia giành thắng lợi. | D. Đập tan hành động xâm lược của quân Pôn Pốt.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Một trong những kết quả tiêu biểu về kinh tế của Việt Nam giai đoạn 1986 - 1991 là\nA. Việt Nam trở thành nước xuất khẩu gạo lớn nhất thế giới. | B. chỉ tập trung phát triển thành phần kinh tế quốc doanh. | C. lương thực, thực phẩm từng bước đáp ứng nhu cầu của nhân dân. (DAP AN DUNG) | D. tốc độ tăng trưởng kinh tế của Việt Nam cao nhất khu vực Đông Nam Á.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Ý nào sau đây không mô tả đúng tình hình xã hội của Trung Quốc?\nA. Thu nhập bình quân đầu người được cải thiện. | B. Công cuộc xóá đói giảm nghèo được đẩy mạnh. | C. Hệ thống y tế được thực hiện đối với đa số người dân. | D. Tinh trạng già hóa dân số, tỉ lệ sinh thấp nhất thế giới. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây phản ánh đúng tình hình kinh tế Hàn Quốc đầu thế kỷ XXI?\nA. Xây dựng nền kinh tế nhiều quy mô dựa trên sở hữu công. | B. Tăng trưởng liên tục, không chịu tác động của khủng hoảng. | C. Nền kinh tế duy trì được mức tăng trưởng ổn định. (DAP AN DUNG) | D. Trở thành cường quốc công - nông nghiệp ở châu Á.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Chiến tranh thế giới thứ hai (1939-1945) đã không có tác động nào đến tình hình thế giới?\nA. Ảnh hưởng tích cực đến phong trào giải phóng dân tộc trên thế giới. | B. Dẫn tới những mâu thuẫn của các nước thắng trận về vấn đề thuộc địa. (DAP AN DUNG) | C. D ẫn tới sự ra đời của các nước xã hội chủ nghĩa trên thế giới. | D. Làm thay đổi tương quan lực lượng giữa các nước tư bản chủ nghĩa .")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Việt Nam Quốc dân đảng xác định lực lượng chủ chốt tiến hành bạo lực cách mạng là\nA. lực lượng du kích trong cứu quốc quân. | B. binh lính người Việt trong quân đội Pháp. (DAP AN DUNG) | C. giai cấp công nhân và giai cấp nông dân. | D. những thân hào, thân sĩ ở nông thôn.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Đảng Cộng sản Việt Nam ra đời năm 1930 có tác động nào đối với phong trào đấu tranh của giai cấp công nhân Việt Nam?\nA. Phong trào công nhân hoàn toàn chuyển sang đấu tranh tự giác. (DAP AN DUNG) | B. Phong trào công nhân bước đầu chuyển sang đấu tranh tự giác. | C. Làm cho phong trào công nhân bước đầu thắng thế ở Việt Nam. | D. Dẫn tới sự ra đời và phát triển mạnh mẽ của phong trào công nhân.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nguyễn Ái Quốc đã bước đầu đặt cơ sở cho mối quan hệ giữa cách mạng Việt Nam với phong trào giải phóng dân tộc trên thế giới trong sự kiện nào?\nA. Tham gia sáng lập Đảng Cộng sản Pháp. | B. Tham gia thành lập Hội Liên hiệp thuộc địa. (DAP AN DUNG) | C. Bỏ phiếu tán thành gia nhập Quốc tế Cộng sản. | D. Dự Đại hội lần thứ V của Quốc tế Cộng sản.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nhiệm vụ hàng đầu của cách mạng Việt Nam được Nguyễn Ái Quốc nêu trong Cương lĩnh chính trị đầu tiên của Đảng là\nA. chia ruộng đất cho người nông dân. | B. lập chính chủ dân chủ cộng hòa. | C. đánh đổ đế quốc và phong kiến. (DAP AN DUNG) | D. thành lập chính phủ của toàn thể nhân dân.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Cao trào dân chủ 1936 - 1939 và phong trào cách mạng 1930 - 1931 ở Việt Nam không có điểm khác biệt về\nA. nhiệm vụ chiến lược. (DAP AN DUNG) | B. nhiệm vụ trước mắt. | C. hình thức mặt trận. | D. khẩu hiệu đấu tranh.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây phản ánh bài học kinh nghiệm của phong trào 1930 - 1931 được Đảng Cộng sản Đông Dương vận dụng trong giai đoạn 1939 - 1945?\nA. Giành chính quyền bằng bạo lực cách mạng. (DAP AN DUNG) | B. Phải xây dựng mặt trận dân tộc thống nhất. | C. Xây dựng khối liên minh công - nông vững chắc. | D. Kết hợp nhiệm vụ kháng chiến và kiến quốc.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Trong quá trình lãnh đạo cách mạng của Đảng, sự kiện nào là mốc đánh dấu sự phát triển hơn nữa tư tưởng cách mạng của Nguyễn Ái Quốc - Hồ Chí Minh thể hiện trong Cương lĩnh chính trị đầu tiên?\nA. Hội nghị lần thứ 7 Ban Chấp hành Trung ương Đảng (11/1940). | B. Đại hội đại biểu lần thứ II của Đảng Cộng sản Đông Dương (2/1951). | C. Hội nghị lần thứ 8 Ban Chấp hành Trung ương Đảng (5/1941). (DAP AN DUNG) | D. Hội nghị lần thứ 6 Ban Chấp hành Trung ương Đảng (11/1939).")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Đội Việt Nam Tuyên truyền Giải phóng quân được thành lập năm 1944 với nhiệm vụ trọng tâm nào sau đây?\nA. Xây dựng lực lượng chính trị đông đảo ở Việt Bắc. | B. Khởi nghĩa vũ trang giành chính quyền trong cả nước. | C. Tuyên truyền, chính trị kết hợp với đấu tranh quân sự. (DAP AN DUNG) | D. Tiến hành khởi nghĩa từng phần ở các căn cứ địa.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Để tiến hành Chiến tranh lạnh với Liên Xô, M ỹ và các cường quốc đã không thực hiện biện pháp nào sau đây ?\nA. Tăng cường đầu tư phát triển quân sự. | B. Thành lập các khối quân sự trên thế giới . | C. Đàn áp phong trào giải phóng dân tộc thế giới . | D. Tiến hành chiến tranh thương mại Mỹ - Trung . (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Sự kiện nào là “sản phẩm” của Chiến tranh lạnh và là cuộc đụng đầu trực tiếp đầu tiên giữa hai phe?\nA. Cuộc chiến tranh xâm lược Đông Dương của Pháp (1945 - 1954). | B. Cuộc chiến tranh Triều Tiên (1950 - 1953). (DAP AN DUNG) | C. Cuộc nội chiến ở Campuchia (1979 - 1991). | D. Cuộc chiến tranh xâm lược Việt Nam của Mỹ (1954 - 1975).")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào phản ánh đúng kết quả sự đối đầu căng thẳng giữa M ỹ và Liên Xô sau Chiến tranh thế giới thứ hai?\nA. Chuyển dần sang hòa bình, đối thoại, cùng phát triển. (DAP AN DUNG) | B. Trở thành Đồng minh thân cận với nhau. | C. Dẫn đến những cuộc xung đột quân sự trực tiếp. | D. Dẫn đến cuộc chiến tranh thế giới mới.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào là kết quả của kế hoạch 5 năm lần thứ tư (1946 - 1950) nhằm khôi phục kinh tế và phát triển đất nước ở Liên Xô?\nA. Hoàn thành một phần kế hoạch đề ra. | B. Hoàn thành thắng lợi vượt mức trước thời hạn. (DAP AN DUNG) | C. Không thực hiện thành công kế hoạch. | D. Phải tạm dừng do tác động chiến tranh.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Ngày 8/9/1951, nhằm tận dụng nguồn viện trợ của Mỹ phục vụ cho phát triển kinh tế, Nhật Bản ký kết với Mĩ bản\nA. Hiệp ước phòng thủ chung Đông Nam Á. | B. Hiệp ước an ninh Mĩ - Nhật. (DAP AN DUNG) | C. Hiệp ước liên minh Mĩ - Nhật. | D. Hiệp ước hợp tác kinh tế Mỹ - Nhật.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Sau Chiến tranh thế giới thứ hai, giai đoạn nào nhân dân Campuchia rơi vào thảm họa diệt chủng?\nA. Thời kỳ nội chiến kéo dài (1979 - 1991). | B. Thời kỳ đế quốc Mỹ xâm lược (1970 - 1975). | C. Thực dân Pháp xâm lược (1945 - 1954). | D. Tập đoàn Khơ-me đỏ cầm quyền (1975 - 1979). (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Sau khi Cách mạng tháng Tám thành công, các thế lực ngoại xâm và nội phản ở Việt Nam đều có chung âm mưu nào sau đây?\nA. Chống phá và tiêu diệt nước Việt Nam non trẻ. (DAP AN DUNG) | B. Ngăn cản quá trình hội nhập quốc tế của Việt Nam. | C. Duy trì chính quyền tay sai Trần Trọng Kim. | D. Biến Việt Nam là tâm điểm của cuộc đối đầu Đông - Tây")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Trận đánh nào có tính chất ác liệt và ý nghĩa quyết định nhất trong chiến dịch Biên giới thu - đông 1950?\nA. Cao Bằng. | B. Đông Khê. (DAP AN DUNG) | C. Thất Khê. | D. Bông Lau.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Cuối tháng 12 năm 1946, ở các đô thị phía Bắc vĩ tuyến 16, quân dân Việt Nam đã\nA. bị động phân tán lực lượng. | B. thực hiện “vườn không nhà trống”. | C. chủ động tấn công quân Pháp. (DAP AN DUNG) | D. chủ động rút lui ra khỏi các đô thị.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Trong kế hoạch Bô-la-e, để bao vây Việt Bắc từ phía Tây, Pháp đã sử dụng thủ đoạn nào sau đây?\nA. Cho quân bộ hành quân theo đường số 4 từ Lạng Sơn lên Cao Bằng. | B. Cho quân nhảy dù xuống Bắc Kạn, Chợ Đồn, Chợ Mới, Chợ Giã. | C. Cho binh đoàn hỗn hợp theo sông Hồng lên sông Lô, sông Gâm. (DAP AN DUNG) | D. Cho binh đoàn hỗn hợp hợp quân tại Đài Thị, Chiêm Hóa, Tuyên Quang.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);

  // --- SECTION: Nhóm 4 (câu 91–120) ---
  form.addPageBreakItem()
    .setTitle("Nhóm 4 (câu 91–120)");
  form.addMultipleChoiceItem()
    .setTitle("Với Hiệp định Giơ-ne-vơ 1954 về chấm dứt chiến tranh, lập lại hòa bình ở Đông Dương, Mỹ đã\nA. thất bại trong việc chuyển trọng tâm chiến lược toàn cầu sang Việt Nam. | B. thất bại âm mưu kéo dài, mở rộng, quốc tế hóa chiến tranh xâm lược Đông Dương. (DAP AN DUNG) | C. thành công trong kế hoạch từng bước thay chân Pháp xâm lược Đông Dương. | D. thắng lợi trong kế hoạch khống chế và nô dịch các nước đồng minh.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Mĩ chính thức gây ra cuộc chiến tranh bằng không quân và hải quân đối với miền Bắc Việt Nam khi nào?\nA. Mĩ dựng lên “sự kiện Vịnh Bắc Bộ”, xâm phạm chủ quyền Việt Nam (1964). | B. Mĩ cho máy bay ném bom bắn phá thị xã Đồng Hới, đảo Cồn Cỏ... (7/2/1965). (DAP AN DUNG) | C. Mĩ cho máy bay ném bom ở cửa sông Gianh, Vinh - Bến Thủy... (5/8/1964). | D. Mĩ cho hải quân phong tỏa vùng biển ở Bắc Bộ, ngăn chặn bờ biển (1964).")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây phản ánh điểm khác biệt về âm mưu của Mĩ khi tiến hành chiến tranh phá hoại miền Bắc lần thứ hai (1972) so với lần thứ nhất (1965 - 1968)?\nA. Phá tiềm lực kinh tế, quốc phòng, công cuộc xây dựng CNXH ở miền Bắc. | B. Ngăn chặn sự chi viện từ bên ngoài vào miền Bắc, từ miền Bắc vào miền Nam. | C. Giành một thắng lợi quân sự quyết định, buộc ta kí hiệp định có lợi cho Mĩ. (DAP AN DUNG) | D. Đánh bại hoàn toàn ý chí chiến đấu của quân và dân hai miền Nam - Bắc.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("So với Chiến dịch Điện Biên Phủ năm 1954, chiến dịch Hồ Chí Minh năm 1975 của quân dân Việt Nam diễn ra ở địa bàn nào?\nA. Rừng núi. | B. Đô thị lớn. (DAP AN DUNG) | C. Trung du. | D. Nông thôn.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Hiệp định Pa-ri về chấm dứt chiến tranh, lập lại hòa bình ở Việt Nam năm 1973 không có ý nghĩa nào nào sau đây?\nA. Mĩ phải công nhận các quyền dân tộc cơ bản của Việt Nam, rút quân về nước. | B. Tạo thời cơ thuận lợi để nhân dân ta tiến lên đánh bại quân đội Sài Gòn. | C. Thúc đẩy những điều kiện khách quan nhanh chóng được hội tụ đầy đủ. (DAP AN DUNG) | D. Là kết quả cuộc đấu tranh kiên cường, bất khuất của quân dân hai miền đất nước.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Việt Nam trở thành nơi diễn ra “cuộc đụng đầu lịch sử mang tính chất thời đại và có tầm vóc quốc tế thời kì 1954 - 1975” vì\nA. Việt Nam có nhiều tài nguyên thiên nhiên, nguồn lao động rẻ mạt. | B. Việt Nam đánh bại cuộc chiến tranh xâm lược thực dân kiểu mới của Mĩ. (DAP AN DUNG) | C. Việt Nam là quốc gia tập trung tất cả mâu thuẫn gay gắt của thời đại. | D. Việt Nam là một nước có vị trí chiến lược quan trọng ở Đông Nam Á.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Trong trật tự thế giới đa cực, sự gia tăng vai trò của các trung tâm, các tổ chức quốc tế phản ánh nội dung nào sau đây?\nA. Nền kinh tế thế giới đã đạt được công bằng mới. | B. Trình độ phát triển của các nước không còn chênh lệch. | C. So sánh lực lượng mới trong quan hệ quốc tế. (DAP AN DUNG) | D. Quy luật phát triển đồng đều của lịch sử thế giới.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nhận xét nào sau đây đúng về GDP của Việt Nam từ năm 1995 đến năm 2021?\nA. GDP của Việt Nam liên tục tăng. (DAP AN DUNG) | B. GDP có sự tăng trưởng không ổn định. | C. GDP giảm do khủng hoảng kinh tế. | D. Có GDP thuộc nhóm cao nhất thế giới.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Trong quá trình xây dựng chủ nghĩa xã hội (1925-1941), Liên Xô đã đặt trọng tâm phát triển lĩnh vực nào?\nA. Thương nghiệp. | B. Thủ công nghiệp. | C. Công nghiệp nặng. (DAP AN DUNG) | D. Công nghiệp nhẹ.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Sau Chiến tranh thế giới thứ hai , quan hệ giữa Mỹ và Liên Xô là\nA. quan hệ hợp tác hữu nghị. | B. q uan hệ Đồng minh. | C. q uan hệ láng giềng thân thiện . | D. quan hệ đối đầu căng thẳng. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Cương lĩnh chính trị đầu tiên của Đảng Cộng sản Việt Nam là cương lĩnh đúng đắn và sáng tạo vì đã\nA. khẳng định cách mạng Việt Nam là bộ phận của cách mạng thế giới. | B. khẳng định công nhân và nông dân là nòng cốt của cách mạng. | C. kêu gọi các dân tộc trên thế giới đoàn kết chống kẻ thù chung. | D. thể hiện rõ tính độc lập dân tộc và tự do của nhân dân Việt Nam. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Lực lượng vũ trang nào giữ vai trò quan trọng đối với thắng lợi của Tổng khởi nghĩa tháng Tám năm 1945?\nA. Cứu quốc quân. | B. Đội Việt Nam Tuyên truyền Giải phóng quân. | C. Việt Nam Giải phóng quân. (DAP AN DUNG) | D. Lực lượng tự vệ chiến đấu.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Trong Cách mạng tháng Tám năm 1945, khởi nghĩa tại các đô thị thắng lợi có ý nghĩa quyết định nhất vì đây là nơi\nA. có đông đảo quần chúng giác ngộ cách mạng. | B. có nhiều căn cứ địa cách mạng của Việt Nam. | C. tập trung các trung tâm kinh tế, chính trị của kẻ thù. (DAP AN DUNG) | D. đặt cơ quan đầu não chỉ huy của lực lượng cách mạng.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nhiệm vụ chính của nhân dân Trung Quốc từ năm 1953 đến năm 1978 là\nA. tiến hành cách mạng dân tộc dân chủ. | B. hoàn thành công cuộc khôi phục kinh tế. | C. tiến hành cải tạo công thương nghiệp. | D. bước đầu xây dựng chủ nghĩa xã hội. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây phản ánh đặc điểm của ASEAN trong giai đoạn 1967 - 1975?\nA. Liên kết bền chặt, hoàn thiện về cơ cấu tổ chức. | B. Liên minh kinh tế chính trị lớn nhất hành tinh. | C. Trở thành tổ chức khu vực có nhiều thành công. | D. Tổ chức non yếu, chưa có vị thế trên trường quốc tế. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Điểm mới trong nhiệm vụ của cách mạng Việt Nam giai đoạn 1951 - 1953 so với giai đoạn 1946 - 1950 là\nA. chống đế quốc Mỹ xâm lược kiểu mới. | B. chống thực dân Pháp và tay sai. | C. chống thực dân Pháp và can thiệp Mỹ. (DAP AN DUNG) | D. chống sự phục hồi của phong kiến.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Năm 1952, Đảng và Chính phủ Việt Nam đề ra phong trào nào trên mặt trận kinh tế đã lôi cuốn mọi người, mọi ngành, mọi giới tham gia vào sản xuất?\nA. Phong trào thi yêu nước và tăng gia sản xuất nông nghiệp. | B. Cuộc vận động quần chúng giảm tô và cải cách ruộng đất. | C. Phong trào “Tuần lễ vàng” xây dựng nền tài chính độc lập. | D. Cuộc vận động tăng gia sản xuất và thực hành tiết kiệm. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nhận xét nào sau đây là đúng về mối quan hệ giữa hậu phương và tiền tuyến trong kháng chiến chống Pháp (1945 - 1954)?\nA. Tiền tuyến sẽ quyết định tới sự phát triển kinh tế của hậu phương. | B. Hậu phương và tiền tuyến có mối quan hệ hữu cơ nhau. (DAP AN DUNG) | C. Hậu phương tác động đến phương châm chiến đấu của tiền tuyến. | D. Thắng lợi trên tiền tuyến sẽ thu hẹp phạm vi của hậu phương.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("“Chiến dịch này là một chiến dịch lịch sử của quân đội ta, ta đánh thắng chiến dịch này có ý nghĩa quân sự và ý nghĩa chính trị quan trọng” là nhận định của Chủ tịch Hồ Chí Minh về\nA. chiến dịch Việt Bắc thu - đông 1947. | B. chiến dịch Biên giới thu - đông 1950. | C. chiến dịch Điện Biên Phủ năm 1954. (DAP AN DUNG) | D. cuộc chiến đấu trong các đô thị (12/1946 - 2/1947).")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Ngày 7/2/1965, Mĩ đã dựa vào sự kiện nào để lấy cớ tiến hành chiến tranh phá hoại miền Bắc lần thứ nhất?\nA. Miền Bắc chi viện cho chiến trường miền Nam qua đường Trường Sơn. | B. Quân dân Việt Nam tấn công vào thôn Vạn Tường (Quảng Ngãi). | C. Hải quân của Việt Nam tấn công hải quân Mĩ ở vịnh Bắc Bộ. | D. Quân giải phóng miền Nam tấn công doanh trại quân Mĩ ở Plây-ku. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Tính chất ác liệt của chiến lược “Chiến tranh cục bộ” so với chiến lược “Chiến tranh đặc biệt” của đế quốc Mĩ ở miền Nam Việt Nam được thể hiện qua thủ đoạn nào sau đây?\nA. Rút dần quân đội Mĩ về nước để quân đội Sài Gòn tự đứng vững. | B. Sử dụng chiến thuật quân sự “Trực thăng vận, thiết xa vận”. | C. Mở các cuộc hành quân “Tìm diệt” và “Bình định” tàn khốc. (DAP AN DUNG) | D. Tăng cường thêm lực lượng và vũ khí cho quân đội Sài Gòn.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào không phải là mục đích phong trào đấu tranh chính trị của nhân dân miền Nam những năm 1969 - 1973?\nA. Đòi quyền tự do dân chủ. | B. Đòi cải cách ruộng đất. (DAP AN DUNG) | C. Chống “bình định”. | D. Phá “Ấp chiến lược”.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Thủ đoạn của Mĩ trong chiến lược “Việt Nam hóa chiến tranh” (1969 - 1973) có điểm mới so với các chiến lược chiến tranh trước đó trên lĩnh vực nào?\nA. Quân sự | B. Bình định. | C. Chính trị. | D. Ngoại giao. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Chiến thắng trong chiến dịch Huế - Đà Nẵng năm 1975 của quân dân Việt Nam có ý nghĩa nào sau đây?\nA. Mở đường cho việc vận tải chi viện quy mô lớn từ miền Bắc vào Nam. | B. Góp phần đẩy nhanh quá trình giải phóng miền Nam, thống nhất đất nước. (DAP AN DUNG) | C. Ngăn chặn mọi sự can thiệp trở lại bằng quân sự của đế quốc Mĩ. | D. Chuyển sang giai đoạn Tổng tiến công chiến lược trên toàn miền Nam.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nguyên nhân khách quan góp phần làm nên thắng lợi của cuộc kháng chiến chống Mĩ, cứu nước (1954 - 1975) của nhân dân Việt Nam là\nA. cách mạng Việt Nam có hậu phương miền Bắc không ngừng lớn mạnh. | B. nhân dân ta giàu lòng yêu nước, đoàn kết nhất trí, chiến đấu dũng cảm. | C. cách mạng đặt dưới sự lãnh đạo sáng suốt của Đảng Lao động Việt Nam. | D. nhân dân Mĩ phản đối cuộc chiến tranh xâm lược Việt Nam. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây phản ánh đúng ý nghĩa của phong trào “Vô sản hóa” năm 1928 do Hội Việt Nam Cách mạng Thanh niên tiến hành?\nA. Làm tăng cường số lượng công nhân làm việc trong các nhà máy, đồn điền. | B. Chuẩn bị trực tiếp về tổ chức cho sự ra đời của Đảng Cộng sản Việt Nam. | C. Là mốc đánh dấu phong trào công nhân chuyển sang đấu tranh tự giác. | D. Nâng cao ý thức chính trị cho công nhân, thúc đẩy phong trào phát triển mạnh. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Trong thời kỳ Chiến tranh lạnh, quốc gia nào sau đây không không chịu tác động trực tiếp của Chiến tranh lạnh?\nA. Triều Tiên. | B. Việt Nam. | C. Nhật Bản. (DAP AN DUNG) | D. Đức.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Từ năm 1947, Mỹ thực hiện kế hoạch Mácsan đã tác động như thế nào tới cục diện các nước Đông Âu và Tây Âu?\nA. Mở màn cho quá trình hợp tác, đối thoại về kinh tế. | B. Tạo nên cục diện đối lập về chính trị giữa hai khối. | C. Tạo nên sự phân chia đối lập về kinh tế và chính trị. (DAP AN DUNG) | D. Mở đầu cho sự hình thành cục diện Chiến tranh lạnh.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Điểm tương đồng trong chính sách của chính quyền Xô viết Nghệ - Tĩnh (1930 - 1931) và chính quyền Việt Nam Dân chủ Cộng hòa (1945 - 1946) là\nA. cho phát hành tiền giấy Việt Nam trên phạm vi cả nước. | B. thành lập Hội đồng Nhân dân và Ủy ban Nhân dân các cấp. | C. thành lập lực lượng vũ trang và Hội Liên hiệp quốc dân. | D. kiên quyết trừng trị những thế lực ra mặt phá hoại. (DAP AN DUNG)")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);
  form.addMultipleChoiceItem()
    .setTitle("Đường lối đổi mới được Đảng Cộng sản Việt Nam đề ra từ Đại hội VI (12/1986) xác định trọng tâm là đổi mới về\nA. kinh tế. (DAP AN DUNG) | B. văn hóa. | C. xã hội. | D. . chính trị.")
    .setChoiceValues(["De", "Trung binh", "Kho"])
    .setRequired(false);

  var ss = SpreadsheetApp.create("Phieu cham do kho Lich su 9 — Responses");
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  Logger.log("Form da tao thanh cong!");
  Logger.log("PUBLISHED URL: " + form.getPublishedUrl());
  Logger.log("EDIT URL: " + form.getEditUrl());
  Logger.log("RESPONSE SHEET: " + ss.getUrl());
}
