/**
 * Google Apps Script: Tao Google Form khao sat do kho cau hoi - Su 9
 *
 * CACH DUNG:
 *   1. Mo https://script.google.com/ -> New project -> dan TOAN BO file nay
 *   2. Save (Ctrl+S)
 *   3. Chon function createForm_A (va _B/_C neu co) tu dropdown
 *   4. Bam RUN (▶) -> lan dau se yeu cau grant permission, cu dong y
 *   5. Xem Execution log de lay PUBLISHED URL gui cho hoc sinh
 *   6. QUAN TRONG: KHONG doi thu tu cau hoi sau khi tao — thu tu phai khop
 *      voi student_exam_manifest.json (sinh cung luc, dung de cham bai)
 */


function createForm_A() {
  var form = FormApp.create("De A - Khao sat Lich su 9 (Cold-Warm)");
  form.setTitle("De A - Khao sat doc lap p-value - Lich su 9");
  form.setDescription(
    "Bai lam gom 45 cau trac nghiem, khong tinh diem, chi phuc vu " +
    "nghien cuu ve uoc luong do kho cau hoi. Vui long lam MOT MINH, khong trao doi.\n\n" +
    "Nhap dung MA HOC SINH duoc phat de doi chieu ket qua an danh.\n" +
    "Thoi gian de nghi: 45 phut."
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);
  form.setShowLinkToRespondAgain(false);
  // KHONG bat setShuffleQuestions() — thu tu cau PHAI co dinh de khop cot
  // trong Sheet ket qua voi student_exam_manifest.json khi cham bai.

  form.addTextItem()
    .setTitle("Ma hoc sinh")
    .setHelpText("Nhap dung ma so duoc phat, dung de doi chieu an danh.")
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("Nenxơn Mandela là lãnh tụ của phong trào đấu tranh")
    .setChoiceValues(["giải phóng dân tộc ở châu Phi", "chống chế độ độc tài thân Mĩ ở Cuba", "chống chế độ phân biệt chủng tộc ở Nam Phi", "xóa bỏ đói nghèo ở Nam Phi"])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Cuộc nội chiến ở Trung Quốc (1946-1949) diễn ra giữa các lực lượng nào?")
    .setChoiceValues(["Chính quyền Mãn Thanh và Trung Hoa Dân Quốc", "Chính quyền Mãn Thanh và Đảng Cộng sản Trung Quốc", "Chính quyền Mãn Châu với Đảng Cộng sản.", "Quốc dân Đảng và Đảng Cộng sản Trung Quốc"])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Nhiệm vụ tập hợp xây dựng lực lượng khối đoàn kết dân tộc từ năm 1951 đến năm 1954 do mặt trận nào đảm nhiệm")
    .setChoiceValues(["Liên minh nhân dân Việt Miên Lào", "Mặt trận Liên Việt", "Mặt trận Việt Minh", "Hội Liên Việt"])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Năm 1923, Nguyễn Ái Quốc chính thức được bầu vào tổ chức nào sau đây?")
    .setChoiceValues(["Đảng Xã hội Pháp.", "Hội đồng Quốc tế Nông dân.", "Quốc tế Cộng sản.", "Đảng Cộng sản Pháp."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Từ tháng 9/1940 đến tháng 3/1945, nhân dân Việt Nam chịu hai tầng cai trị áp bức bóc lột của thế lực nào sau đây?")
    .setChoiceValues(["Thực dân Pháp và Quân phiệt Nhật.", "Tư sản dân tộc và đại địa chủ.", "Quân phiệt Nhật và tay sai.", "Thực dân Pháp và phong kiến."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Từ năm 1922, lãnh đạo phong trào đấu tranh của giai cấp công nhân Nhật Bản là")
    .setChoiceValues(["Quốc dân Đảng.", "Đảng Quốc đại.", "Đảng Dân chủ.", "Đảng Cộng sản."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Mĩ mở cuộc hành quân đánh vào căn cứ Dương Minh Châu (Bắc Tây Ninh) nhằm mục đích nào sau đây?")
    .setChoiceValues(["Giành lại thế chủ động trên chiến trường chính.", "Phá hoại hậu phương, xây dựng các ấp chiến lược.", "Tiêu diệt quân chủ lực và cơ quan đầu não của ta.", "Uy hiếp tinh thần chiến đấu của quân dân ta."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Trọng tâm trong chính sách đối ngoại của Mỹ giai đoạn 1991 - 2000 là")
    .setChoiceValues(["cố gắng thiết lập trật tự thế giới mới theo xu hướng đơn cực.", "cạnh tranh với Trung Quốc và các cường quốc khác.", "phát động chiến lược toàn cầu chống khủng bố.", "cải thiện quan hệ với Liên Xô và phe xã hội chủ nghĩa."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Sau Chiến tranh thế giới thứ hai, Mỹ đã thành lập khối quân sự ở khu vực nào sau đây?")
    .setChoiceValues(["Đông Bắc Á.", "Đông Nam Á.", "Bắc Phi.", "Đông Âu."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây phản ánh đúng đặc điểm của Nhật Bản ngay sau Chiến tranh thế giới thứ nhất?")
    .setChoiceValues(["Cuộc khủng hoảng tài chính trầm trọng đã diễn ra ở Tôkiô.", "Nội bộ giới quân phiệt và tài phiệt Nhật có sự phân hóa sâu sắc.", "Nền kinh tế Nhật Bản phát triển nhanh chóng sau chiến tranh.", "Chính quyền Nhật Bản tiến hành quân sự hóa bộ máy nhà nước."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Trong những năm 1960 - 1965, khẩu hiệu “Một tấc không đi, một li không rời” ra đời trong phong trào đấu tranh nào của quân dân miền Nam?")
    .setChoiceValues(["“Phụ nữ ba đảm đang”.", "Phá “Ấp chiến lược”.", "“Đồng khởi”.", "“Người cày có ruộng”."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Quốc gia đầu tiên công nhận và đặt quan hệ ngoại giao với Việt Nam Dân chủ Cộng hòa là quốc gia nào")
    .setChoiceValues(["Tiệp Khắc", "Trung Quốc", "Liên Xô", "Cộng hòa Dân chủ Đức"])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Hành động nào sau đây của Trung Quốc đối với Việt Nam trong nửa sau những năm 70 của thế kỷ XX là biểu hiện cho quan hệ căng thẳng giữa hai nước?")
    .setChoiceValues(["Cấm vận về kinh tế, cô lập về chính trị.", "Ngăn cản Việt Nam gia nhập Liên hợp quốc.", "Công nhận và ủng hộ Chính quyền Sài Gòn.", "Chấm dứt các viện trợ kinh tế, kỹ thuật."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Chính sách thống trị của thực dân Pháp ở Đông Dương trong những năm Chiến tranh thế giới thứ hai nhằm mục đích nào sau đây?")
    .setChoiceValues(["Vơ vét sức người, sức của ở Đông Dương để phục vụ chiến tranh.", "Chống lại sự bành trướng của chủ nghĩa phát xít ở châu Á.", "Chuẩn bị tuyên chiến với quân Nhật khi chúng vào Đông Dương.", "Khôi phục và phát triển lại nền kinh tế đang bị khủng hoảng."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào không phản ánh đúng về chiến lược “Chiến tranh đặc biệt” (1961 - 1965) của Mĩ thực hiện ở miền Nam Việt Nam?")
    .setChoiceValues(["Được tiến hành bằng quân đội Sài Gòn do cố vấn Mĩ chỉ huy.", "Là chiến lược chiến tranh có quy mô lớn và mức độ ác liệt nhất.", "Là hình thức chiến tranh xâm lược thực dân kiểu mới của Mĩ.", "Nhằm chống lại lượng cách mạng và nhân dân miền Nam."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Năm 1929, tổ chức Việt Nam Quốc dân đảng có hoạt động tiêu biểu nào sau đây?")
    .setChoiceValues(["Ám sát toàn quyền Đông Dương Méc-lanh.", "Ám sát trùm mộ phu Ba-danh.", "Khởi nghĩa Yên Bái.", "Đấu tranh đòi thả Nguyễn An Ninh."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Thông điệp của Tổng thống Truman tại Quốc hội Mỹ (3/1947) đã")
    .setChoiceValues(["ngăn chặn quá trình mở rộng của chủ nghĩa xã hội.", "tạo nên sự đối lập giữa các nước Đông Âu và Tây Âu.", "củng cố hơn nữa mối quan hệ giữa Mỹ và Tây Âu.", "mở đầu việc xác lập trật tự hai cực trên thế giới."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Sự kiện nào sau đây đánh dấu chủ nghĩa xã hội đã vượt ra khỏi phạm vi một nước (Liên Xô) và bước đầu trở thành hệ thống thế giới?")
    .setChoiceValues(["Sự ra đời nhà nước Cộng hoà Nhân dân Trung Hoa.", "Sự ra đời nhà nước Cộng hoà Cuba ở châu Mỹ.", "Chủ nghĩa xã hội ra đời ở Việt Nam và Triều Tiên.", "Sự ra đời các nhà nước Dân chủ Nhân dân Đông Âu."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Năm 1949, Liên Xô và các nước Đông Âu thành lập Hội đồng tương trợ kinh tế (SEV) nhằm mục đích nào sau đây?")
    .setChoiceValues(["Đạt được thế cân bằng về sức mạnh quân sự đối với các nước Tây Âu.", "Viện trợ không hoàn lại cho các nước Đông Âu phát triển kinh tế.", "Tăng cường chạy đua vũ trang với các nước tư bản chủ nghĩa.", "Tăng cường sự hợp tác giữa các nước xã hội chủ nghĩa ở châu Âu."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Năm 1965, Mĩ ồ ạt đưa quân viễn chinh, quân đồng minh vào chiến trường miền Nam Việt Nam vì")
    .setChoiceValues(["muốn tiến hành cuộc đảo chính lật đổ Ngô Đình Diệm.", "muốn nhanh chóng kết thúc chiến tranh ở Việt Nam.", "muốn đẩy mạnh chiến tranh ra cả ba nước Đông Dương.", "quân đội Sài Gòn không có khả năng tự đứng vững."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Sự kiện nào sau đây không tác động mạnh mẽ đến tiến trình Việt Nam trong những năm 1939 - 1945?")
    .setChoiceValues(["Nhật mở rộng cuộc chiến tranh ra châu Á - Thái Bình Dương.", "Đức xâm lược Pháp, Pháp phải nuôi số quân Đức chiếm đóng.", "Sự ra đời và hoạt động tích cực của tổ chức Liên hợp quốc.", "Quân phiệt Nhật Bản đầu hàng phe Đồng minh vô điều kiện."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây không phải mục đích của Pháp khi đề ra kế hoạch Na-va năm 1953?")
    .setChoiceValues(["Kết thúc chiến tranh ở Việt Nam trong danh dự.", "Biến Điện Biên Phủ thành pháo đài bất khả xâm phạm.", "Xoay chuyển cục diện chiến tranh Đông Dương.", "Chuyển bại thành thắng trong vòng 18 tháng."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Hội nghị Ban Chấp hành Trung ương Đảng (5/1941) tạm gác khẩu hiệu “Cách mạng ruộng đất”, đề ra khẩu hiệu “Tịch thu ruộng đất của đế quốc và Việt gian chia cho dân cày” đã chứng tỏ")
    .setChoiceValues(["Đảng đã vận dụng sáng tạo chủ trương của phe Đồng minh chống phát xít.", "nhiệm vụ dân chủ được tiến hành từng bước để phục vụ nhiệm vụ dân tộc.", "vấn đề dân cày ít quan trọng trong bối cảnh đất nước chưa được giải phóng.", "Việt Nam cần tập trung nhiệm vụ để chống đế quốc trên lĩnh vực kinh tế."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Cuộc kháng chiến chống quân Nhật của nhân dân Trung Quốc (1937 - 1945) đã")
    .setChoiceValues(["trở thành thắng lợi tiên phong trong đấu tranh chống phát xít.", "quyết định đến số phận của Nhật trong chiến tranh thế giới.", "buộc Nhật hoàng tuyên bố đầu hàng Đồng minh vô điều kiện.", "làm tiêu hao và tiêu diệt một bộ phận lớn quân Nhật."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Sự kiện nào đánh dấu việc Mĩ bắt đầu dính líu và can thiệp vào cuộc chiến tranh Đông Dương")
    .setChoiceValues(["Kí với Pháp Hiệp định phòng thủ chung Đông Dương", "Giúp Pháp thực hiện kế hoạch Đờlát đơTátxinhi", "Giúp Pháp thực hiện kế hoạch Rơve", "Kí với Bảo Đại Hiệp ước hợp tác kinh tế Việt Mĩ"])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Trong thời kì 1939 - 1945, Trung ương Đảng và lãnh tụ Hồ Chí Minh quyết định đặt nhiệm vụ giải phóng dân tộc lên hàng đầu dựa trên cơ sở nào sau đây?")
    .setChoiceValues(["Mâu thuẫn giữa nhân dân Việt Nam với Pháp - Nhật trở nên gay gắt.", "Chiến tranh thế giới thứ hai bùng nổ, nước Pháp bị phát xít Đức chiếm đóng.", "Nhiệm vụ dân chủ giành ruộng đất cho dân cày không còn phù hợp.", "Quân phiệt Nhật vào miền Bắc Việt Nam, lật đổ sự thống trị của Pháp."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Nguyên nhân sâu xa dẫn đến bùng nổ Chiến tranh thế giới thứ hai là gì?")
    .setChoiceValues(["Sự phát triển không đều của chủ nghĩa tư bản", "Khủng hoảng kinh tế 1929-1933", "Sự xuất hiện của chủ nghĩa phát xít", "Chính sách thỏa hiệp, nhượng bộ của Anh, Pháp"])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây phản ánh đúng ý nghĩa của công cuộc Đổi mới đất nước giai đoạn 1986 - 1991?")
    .setChoiceValues(["Đưa Việt Nam dần thoát khỏi tình trạng khủng hoảng.", "Thu nhập bình quân đầu người của Việt Nam đạt tốp đầu của châu Á.", "Mỹ tuyên bố xoá bỏ lệnh cấm vận đối với Việt Nam.", "Đưa Việt Nam trở thành cường quốc công nghiệp trong khu vực."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Trong cuộc kháng chiến chống Mĩ, cứu nước (1954 - 1975), Tây Nguyên là nơi được Đảng Lao động Việt Nam chọn để mở đầu cho sự kiện nào?")
    .setChoiceValues(["Trận “Điện Biên Phủ trên không” cuối 1972.", "Tổng tiến công và nổi dậy Xuân năm 1975.", "Tổng tiến công và nổi dậy Xuân Mậu Thân 1968.", "Cuộc tiến công chiến lược năm 1972."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây phản ánh vị thế của Đà Nẵng trong chiến lược của Mỹ ở miền Nam Việt Nam?")
    .setChoiceValues(["Căn cứ phòng thủ của địch để bảo vệ Sài Gòn từ phía Đông.", "Là thành phố lớn tập trung nhiều cơ quan đầu não của địch.", "Căn cứ quân sự liên hợp lớn nhất của Mĩ và quân đội Sài Gòn.", "Là địa bàn chiến lược quan trọng để chống phá miền Bắc."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Để đấu tranh chống ngoại xâm nội phản (1945 - 1946), Đảng và Chính phủ Việt Nam đã sử dụng chính sách nào sau đây?")
    .setChoiceValues(["Hòa với kẻ thù nguy hiểm nhất để có thời gian hòa bình.", "Ngả về phía các nước Đồng minh để chống nội phản.", "Từng bước phân hóa và cô lập kẻ thù của cách mạng.", "Khoét sâu mâu thuẫn giữa các nước đồng minh."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Hội nghị Ianta 1945 có sự tham gia của các nước nào")
    .setChoiceValues(["Liên Xô Mĩ Anh", "Mĩ Liên Xô Trung Quốc", "Anh Pháp Đức", "Anh Pháp Nhật Bản"])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây phản ánh đúng đặc điểm về mặt xã hội của Liên Xô trong những năm 1945 - 1973?")
    .setChoiceValues(["Giai cấp địa chủ phong kiến sở hữu nhiều ruộng đất, làm chủ về kinh tế ở nông thôn.", "Xã hội có sự phân hóa triệt để, loại bỏ phương thức sản xuất tư bản chủ nghĩa.", "Nhà nước tiến hành quốc hữu hóa các xí nghiệp của tư bản, cải tạo xã hội chủ nghĩa.", "Nhân dân tin tưởng vào sự lãnh đạo của Đảng và con đường xây dựng chủ nghĩa xã hội."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Trong những năm 20 của thế kỉ XX, chính đảng nào nắm quyền ở Mỹ?")
    .setChoiceValues(["Đảng Bảo thủ.", "Đảng Cộng hòa.", "Đảng Dân chủ.", "Đảng Tự do."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Việc kí Hiệp định Giơ-ne-vơ năm 1954 có ý nghĩa nào sau đây đối với dân tộc?")
    .setChoiceValues(["Là mốc đánh dấu chế độ quân chủ ở Việt Nam đã hoàn toàn sụp đổ.", "Kết thúc thắng lợi hoàn toàn cuộc kháng chiến chống thực dân Pháp ở Việt Nam.", "Là mốc đánh dấu sự sụp đổ hoàn toàn của chủ nghĩa thực dân mới ở Việt Nam.", "Chứng tỏ cuộc cách mạng dân tộc dân chủ nhân dân đã hoàn thành trong cả nước."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Khi thực dân Pháp trở lại xâm lược (23/9/1945), quân dân Sài Gòn - Chợ Lớn đã")
    .setChoiceValues(["nhanh chóng đầu hàng thực dân Pháp.", "hòa hoãn với Pháp để giữ vững hòa bình.", "hợp tác với thực dân Pháp.", "kiên quyết đứng lên chống Pháp."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Công cuộc khôi phục kinh tế, hàn gắn vết thương chiến tranh ở Liên Xô từ năm 1945 đến 1950 có ý nghĩa nào sau đây?")
    .setChoiceValues(["Quyết định đến thành bại trong chạy đua vũ trang với Mỹ.", "Khắc phục được những khó khăn của Chiến tranh thế giới hai.", "Đạt được thế cân bằng về sức mạnh nguyên tử với Mỹ.", "Là nền tảng vững chắc để Liên Xô xây dựng chủ nghĩa xã hội."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Trong những năm 5060 của thế kỉ XX nền kinh tế Kiên Xô phát triển mạnh")
    .setChoiceValues(["chiếm 25 sản lượng điện toàn thế giới", "chiếm 20 sản lượng công nghiệp toàn thế giới", "chiếm 30 sản lượng than toàn thế giới", "chiếm 20 sản lượng nông nghiệp toàn thế giới"])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Theo quy định của Hiến pháp Mỹ, hai đảng nào thay nhau lên nắm chính quyền?")
    .setChoiceValues(["Đảng Tự do và Đảng Bảo thủ.", "Đảng Cộng sản và Đảng Xã hội.", "Đảng Cộng hòa và Đảng Xã hội.", "Đảng Dân chủ và Đảng Cộng hòa."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Phong trào “vô sản hóa” do Hội Việt Nam Cách mạng Thanh niên phát động và thực hiện là")
    .setChoiceValues(["phương thức tự rèn luyện của những chiến sĩ cách mạng tiến bộ.", "cơ hội thuận lợi giúp những người cộng sản về nước hoạt động.", "điều kiện để công nhân phát triển về số lượng và trở thành giai cấp.", "mốc đánh dấu phong trào công nhân hoàn toàn trở thành tự giác."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Sang thế kỷ XXI, nền kinh tế Hàn Quốc đã đạt được vị thế nào sau đây?")
    .setChoiceValues(["Nắm giữ chuỗi cung ứng toàn cầu ở khu vực Đông Bắc Á.", "Có nền kinh tế quy lớn lớn nhất ở khu vực Đông Bắc Á.", "Đi đầu thế giới trong việc sản xuất ô tô và chất bán dẫn.", "Trở thành 1 trong 15 nước có nền kinh tế lớn nhất thế giới."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Sự kiện nào sau đây đánh dấu sự tan vỡ mối quan hệ Đồng minh chống phát xít giữa Mĩ và Liên Xô sau Chiến tranh thế giới thứ hai?")
    .setChoiceValues(["Việc Liên Xô chế tạo thành công bom nguyên tử (1949).", "Sự phân chia phạm vi đóng quân giữa Mĩ và Liên Xô.", "Sự ra đời của Tổ chức Hiệp ước Bắc Đại Tây Dương.", "Mĩ chính thức phát động Chiến tranh lạnh (1947)."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Nội dung nào sau đây phản ánh đường lối đối ngoại của chính phủ Mỹ trước các cuộc chiến tranh xâm lược của các nước phát xít trong những năm 30 của thế kỷ XX?")
    .setChoiceValues(["Kêu gọi các nước tư bản thành lập một liên minh để tiêu diệt chủ nghĩa phát xít", "Thực hiện chính sách nhượng bộ phát xít để giữ vững hòa mình ở châu Mỹ.", "Ban hành đạo luật trung lập, không can thiệp vào các sự kiện bên ngoài châu Mỹ.", "Đề xuất thành lập phe đồng minh để đoàn kết với Liên Xô chống lại phát xít."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Sau thắng lợi của Cách mạng tháng Mười Nga năm 1917, nhiệm vụ hàng đầu của Chính quyền Xô viết là gì?")
    .setChoiceValues(["Đập tan bộ máy nhà nước cũ, xây dựng nhà nước mới của người lao động.", "Đưa nước Nga giành những thắng lợi quan trọng trong chiến tranh thế giới.", "Xoá bỏ cơ sở vật chất còn lại của chế độ phong kiến chuyên chế Nga hoàng.", "Mở rộng hơn nữa phạm vi ảnh hưởng của nước Nga đến các châu lục khác."])
    .setRequired(true);
  form.addMultipleChoiceItem()
    .setTitle("Sự kiện nào đánh dấu sự phục hồi lực lượng lãnh đạo cách mạng của Đảng Cộng sản Đông Dương giai đoạn 1932 - 1935?")
    .setChoiceValues(["Hội nghị Ban Chấp hành Trung ương Đảng (5/1941).", "Hội nghị Ban Chấp hành Trung ương Đảng (11/1939).", "Hội nghị Ban Chấp hành Trung ương Đảng (7/1936).", "Đại hội đại biểu lần thứ nhất của Đảng (3/1935)."])
    .setRequired(true);

  var ss = SpreadsheetApp.create("De A - Ket qua");
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  Logger.log("De A da tao xong!");
  Logger.log("PUBLISHED URL: " + form.getPublishedUrl());
  Logger.log("EDIT URL: " + form.getEditUrl());
  Logger.log("RESPONSE SHEET: " + ss.getUrl());
}
