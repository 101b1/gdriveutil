# gdriveutil
Python utility for downloading from / uploading to Google Drive.

Для работы с утилитой необохдимо установить соответствующие пакеты, выполнив команду:
$ pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

Исходный файл gdriveutil.py можно разместить в любой папке.
ВАЖНО: файл credentials.json должен быть в папке вместе с gdriveutils.py!

Список агрументов:
  - [action], принимает значения put (для загрузки в Drive) и get (для загрузки из Drive)
  - [src_path], полный путь к исходному файлу
  - [dest_path], полный путь к конечному файлу

Пример загрузки в Drive:
$ python gdriveutil.py put /home/user/myfile.txt /myfolder/myfile.txt

Пример загрузки из Drive:
$ python gdriveutil.py get /my_google_photo.jpg /home/user/photos/my_google_photo.jpg

При первом запуске в браузере по умолчанию откроется окно авторизации аккаунта Google, сервис спросит о предоставлении утилите доступа к Google Drive.
