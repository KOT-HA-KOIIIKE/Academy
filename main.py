from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Сюда вставляем ссылку на статью
url = "https://selectel.ru/blog/deep-learning-origin/"

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.get(url)

wait = WebDriverWait(driver, 10)

# Проверка мета-описания
meta_description = None

try:
   meta = driver.find_element(By.CSS_SELECTOR, "meta[name='description']")
   meta_description = meta.get_attribute("content")
except:
   meta_description = None

# Основной контейнер
content = wait.until(
   EC.presence_of_element_located((By.CSS_SELECTOR, "div.article-content_content"))
)

# Проверка текста на "Привет, Хабр"
page_text = content.text
has_habr_greeting = "Привет, Хабр" in page_text

# Проверка ссылок на Хабр
links = content.find_elements(By.TAG_NAME, "a")
habr_links = []

for link in links:
   href = link.get_attribute("href") or ""
   text = link.text.strip()

   if "habr.com" in href:
       if not text:
           text = "[без текста]"
       habr_links.append(f"{text} | {href}")

# Проверка баннера
promo_elements = content.find_elements(By.CSS_SELECTOR, "h2.promo-link_title")
banner_exists = len(promo_elements) > 0

# Проверка блока "Читайте также"
read_also_elements = content.find_elements(By.CSS_SELECTOR, "h5.read-also__articles-title")
read_also_exists = len(read_also_elements) > 0

# Проверка ссылки "на полях"
side_link_elements = content.find_elements(By.CSS_SELECTOR, "a.columns-flex_right-link, a.columns-flex_big-link")
side_link_exists = len(side_link_elements) > 0

# Сбор меток
tag_elements = content.find_elements(By.CSS_SELECTOR, "a.tag.f-12")
tags = [tag.text.strip() for tag in tag_elements if tag.text.strip()]

# Проверка изображений
images = content.find_elements(By.TAG_NAME, "img")
image_results = []

for i, img in enumerate(images, start=1):
   alt = img.get_attribute("alt")
   src = img.get_attribute("src") or img.get_attribute("data-src")

   try:
       figure = img.find_element(By.XPATH, "./ancestor::figure[1]")
       figure_class = figure.get_attribute("class") or ""
       rounded = "✅ Есть скругление" if "is-style-rounded" in figure_class else "❌ Нет скругления"
   except:
       rounded = "❌ Нет скругления"

   alt_text = alt if alt and alt.strip() else "❌ alt отсутствует"
   image_results.append(f"{i}. {alt_text} | {src} | {rounded}")

# Проверка ссылок (исключая блок с метками)
bad_links = []

tag_block = content.find_elements(By.CSS_SELECTOR, "div.article-content-tag-block")
tag_block_element = tag_block[0] if tag_block else None

for link in links:
   if tag_block_element:
       try:
           link.find_element(By.XPATH, "./ancestor::div[contains(@class, 'article-content-tag-block')]")
           continue
       except:
           pass

   target = link.get_attribute("target")
   href = link.get_attribute("href")
   text = link.text.strip()

   if target != "_blank":
       if not text:
           text = "[без текста]"
       bad_links.append(f"{text} | {href} | ❌ открывается в той же вкладке")

# Запись в файл
with open("review.txt", "w", encoding="utf-8") as file:
   # Meta description
   file.write("МЕТА-ОПИСАНИЕ:\n")
   if meta_description and meta_description.strip():
       file.write(f"✅ {meta_description}\n")
   else:
       file.write("❌ Нет мета-описания\n")

   # Хабр-паттерны
   file.write("\nХАБР:\n")

   # Приветствие
   if has_habr_greeting:
       file.write("❌ Приветствие для Хабра\n")
   else:
       file.write("✅ Нет приветствия для Хабра\n")

   # Ссылки на Хабр
   if habr_links:
       file.write("\n⚠️ Есть ссылки на Хабр:\n")
       for link in habr_links:
           file.write(link + "\n")
   else:
       file.write("\n✅ Нет ссылок на Хабр\n")

   # Баннер
   file.write("\nБАННЕР:\n")
   file.write("✅ Есть баннер\n" if banner_exists else "❌ Нет баннера\n")

   # Читайте также
   file.write("\nЧИТАЙТЕ ТАКЖЕ:\n")
   file.write("✅ Есть блок ЧИТАЙТЕ ТАКЖЕ\n" if read_also_exists else "❌ Нет блока ЧИТАЙТЕ ТАКЖЕ\n")

   # Ссылка "на полях"
   file.write("\nССЫЛКИ НА ПОЛЯХ:\n")
   file.write("✅ Есть ссылка на полях\n" if side_link_exists else "❌ Нет ссылки на полях\n")

   # Метки
   file.write("\nМЕТКИ:\n")
   if tags:
       for i, tag in enumerate(tags, start=1):
           file.write(f"{i}. {tag}\n")
   else:
       file.write("❌ Нет меток\n")

   # Изображения
   file.write("\nИЗОБРАЖЕНИЯ:\n")
   for line in image_results:
       file.write(line + "\n")

   # Ссылки
   file.write("\nССЫЛКИ:\n")
   if not bad_links:
       file.write("✅ Все ссылки открываются в новой вкладке\n")
   else:
       for line in bad_links:
           file.write(line + "\n")

print(f"Ссылки на Хабр: {len(habr_links)}")
print(f"Приветствие для Хабра: {has_habr_greeting}")
print(f"Мета-описание: {'есть' if meta_description else 'нет'}")
print(f"Баннер: {banner_exists}")
print(f"Читайте также: {read_also_exists}")
print(f"Ссылка на полях: {side_link_exists}")
print(f"Метки: {len(tags)}")
print(f"Изображений: {len(images)}")
print(f"Ссылок: {len(links)}")

driver.quit()