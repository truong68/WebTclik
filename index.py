from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import zipfile

# Thông tin proxy
proxy_host = "160.22.173.91"
proxy_port = 39546
proxy_user = "best6395"
proxy_pass = "xedaba89n03"

# Cấu hình proxy cho Chrome
chrome_options = Options()
chrome_options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')
chrome_options.add_argument('--ignore-certificate-errors')

# Đăng nhập proxy (nếu proxy yêu cầu xác thực)
proxy_auth_extension = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{proxy_host}",
                port: parseInt({proxy_port})
            }},
            bypassList: []
        }}
    }};
    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_user}",
                password: "{proxy_pass}"
            }}
        }};
    }}
    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );
"""

# Lưu extension để sử dụng proxy authentication
proxy_auth_plugin_path = 'proxy_auth_plugin.zip'
with zipfile.ZipFile(proxy_auth_plugin_path, 'w') as zp:
    zp.writestr("manifest.json", """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version": "22.0.0"
    }
    """)
    zp.writestr("background.js", proxy_auth_extension)

chrome_options.add_extension(proxy_auth_plugin_path)

# Khởi tạo WebDriver với proxy
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Hàm tìm kiếm và cuộn trang nếu tìm thấy URL yêu cầu
def tim_kiem_va_cuon_trang(tu_khoa):
    try:
        driver.get("https://www.google.com")
        time.sleep(2)
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(tu_khoa)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        max_pages = 5
        current_page = 1
        found = False

        while current_page <= max_pages:
            print(f"Đang kiểm tra trang {current_page}...")

            cites = driver.find_elements(By.XPATH, "//cite")
            for cite in cites:
                url = cite.text
                if "duhocvietphuong.edu.vn" in url:
                    print(f"Đã tìm thấy URL trong cite: {url}")
                    parent_link = cite.find_element(By.XPATH, "..")
                    parent_link.click()
                    time.sleep(5)
                    found = True
                    break

            if found:
                break

            try:
                next_page_button = driver.find_element(By.XPATH, "//a[@id='pnnext']")
                next_page_button.click()
                current_page += 1
                time.sleep(3)
            except Exception:
                print("Không tìm thấy nút 'Tiếp', kết thúc tìm kiếm.")
                break

        if found:
            print("Trang đã tải xong. Bắt đầu cuộn lên và xuống trong 120 giây...")
            start_time = time.time()
            scroll_direction = "down"
            while time.time() - start_time < 120:
                if scroll_direction == "down":
                    driver.execute_script("window.scrollBy(0, 200);")
                    if driver.execute_script("return window.innerHeight + window.scrollY") >= driver.execute_script("return document.body.scrollHeight"):
                        scroll_direction = "up"
                else:
                    driver.execute_script("window.scrollBy(0, -200);")
                    if driver.execute_script("return window.scrollY") == 0:
                        scroll_direction = "down"
                time.sleep(0.5)
        else:
            print(f"Không tìm thấy URL 'duhocvietphuong.edu.vn' cho từ khóa '{tu_khoa}'.")

    except Exception as e:
        print(f"Lỗi xảy ra khi tìm kiếm từ khóa '{tu_khoa}': {e}")

# Đọc từ khóa từ file
keywords_file = "keywords.txt"
with open(keywords_file, "r", encoding="utf-8") as file:
    keywords = [line.strip() for line in file if line.strip()]

# Thực hiện tìm kiếm cho các từ khóa trong danh sách
for keyword in keywords:
    tim_kiem_va_cuon_trang(keyword)
    print(f"Đã hoàn thành tìm kiếm từ khóa: {keyword}")
    time.sleep(120)

# Đóng trình duyệt sau khi hoàn thành
driver.quit()
