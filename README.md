# omo Music

**omo Music** — независимый Android-клиент YouTube Music с нативным интерфейсом **Material 3 Expressive**. Не WebView-оболочка: проект использует открытый музыкальный движок, Media3 и Compose-интерфейс [Metrolist](https://github.com/MetrolistGroup/Metrolist).

> **Статус:** исходники Android-клиента импортированы и брендированы. APK и функции требуют подтверждения сборкой CI и тестирования на устройстве. Это ранняя разработка, не стабильный релиз.

## Структура

| Путь | Что внутри |
| --- | --- |
| [native/](native/) | Основной Android-клиент: проигрывание, поиск, библиотека, очередь, плейлисты и Material 3 Expressive |
| [patches/](patches/) | Отдельные ReVanced-патчи оформления для оригинального YouTube Music |
| [assets/omo-icon.svg](assets/omo-icon.svg) | Фирменный логотип omo с мягким голубым ▶ |
| [scripts/import_native.py](scripts/import_native.py) | Импорт открытой кодовой базы Android-клиента |
| [scripts/brand_native.py](scripts/brand_native.py) | Применение фирменного стиля, иконки, package ID и стандартных настроек |

## Фирменный стиль omo

- Чёрная тема и голубой акцент **#A7D7FF** по умолчанию.
- Круглая адаптивная и монохромная иконка.
- Material 3 Expressive: настраиваемый интерфейс, анимации и мини-плеер.
- Настройка темы, внешнего вида проигрывателя, шрифтов и навигации через существующие настройки.
- Независимый ID Android-приложения: **dev.w0rd3r.omomusic**.
- Обновления и Discord application ID исходного клиента отключены до собственной реализации.

**План следующих доработок:** отдельные экраны в стиле omo, быстрые пресеты, улучшенные анимации, персонализация плеера и проверка совместимости на реальных устройствах.

## Сборка Android APK

Требуются **Temurin JDK 25**, Android SDK **37.1** и зависимости Gradle.

~~~bash
git clone https://github.com/W0rd3r566/omomusic.git
cd omomusic/native
./gradlew :androidApp:assembleDebug
~~~

Ожидаемый путь результата: native/androidApp/build/outputs/apk/debug/.

[GitHub Actions: Build omo Music Android](https://github.com/W0rd3r566/omomusic/actions/workflows/native-build.yml) выполняет сборку и прикладывает APK **только при успехе**. Факт появления исходников не означает успешную компиляцию.

## Старые ReVanced-патчи

Эта часть независима от Android-клиента и использует JDK 17:

~~~bash
python3 scripts/check_assets.py
./gradlew build
~~~

Результат — пакет патчей, а не модифицированный APK YouTube Music. Совместимость с конкретной версией приложения отдельно не подтверждена.

## Авторство и лицензии

Основой native-клиента является [Metrolist](https://github.com/MetrolistGroup/Metrolist), распространяемый по GNU GPL v3. Исходники и оригинальные лицензии сохранены; точная импортированная ревизия указана в [native/UPSTREAM.md](native/UPSTREAM.md).

Собственные патчи и оформление omo — W0rd3r566 и участники проекта. При распространении сборок и модификаций соблюдайте GPL и лицензии сторонних компонентов.

omo Music не является продуктом Google, YouTube, Metrolist или ReVanced. Работа с YouTube Music через сторонний клиент может нарушать условия сервиса и зависеть от изменений его API.
