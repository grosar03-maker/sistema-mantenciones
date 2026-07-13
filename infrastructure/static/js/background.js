var BG_DEFAULT = 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1920&q=80';

function aplicarBg(url) {
    var main = document.getElementById('main-content');
    if (!main) return;
    var isDark = document.documentElement.classList.contains('dark');
    var overlay = isDark
        ? 'linear-gradient(135deg, rgba(15,23,42,0.92) 0%, rgba(30,41,59,0.88) 50%, rgba(15,23,42,0.92) 100%)'
        : 'linear-gradient(135deg, rgba(248,250,252,0.92) 0%, rgba(255,255,255,0.88) 50%, rgba(241,245,249,0.92) 100%)';
    main.style.background = overlay + ', url(' + url + ') center/cover fixed';
    try { localStorage.setItem('bg_url', url); } catch(e) {}
}

function abrirConfig() {
    var modal = document.getElementById('modalConfig');
    if (!modal) return;
    var input = document.getElementById('input-bg-url');
    try { input.value = localStorage.getItem('bg_url') || BG_DEFAULT; } catch(e) { input.value = BG_DEFAULT; }
    modal.classList.remove('hidden');
}

function cerrarConfig() {
    var modal = document.getElementById('modalConfig');
    if (modal) modal.classList.add('hidden');
}

function guardarConfig() {
    var url = document.getElementById('input-bg-url').value.trim();
    if (!url) { alert('Ingresa una URL válida'); return; }
    aplicarBg(url);
    cerrarConfig();
}

function restaurarBg() {
    aplicarBg(BG_DEFAULT);
    cerrarConfig();
}

(function() {
    try {
        var saved = localStorage.getItem('bg_url');
        if (saved) aplicarBg(saved);
    } catch(e) {}
    var obs = new MutationObserver(function() {
        var saved = (function(){ try { return localStorage.getItem('bg_url'); } catch(e) { return null; } })();
        if (saved) aplicarBg(saved);
        else aplicarBg(BG_DEFAULT);
    });
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
})();
