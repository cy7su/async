/**
 * async.pw - Современный JavaScript для Flask сайта
 */

// Современные ES6+ функции
class AsyncPW {
  constructor() {
    this.init();
  }

  init() {
    this.setupNavigation();
    this.setupAnimations();
    this.setupPerformance();
    this.setupAccessibility();
  }

  /**
   * Настройка навигации
   */
  setupNavigation() {
    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", (e) => {
        e.preventDefault();
        const target = document.querySelector(anchor.getAttribute("href"));
        if (target) {
          target.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }
      });
    });

    // Активное состояние для навигации
    const currentPath = window.location.pathname;
    document.querySelectorAll("nav a").forEach((link) => {
      if (link.getAttribute("href") === currentPath) {
        link.classList.add("active");
      }
    });
  }

  /**
   * Настройка анимаций
   */
  setupAnimations() {
    // Intersection Observer для анимаций при скролле
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("animate-in");
            }
          });
        },
        {
          threshold: 0.1,
          rootMargin: "0px 0px -50px 0px",
        },
      );

      // Наблюдаем за карточками
      document
        .querySelectorAll(".language-card, .project-card")
        .forEach((card) => {
          observer.observe(card);
        });
    }
  }

  /**
   * Настройка производительности
   */
  setupPerformance() {
    // Ленивая загрузка изображений
    if ("IntersectionObserver" in window) {
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.classList.remove("lazy");
              observer.unobserve(img);
            }
          }
        });
      });

      document.querySelectorAll("img[data-src]").forEach((img) => {
        imageObserver.observe(img);
      });
    }

    // Preload критических ресурсов
    this.preloadCriticalResources();
  }

  /**
   * Preload критических ресурсов
   */
  preloadCriticalResources() {
    const criticalResources = [
      "/static/css/styles.css",
      "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&display=swap",
    ];

    criticalResources.forEach((resource) => {
      const link = document.createElement("link");
      link.rel = "preload";
      link.href = resource;
      link.as = resource.endsWith(".css") ? "style" : "font";
      if (resource.endsWith(".css")) {
        link.onload = () => (link.rel = "stylesheet");
      }
      document.head.appendChild(link);
    });
  }

  /**
   * Настройка доступности
   */
  setupAccessibility() {
    // Улучшения для скрин-ридеров
    this.setupScreenReaderSupport();

    // Клавиатурная навигация
    this.setupKeyboardNavigation();

    // Уведомления об изменениях
    this.setupLiveRegions();
  }

  /**
   * Поддержка скрин-ридеров
   */
  setupScreenReaderSupport() {
    // Добавляем ARIA-атрибуты для динамического контента
    document
      .querySelectorAll(".language-card, .project-card")
      .forEach((card) => {
        const title = card.querySelector("h2, h3");
        if (title) {
          card.setAttribute("role", "article");
          card.setAttribute(
            "aria-labelledby",
            title.id || this.generateId(title),
          );
        }
      });
  }

  /**
   * Клавиатурная навигация
   */
  setupKeyboardNavigation() {
    document.addEventListener("keydown", (e) => {
      // Escape для закрытия модальных окон
      if (e.key === "Escape") {
        this.closeModals();
      }

      // Enter для активации кнопок
      if (e.key === "Enter" && e.target.classList.contains("btn")) {
        e.target.click();
      }
    });
  }

  /**
   * Live regions для уведомлений
   */
  setupLiveRegions() {
    // Создаем live region для уведомлений
    const liveRegion = document.createElement("div");
    liveRegion.setAttribute("aria-live", "polite");
    liveRegion.setAttribute("aria-atomic", "true");
    liveRegion.className = "sr-only";
    document.body.appendChild(liveRegion);

    this.liveRegion = liveRegion;
  }

  /**
   * Утилиты
   */
  generateId(element) {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    const id = `element-${timestamp}-${random}`;
    element.id = id;
    return id;
  }

  /**
   * Закрытие модальных окон
   */
  closeModals() {
    document.querySelectorAll(".modal, .dropdown").forEach((modal) => {
      modal.classList.remove("active");
    });
  }

  /**
   * Уведомления
   */
  notify(message, type = "info") {
    if (this.liveRegion) {
      this.liveRegion.textContent = message;
    }

    // Визуальное уведомление
    this.showToast(message, type);
  }

  /**
   * Toast уведомления
   */
  showToast(message, type) {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    // Анимация появления
    requestAnimationFrame(() => {
      toast.classList.add("show");
    });

    // Автоматическое скрытие
    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 3000);
  }

  /**
   * API запросы
   */
  async fetchData(url, options = {}) {
    try {
      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Fetch error:", error);
      this.notify("Ошибка загрузки данных", "error");
      throw error;
    }
  }

  /**
   * Кеширование
   */
  cache = new Map();

  getCachedData(key) {
    return this.cache.get(key);
  }

  setCachedData(key, data, ttl = 300000) {
    // 5 минут по умолчанию
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  isCacheValid(key) {
    const cached = this.cache.get(key);
    if (!cached) return false;

    return Date.now() - cached.timestamp < cached.ttl;
  }
}

// Инициализация при загрузке DOM
document.addEventListener("DOMContentLoaded", () => {
  window.asyncPW = new AsyncPW();
});

// Service Worker для кеширования
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/static/js/sw.js")
      .then((registration) => {
        console.log("SW registered: ", registration);
      })
      .catch((registrationError) => {
        console.log("SW registration failed: ", registrationError);
      });
  });
}

// Экспорт для использования в других модулях
// export default AsyncPW;
