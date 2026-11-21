# omo Music

**omo Music** — независимый музыкальный клиент для Android на **Kotlin + Jetpack Compose**. Это **устанавливаемое приложение**, не ReVanced-патчи, WebView или модифицированный APK YouTube Music.

Визуальный язык: **Material 3 Expressive**, graphite/black, плавные формы и аккуратные голубые акценты. Исходники открыты.

## Разработка

Основной Android-проект расположен в **[client/](client/)**.

- **Музыка:** поиск YouTube Music, очередь, фоновое воспроизведение, плейлисты, локальная медиатека, рекомендации и управление через системную медиасессию реализуются на базе открытого движка [OuterTune](https://github.com/OuterTune/OuterTune) (основан на InnerTune).
- **Новый интерфейс omo:** собственная стартовая панель с переходами к поиску и настройкам; чёрно-графитовая тема, фирменный голубой акцент, оригинальная иконка.
- **Настройка оформления:** пять акцентных палитр (Sky, Mint, Lavender, Coral, Amber), три пресета скругления (Soft, Expressive, Round), системная/тёмная/светлая тема, адаптация под цвета обложки и другие параметры движка. Предпочтения сохраняются в Android DataStore.
- **Сборка:** отдельный application ID `dev.w0rd3r.omomusic`, GitHub Actions собирает Android debug APK.

Важное уточнение: текущая версия — ранняя разработка. Наличие кода не подтверждает успешную сборку, работу всех YouTube Music функций или стабильность на реальном телефоне.

## Сборка из исходников

Требуются **JDK 21**, **Android SDK API 36**, доступ к Maven Central и Google Maven. Проект использует Gradle Wrapper и Kotlin.

```bash
git clone https://github.com/W0rd3r566/omomusic.git
cd omomusic/client
chmod +x gradlew
./gradlew :app:assembleCoreDebug
```

После успешной сборки APK появится в `client/app/build/outputs/apk/core/debug/`.

**[GitHub Actions: Build omo Music Android APK](https://github.com/W0rd3r566/omomusic/actions/workflows/omo-build.yml)** — артефакт `omo-music-android-debug` прикрепляется только при успешном завершении.

## Структура

| Путь | Содержимое |
| --- | --- |
| `client/app/` | Код Kotlin, Compose UI, Media3 и ресурсы Android |
| `client/material-color-utilities/` | Цветовые инструменты движка |
| `client/UPSTREAM.md` | Ссылка на upstream и точный исходный коммит |
| `client/LICENSE` | Лицензия открытой основы |
| `scripts/import_omo_android.py` | Воспроизводимый импорт исходного движка с omo-изменениями |
| `assets/` | Оригинальная графика |
| `patches/`, `native/` | Старые эксперименты, не входят в сборку текущего клиента |

## Лицензия и авторство

Основа проигрывателя — OuterTune/InnerTune, **GPL-3.0**, с сохранёнными upstream copyright notices и лицензией; [указанная ревизия](client/UPSTREAM.md). Собственные модификации omo Music — © 2026 W0rd3r566, GPL-3.0-or-later. Проект не аффилирован с Google, YouTube или ReVanced.
