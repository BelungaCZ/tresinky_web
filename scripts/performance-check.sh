#!/bin/bash

# performance-check.sh - Быстрая проверка производительности сайта с сохранением истории
# Использование: ./scripts/performance-check.sh [URL] [--history] [--api-key KEY]

# Парсинг аргументов
SHOW_HISTORY=false
URL="https://sad-tresinky-cetechovice.cz"
# Встроенный API ключ для удобства. Если не работает - получите новый:
# https://console.cloud.google.com/apis/credentials
API_KEY="AIzaSyAv9PtiPVIEnC0jf73hh6Gkm6ZTAlbUwyE"

for arg in "$@"; do
    case $arg in
        --history)
            SHOW_HISTORY=true
            ;;
        --api-key)
            shift
            API_KEY="$1"
            ;;
        http*)
            URL="$arg"
            ;;
    esac
done

# Проверка API ключа из переменной окружения (переопределяет встроенный)
if [ -n "$PAGESPEED_API_KEY" ]; then
    API_KEY="$PAGESPEED_API_KEY"
fi

HISTORY_FILE="logs/performance-history.log"
TEMP_FILE="logs/temp-performance.log"

# Создаем папку logs если она не существует
mkdir -p logs

# Если запрошена только история, показываем её и выходим
if [ "$SHOW_HISTORY" = true ]; then
    if [ ! -f "$HISTORY_FILE" ]; then
        echo "📝 История измерений пуста. Файл $HISTORY_FILE не найден."
        echo ""
        echo "💡 Запустите обычный тест для создания истории:"
        echo "   ./scripts/performance-check.sh"
        exit 0
    fi
    
    echo "�� История последних 5 измерений:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    # Каждая запись занимает 9 строк, показываем первые 5 записей (45 строк)
    head -45 "$HISTORY_FILE" | while IFS= read -r line; do
        echo "   $line"
    done
    echo ""
    
    # Подсчитываем общее количество записей
    total_records=$(grep -c "^\[" "$HISTORY_FILE")
    echo "📊 Всего записей в истории: $total_records"
    exit 0
fi

echo "🚀 Запуск проверки производительности для: $URL"
echo "⏰ Время: $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Проверка доступности jq
if ! command -v jq &> /dev/null; then
    echo "❌ jq не установлен. Для детального анализа установите jq:"
    echo "   brew install jq  # macOS"
    echo "   apt install jq   # Ubuntu/Debian" 
    echo ""
fi

# Переменные для сохранения результатов
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
MOBILE_SCORE="N/A"
DESKTOP_SCORE="N/A"
MOBILE_LCP="N/A"
MOBILE_FID="N/A"
MOBILE_CLS="N/A"
DESKTOP_LCP="N/A"
DESKTOP_FID="N/A"
DESKTOP_CLS="N/A"
# Дополнительные метрики Mobile
MOBILE_FCP="N/A"
MOBILE_SI="N/A"
MOBILE_TTI="N/A"
MOBILE_FMP="N/A"
MOBILE_FCI="N/A"
MOBILE_EIL="N/A"
MOBILE_TBT="N/A"
# Дополнительные метрики Desktop
DESKTOP_FCP="N/A"
DESKTOP_SI="N/A"
DESKTOP_TTI="N/A"
DESKTOP_FMP="N/A"
DESKTOP_FCI="N/A"
DESKTOP_EIL="N/A"
DESKTOP_TBT="N/A"
HTTP_STATUS="N/A"
RESPONSE_TIME="N/A"

