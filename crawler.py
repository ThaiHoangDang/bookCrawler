from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import requests
import os
from PIL import Image
from reportlab.pdfgen import canvas
import re


print("Đây là một tool để tải chùa sách trên trang Proquest, được tạo ra vì quá bức xúc chả hiểu sao giới hạn số trang tải???")
print()
print("Lưu ý: máy tính bạn cần có Chrome để sử dụng ứng dụng này")
print()
print("Đầu tiên, bạn sẽ cần điền một số thông tin (URL sách, username, pass, etc.)")
print("Sau khi điền xong, một trang web chrome sẽ tự động mở lên và tự động chạy để tải các trang về, bạn sẽ không cần làm gì cả")
print("Yên tâm là các thông tin bạn cung cấp chỉ phục vụ mục đích mở trang và tải, sẽ không bị thu thập đâu 😉")
print()
print("Đầu tiên, bạn cần cung cấp URL trang sách")
print("Lưu ý là chỉ cóp từ https đến docID=XXXXXXXX thôi nhé chứ đừng cóp đoạn sau, tham khảo link bên dưới")
print("Link bên dưới: https://ebookcentral.proquest.com/lib/rmit/reader.action?docID=5359393")
print()
print("Ok bắt đầu thôi!")
print()

# Lấy input từ người dùng
login_url = input("Url đến sách : ")
input_username = input("Username (eg: s123456): ")
input_password = input("Password (Yên tâm đi không ai lấy của bạn đâu 😉): ")
input_firstpage = int(input("Trang tải đầu: "))
input_lastpage = int(input("Trang tải cuối: "))

# Tạo thư mục nếu chưa tồn tại
output_dir = './pages'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Khởi tạo trình điều khiển
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Truy cập địa chỉ
driver.get(login_url)

# Tìm các trường đăng nhập và nhập thông tin
username = driver.find_element(By.ID, "Ecom_User_ID")  
password = driver.find_element(By.ID, "Ecom_Password")

username.send_keys(input_username)  # Thay bằng tên đăng nhập của bạn
password.send_keys(input_password)  # Thay bằng mật khẩu của bạn

# Tìm nút đăng nhập và nhấn vào nó
login_button = driver.find_element(By.ID, "loginButton2")
login_button.click()

# Đợi đăng nhập xong
time.sleep(10)  # Có thể cần thêm thời gian tùy thuộc vào tốc độ kết nối và trang web

for page_num in range(input_firstpage, input_lastpage + 1):
    # Path đến ảnh
    image_url = f"{login_url}&ppg={page_num}&pq-origsite=primo"

    # Tải trang hình ảnh
    driver.get(image_url)
    time.sleep(3)  # Đợi trang tải xong, điều chỉnh tăng giảm tuỳ tốc độ mạng

    # Lấy URL thực của hình ảnh
    try:
        image_element = driver.find_element(By.CLASS_NAME, "mainViewerImg")
        image_src = image_element.get_attribute("src")

        # Chuyển đổi danh sách cookie thành từ điển
        cookies = driver.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        # Tải hình ảnh về
        img_data = requests.get(image_src, cookies=cookie_dict).content
        with open(f'./pages/downloaded_image_page_{page_num}.png', 'wb') as handler:
            handler.write(img_data)

        print(f"Đã tải trang {page_num} thành công.")
    except Exception as e:
        print(f"Không thể tải trang {page_num}: {e}")

# Đóng trình điều khiển
driver.quit()


# Đường dẫn thư mục chứa ảnh
image_dir = "./pages/"

# Lấy danh sách các file ảnh trong thư mục hiện tại
image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]

# Sắp xếp các file ảnh theo số trong tên file
def extract_number(filename):
    match = re.search(r'(\d+)', filename)
    return int(match.group()) if match else 0

image_files.sort(key=extract_number)

# Tạo file PDF
pdf_filename = "book.pdf"
first_image = True

# Khởi tạo canvas và thiết lập kích thước trang dựa trên hình ảnh
c = None
for image_file in image_files:
    img = Image.open(os.path.join(image_dir, image_file))
    width, height = img.size
    
    # Khởi tạo canvas cho trang mới
    if first_image:
        c = canvas.Canvas(pdf_filename, pagesize=(width, height))
        first_image = False
    else:
        c.setPageSize((width, height))

    c.drawImage(os.path.join(image_dir, image_file), 0, 0, width=width, height=height)
    c.showPage()  # Tạo trang mới cho mỗi hình ảnh

c.save()

# Xoá các file ảnh thừa
for image_file in image_files:
    os.remove(os.path.join(image_dir, image_file))

print(f"Đã tạo file PDF '{pdf_filename}' và xoá các ảnh thừa.")
