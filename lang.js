document.addEventListener('DOMContentLoaded', () => {
  const selectedLanguage = localStorage.getItem('selectedLanguage') || 'en';

  // Function to translate elements with data-i18n attribute
  function translatePage() {
    // Update page title if translation exists
    if (translations[selectedLanguage] && translations[selectedLanguage].page_title) {
      document.title = translations[selectedLanguage].page_title;
    }

    // Translate all elements with data-i18n attribute
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (translations[selectedLanguage] && translations[selectedLanguage][key]) {
        el.textContent = translations[selectedLanguage][key];
      }
    });

    // Update nav links text if translations exist
    const navKeys = [
      'nav_home', 'nav_market_prices', 'nav_find_buyers', 'nav_how_it_works',
      'nav_language_selector', 'nav_download_app', 'nav_about_us', 'nav_contact', 'nav_privacy_policy'
    ];
    navKeys.forEach(key => {
      const navEl = document.querySelector(`[data-i18n="${key}"]`);
      if (navEl && translations[selectedLanguage] && translations[selectedLanguage][key]) {
        navEl.textContent = translations[selectedLanguage][key];
      }
    });
  }

  translatePage();
});
