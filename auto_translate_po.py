from googletrans import Translator
import polib

# Khởi tạo translator
translator = Translator()


po = polib.pofile('locale/en/LC_MESSAGES/django.po')

for entry in po:
    if not entry.msgstr.strip():
        translated = translator.translate(entry.msgid, src='vi', dest='en').text
        entry.msgstr = translated
        print(f'Dịch: "{entry.msgid}" -> "{entry.msgstr}"')

po.save('locale/en/LC_MESSAGES/django_translated.po')
# xong thì đổi tên file mới này thành django.po replace cái cũ đi nhee
print("Hoàn tất dịch tự động!")