# Функция для проверки PageSpeed
check_pagespeed() {
    local strategy=$1
    local icon=$2
    
    echo "$icon Проверка PageSpeed Insights ($strategy)..."
    
    local api_url="https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    local url_params="url=$URL&strategy=$strategy&category=performance"
    
    # Добавляем API ключ если он есть
    if [ -n "$API_KEY" ]; then
        url_params="$url_params&key=$API_KEY"
        echo "   🔑 Используется API ключ"
    else
        echo "   ⚠️  Без API ключа (ограниченные запросы)"
    fi
    
    local response=$(curl -s "$api_url?$url_params")
    
    # Проверка на ошибки API
    if echo "$response" | jq -e '.error' > /dev/null 2>&1; then
        local error_message=$(echo "$response" | jq -r '.error.message // "Unknown error"')
        local error_code=$(echo "$response" | jq -r '.error.code // "Unknown"')
        
        echo "   ❌ Ошибка API (код $error_code): $error_message"
        
        if [[ "$error_code" == "429" ]]; then
            if [ -z "$API_KEY" ]; then
                echo "   💡 Превышен лимит запросов. Получите API ключ на:"
                echo "      https://developers.google.com/speed/docs/insights/v5/get-started"
            else
                echo "   💡 Превышен лимит даже с API ключом. Попробуйте позже."
            fi
        elif [[ "$error_code" == "400" ]]; then
            echo "   💡 Проверьте правильность API ключа и URL"
        fi
        
        echo ""
        return
    fi
    
    if command -v jq &> /dev/null; then
        # Проверяем наличие lighthouseResult
        if echo "$response" | jq -e '.lighthouseResult' > /dev/null 2>&1; then
            local score=$(echo "$response" | jq -r '.lighthouseResult.categories.performance.score // null | if . == null then "N/A" else (. * 100 | floor) end')
            
            # Основные метрики Core Web Vitals
            local lcp=$(echo "$response" | jq -r '.lighthouseResult.audits["largest-contentful-paint"].displayValue // "N/A"')
            local fid=$(echo "$response" | jq -r '.lighthouseResult.audits["max-potential-fid"].displayValue // "N/A"')
            local cls=$(echo "$response" | jq -r '.lighthouseResult.audits["cumulative-layout-shift"].displayValue // "N/A"')
            
            # Дополнительные метрики производительности
            local fcp=$(echo "$response" | jq -r '.lighthouseResult.audits["first-contentful-paint"].displayValue // "N/A"')
            local si=$(echo "$response" | jq -r '.lighthouseResult.audits["speed-index"].displayValue // "N/A"')
            local tti=$(echo "$response" | jq -r '.lighthouseResult.audits["interactive"].displayValue // "N/A"')
            local fmp=$(echo "$response" | jq -r '.lighthouseResult.audits["first-meaningful-paint"].displayValue // "N/A"')
            local fci=$(echo "$response" | jq -r '.lighthouseResult.audits["first-cpu-idle"].displayValue // "N/A"')
            local eil=$(echo "$response" | jq -r '.lighthouseResult.audits["estimated-input-latency"].displayValue // "N/A"')
            local tbt=$(echo "$response" | jq -r '.lighthouseResult.audits["total-blocking-time"].displayValue // "N/A"')
            
            echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "   📊 Performance Score: $score/100"
            echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "   🚀 Core Web Vitals:"
            echo "      • Largest Contentful Paint: $lcp"
            echo "      • First Input Delay: $fid"
            echo "      • Cumulative Layout Shift: $cls"
            echo ""
            echo "   ⚡ Loading Metrics:"
            echo "      • First Contentful Paint: $fcp"
            echo "      • First Meaningful Paint: $fmp"
            echo "      • Speed Index: $si"
            echo ""
            echo "   🎯 Interactivity Metrics:"
            echo "      • Time To Interactive: $tti"
            echo "      • First CPU Idle: $fci"
            echo "      • Estimated Input Latency: $eil"
            echo "      • Total Blocking Time: $tbt"
            
            # Сохранение результатов в переменные
            if [ "$strategy" = "mobile" ]; then
                MOBILE_SCORE="$score"
                MOBILE_LCP="$lcp"
                MOBILE_FID="$fid"
                MOBILE_CLS="$cls"
                MOBILE_FCP="$fcp"
                MOBILE_SI="$si"
                MOBILE_TTI="$tti"
                MOBILE_FMP="$fmp"
                MOBILE_FCI="$fci"
                MOBILE_EIL="$eil"
                MOBILE_TBT="$tbt"
            else
                DESKTOP_SCORE="$score"
                DESKTOP_LCP="$lcp"
                DESKTOP_FID="$fid"
                DESKTOP_CLS="$cls"
                DESKTOP_FCP="$fcp"
                DESKTOP_SI="$si"
                DESKTOP_TTI="$tti"
                DESKTOP_FMP="$fmp"
                DESKTOP_FCI="$fci"
                DESKTOP_EIL="$eil"
                DESKTOP_TBT="$tbt"
            fi
        else
            echo "   ❌ Нет данных Lighthouse в ответе API"
        fi
    else
        echo "   ✅ Запрос выполнен (установите jq для детального анализа)"
    fi
    
    echo ""
}

# Функция сохранения результатов
save_results() {
    # Создаем детальную запись с все метриками
    local entry="[$TIMESTAMP] URL: $URL | HTTP: $HTTP_STATUS (${RESPONSE_TIME}s)
Mobile Score: $MOBILE_SCORE/100
  Core Web Vitals: LCP=$MOBILE_LCP, FID=$MOBILE_FID, CLS=$MOBILE_CLS
  Loading: FCP=$MOBILE_FCP, FMP=$MOBILE_FMP, SI=$MOBILE_SI
  Interactivity: TTI=$MOBILE_TTI, FCI=$MOBILE_FCI, EIL=$MOBILE_EIL, TBT=$MOBILE_TBT
Desktop Score: $DESKTOP_SCORE/100
  Core Web Vitals: LCP=$DESKTOP_LCP, FID=$DESKTOP_FID, CLS=$DESKTOP_CLS
  Loading: FCP=$DESKTOP_FCP, FMP=$DESKTOP_FMP, SI=$DESKTOP_SI
  Interactivity: TTI=$DESKTOP_TTI, FCI=$DESKTOP_FCI, EIL=$DESKTOP_EIL, TBT=$DESKTOP_TBT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Создаем временный файл с новой записью наверху
    echo "$entry" > "$TEMP_FILE"
    
    # Добавляем существующие записи если файл истории существует
    if [ -f "$HISTORY_FILE" ]; then
        cat "$HISTORY_FILE" >> "$TEMP_FILE"
    fi
    
    # Заменяем файл истории
    mv "$TEMP_FILE" "$HISTORY_FILE"
    
    echo "💾 Результаты сохранены в $HISTORY_FILE"
}

