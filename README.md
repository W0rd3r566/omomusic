# omo Music

**omo** — независимые ReVanced-патчи оформления для YouTube Music. Основа проекта — [официальный шаблон ReVanced Patches](https://github.com/ReVanced/revanced-patches-template) и его Patcher API. Фирменный стиль: чёрный фон, округлая надпись **omo** и маленький голубой знак Play.

> **Статус:** переход на ReVanced-first. Исходники и GitHub Actions для сборки пакета патчей находятся здесь. Совместимость с текущими версиями YouTube Music ещё нужно подтвердить. Это **не APK и не новый открытый клиент YouTube Music**: сам YouTube Music не имеет открытых исходников.

## Что делает omo

| Патч | Действие |
| --- | --- |
| **omo Branding** | Ставит название `omo`, адаптивную иконку, монохромный слой и голубой Play |
| **omo Black** | Изменяет известные тёмные цветовые ресурсы на чёрно-графитовую палитру |

Оба патча работают с ресурсами приложения. Код Google, вход в аккаунт и механизмы платного доступа здесь не распространяются и не изменяются.

**Про Material 3 Expressive:** полноценная замена навигации, экрана плеера и анимаций невозможна лишь изменением нескольких XML-ресурсов. Для такой UI-переработки нужны отдельные проверенные bytecode-патчи под определённые версии приложения. Не выдаём перекраску за готовый Material 3.

## Сборка ReVanced-патчей

Нужны JDK 17, Gradle Wrapper из репозитория, доступ к зависимостям ReVanced через GitHub Packages.

```bash
git clone https://github.com/W0rd3r566/omomusic.git
cd omomusic
python3 scripts/check_assets.py
./gradlew :patches:buildAndroid
```

**GitHub Actions:** [Build omo ReVanced patches](https://github.com/W0rd3r566/omomusic/actions/workflows/build.yml) — после успешной сборки можно забрать артефакт `omo-revanced-patches` (файл `.rvp`). Этот пакет предназначен для совместимого ReVanced Patcher и самостоятельно полученного совместимого приложения. **APK не создаётся** и не распространяется.

## Структура

- `patches/src/main/kotlin/dev/w0rd3r/omo/patches/` — Kotlin-патчи
- `patches/src/main/resources/omo/` — исходники иконки и Android XML-ресурсы
- `assets/omo-icon.svg` — логотип
- `scripts/check_assets.py` — статическая проверка ресурсов
- `native/` — **неактивный эксперимент** с Metrolist; **не используется** в ReVanced-сборке и не является актуальным кодом omo

## Авторство

omo Music — W0rd3r566 и участники проекта, GPL-3.0-or-later. Сборочная инфраструктура основана на [ReVanced Patches Template](https://github.com/ReVanced/revanced-patches-template), GPL-3.0. Проект не аффилирован с Google, YouTube Music или ReVanced.

Использование сторонних патчей может зависеть от версий YouTube Music и условий сервиса.
