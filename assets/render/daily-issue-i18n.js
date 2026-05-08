(function(){
  var LANG_STORAGE = 'lavaagent_home_lang';
  var I18N = {
    zh: {
      nav_back_text: '返回',
      skip_to_content: '跳到正文',
      hero_title: '今日刊',
      hero_tagline: '每日精选',
      hero_count_unit: '条',
      card_read_more: '查看原文',
      card_share: '分享',
      lang_group_label: '界面语言'
    },
    en: {
      nav_back_text: 'Back',
      skip_to_content: 'Skip to content',
      hero_title: 'Today',
      hero_tagline: 'Daily picks',
      hero_count_unit: ' items',
      card_read_more: 'Read more',
      card_share: 'Share',
      lang_group_label: 'Language'
    }
  };
  function getLang(){
    try { var s = localStorage.getItem(LANG_STORAGE); return (s === 'en' || s === 'zh') ? s : 'zh'; }
    catch(_){ return 'zh'; }
  }
  function applyI18n(){
    var lang = getLang();
    var pack = I18N[lang];
    document.querySelectorAll('[data-i18n]').forEach(function(el){
      var k = el.dataset.i18n;
      if (pack[k] !== undefined) el.textContent = pack[k];
    });
    document.querySelectorAll('[data-i18n-text]').forEach(function(el){
      el.hidden = (el.dataset.i18nText !== lang);
    });
    document.documentElement.lang = (lang === 'zh') ? 'zh-CN' : 'en';
    var bZh = document.getElementById('lang-zh');
    var bEn = document.getElementById('lang-en');
    if (bZh) bZh.classList.toggle('active', lang === 'zh');
    if (bEn) bEn.classList.toggle('active', lang === 'en');
    var lg = document.querySelector('.atlas-lang');
    if (lg) lg.setAttribute('aria-label', pack.lang_group_label);
  }
  function setLang(lang){
    if (lang !== 'zh' && lang !== 'en') return;
    try { localStorage.setItem(LANG_STORAGE, lang); } catch(_){}
    applyI18n();
  }
  document.querySelectorAll('[data-set-lang]').forEach(function(el){
    el.addEventListener('click', function(){ setLang(el.dataset.setLang); });
  });
  applyI18n();
})();