# Функция сравнения с предыдущими результатами
compare_with_previous() {
    if [ ! -f "$HISTORY_FILE" ]; then
        echo "📈 Недостаточно данных для сравнения (нет файла истории)"
        return
    fi
    
    # Подсчитываем количество записей (каждая запись занимает 8 строк + разделитель)
    local total_lines=$(wc -l < "$HISTORY_FILE")
    if [ "$total_lines" -lt 18 ]; then  # Минимум 2 записи (9 строк каждая)
        echo "📈 Недостаточно данных для сравнения (нужно минимум 2 измерения)"
        return
    fi
    
    echo "📊 Сравнение с предыдущим измерением:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Извлекаем предыдущие результаты (начинаем с строки 10 - вторая запись)
    local prev_mobile=$(sed -n '11p' "$HISTORY_FILE" | sed -n 's/Mobile Score: \([0-9.]*\).*/\1/p')
    local prev_desktop=$(sed -n '15p' "$HISTORY_FILE" | sed -n 's/Desktop Score: \([0-9.]*\).*/\1/p')
    
    if [[ "$MOBILE_SCORE" =~ ^[0-9.]+$ ]] && [[ "$prev_mobile" =~ ^[0-9.]+$ ]]; then
        local mobile_diff=$(echo "$MOBILE_SCORE - $prev_mobile" | bc)
        local mobile_change=""
        if (( $(echo "$mobile_diff > 0" | bc -l) )); then
            mobile_change="📈 +$mobile_diff"
        elif (( $(echo "$mobile_diff < 0" | bc -l) )); then
            mobile_change="📉 $mobile_diff"
        else
            mobile_change="➡️ без изменений"
        fi
        echo "   Mobile Score: $MOBILE_SCORE (было: $prev_mobile) $mobile_change"
    fi
    
    if [[ "$DESKTOP_SCORE" =~ ^[0-9.]+$ ]] && [[ "$prev_desktop" =~ ^[0-9.]+$ ]]; then
        local desktop_diff=$(echo "$DESKTOP_SCORE - $prev_desktop" | bc)
        local desktop_change=""
        if (( $(echo "$desktop_diff > 0" | bc -l) )); then
            desktop_change="📈 +$desktop_diff"
        elif (( $(echo "$desktop_diff < 0" | bc -l) )); then
            desktop_change="📉 $desktop_diff"
        else
            desktop_change="➡️ без изменений"
        fi
        echo "   Desktop Score: $DESKTOP_SCORE (было: $prev_desktop) $desktop_change"
    fi
    
    echo ""
}

# Проверка мобильной версии
check_pagespeed "mobile" "📱"

# Проверка десктопной версии  
check_pagespeed "desktop" "🖥️"

# Быстрая проверка доступности
echo "🌐 Проверка доступности..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" "$URL")

if [[ "$HTTP_STATUS" =~ ^(200|301|302)$ ]]; then
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "   ✅ Сайт доступен (HTTP $HTTP_STATUS)"
    else
        echo "   ✅ Сайт доступен с редиректом (HTTP $HTTP_STATUS)"
    fi
    echo "   ⏱️  Время ответа: ${RESPONSE_TIME}s"
else
    echo "   ❌ Сайт недоступен (HTTP $HTTP_STATUS)"
fi

echo ""

# Сохранение результатов
save_results

# Сравнение с предыдущими результатами
compare_with_previous

# Показ последних результатов
echo "📝 Последние 3 измерения:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "$HISTORY_FILE" ]; then
    # Каждая запись занимает 9 строк (включая разделитель), показываем первые 3 записи
    head -27 "$HISTORY_FILE" | while IFS= read -r line; do
        echo "   $line"
    done
else
    echo "   Нет данных в истории"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Проверка завершена!"
echo ""
echo "💡 Для более детального анализа:"
echo "   • Chrome DevTools: F12 → Lighthouse"
echo "   • PageSpeed Insights: https://pagespeed.web.dev/"
echo "   • WebPageTest: https://webpagetest.org/"
echo ""
echo "🔑 Для частого использования рекомендуется получить API ключ:"
echo "   • Google PageSpeed API: https://developers.google.com/speed/docs/insights/v5/get-started"
echo "   • Без ключа: ограниченное количество запросов в день"
echo "   • С ключом: до 25,000 запросов в день бесплатно"
echo ""
echo "📊 Использование скрипта:"
echo "   • Текущий тест: ./scripts/performance-check.sh"
echo "   • История: ./scripts/performance-check.sh --history"
echo "   • Другой URL: ./scripts/performance-check.sh https://example.com"
echo "   • С API ключом: ./scripts/performance-check.sh --api-key YOUR_KEY"
echo "   • Переменная окружения: export PAGESPEED_API_KEY=YOUR_KEY"
echo ""
echo "📈 Файлы результатов:"
echo "   • История: $HISTORY_FILE"
echo "   • Документация: Обновите PERFORMANCE_METRICS.md с новыми данными" 