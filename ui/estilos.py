"""Sistema de diseño de la app: colores, tipografía, iconos y componentes HTML.

Para cambiar la identidad visual:
  - Colores de la interfaz  -> variables CSS de abajo (bloque :root) y .streamlit/config.toml
  - Colores de los gráficos -> ui/graficos.py
"""

from html import escape
from urllib.parse import quote

import streamlit as st

# Colores usados también desde Python (insignias de prioridad y gráficos).
AZUL = "#2a78d6"
PRIORIDAD_COLOR = {"A": "#0d366b", "B": "#256abf", "C": "#86b6ef"}   # una sola familia, de oscuro a claro
PRIORIDAD_TEXTO = {"A": "#ffffff", "B": "#ffffff", "C": "#0d366b"}

CSS = """
<style>
:root{
  --tm-navy:#0c2444; --tm-blue-700:#0d366b; --tm-blue-600:#184f95; --tm-blue-500:#256abf;
  --tm-blue:#2a78d6; --tm-blue-250:#86b6ef; --tm-blue-100:#cde2fb; --tm-blue-50:#edf4fd;
  --tm-accent:#eb6834;
  --tm-ink:#0f1b2d; --tm-ink2:#48566a; --tm-muted:#66758a;
  --tm-line:#e3e7ee; --tm-page:#f4f6fa; --tm-card:#ffffff;
  --tm-good:#006300; --tm-good-dot:#0ca30c; --tm-good-bg:#e7f6e7; --tm-crit:#b93232; --tm-crit-bg:#fbeaea;
  --tm-shadow:0 1px 2px rgba(15,27,45,.04), 0 10px 28px -18px rgba(15,27,45,.18);
}

/* ---------- estructura general ---------- */
[data-testid="stMainBlockContainer"]{max-width:1240px;padding:1.6rem 2.2rem 7rem;}
[data-testid="stHeader"]{background:transparent;}
h1,h2,h3{letter-spacing:-.01em;}

/* tarjetas: cualquier st.container(key="card_...") */
[class*="st-key-card_"]{background:var(--tm-card);border:1px solid var(--tm-line);border-radius:16px;
  padding:20px 22px 22px;box-shadow:var(--tm-shadow);}
[data-testid="stColumn"] > [data-testid="stVerticalBlock"]:has(> [data-testid="stLayoutWrapper"]:only-child > [class*="st-key-card_"]){height:100%;}
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:only-child:has(> [class*="st-key-card_"]){flex:1 1 auto;}
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:only-child > [class*="st-key-card_"]{flex:1 1 auto;}
.tm-card-t{font-size:15px;font-weight:650;color:var(--tm-ink);margin:0 0 2px;display:flex;align-items:center;gap:8px;}
.tm-card-t .tm-i{color:var(--tm-blue-500);}
.tm-card-s{font-size:12.5px;color:var(--tm-muted);margin:0;}

/* ---------- encabezado de página ---------- */
.tm-head{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;margin:0 0 6px;flex-wrap:wrap;}
.tm-eyebrow{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--tm-blue-500);margin-bottom:4px;}
.tm-head h1{font-size:28px;line-height:1.15;font-weight:700;color:var(--tm-ink);margin:0;padding:0;}
.tm-head-r{display:flex;gap:8px;align-items:center;flex-wrap:wrap;}

/* ---------- chips e insignias ---------- */
.tm-chip{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;background:#fff;
  border:1px solid var(--tm-line);font-size:12.5px;font-weight:500;color:var(--tm-ink2);white-space:nowrap;}
.tm-chip .tm-i{color:var(--tm-muted);}
.tm-chip.soft{background:var(--tm-blue-50);border-color:transparent;color:var(--tm-blue-600);}
.tm-chip.soft .tm-i{color:var(--tm-blue-500);}
.tm-pri{display:inline-flex;align-items:center;justify-content:center;min-width:26px;height:26px;padding:0 7px;
  border-radius:8px;font-size:13px;font-weight:700;}
.tm-pri.lg{min-width:34px;height:34px;font-size:16px;border-radius:10px;}
.tm-estado{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;font-size:12.5px;
  font-weight:600;background:#f1f4f8;color:var(--tm-ink2);white-space:nowrap;}
.tm-estado i{width:8px;height:8px;border-radius:50%;background:#9aa7b8;display:inline-block;}
.tm-estado.activo{background:var(--tm-blue-50);color:var(--tm-blue-600);} .tm-estado.activo i{background:var(--tm-blue);}
.tm-estado.bien{background:var(--tm-good-bg);color:var(--tm-good);} .tm-estado.bien i{background:var(--tm-good-dot);}
.tm-estado.fuera{background:var(--tm-crit-bg);color:var(--tm-crit);} .tm-estado.fuera i{background:var(--tm-crit);}

/* ---------- indicadores (KPI) ---------- */
.tm-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin:6px 0 4px;}
.tm-kpi{background:var(--tm-card);border:1px solid var(--tm-line);border-radius:16px;padding:16px 18px;box-shadow:var(--tm-shadow);}
.tm-kpi-top{display:flex;align-items:center;gap:10px;margin-bottom:10px;}
.tm-kpi-ico{width:34px;height:34px;border-radius:10px;background:var(--tm-blue-50);color:var(--tm-blue-500);
  display:flex;align-items:center;justify-content:center;flex:none;}
.tm-kpi-lab{font-size:12.5px;font-weight:500;color:var(--tm-ink2);line-height:1.25;}
.tm-kpi-val{font-size:30px;font-weight:650;color:var(--tm-ink);line-height:1.05;letter-spacing:-.02em;}
.tm-kpi-sub{font-size:12px;color:var(--tm-muted);margin-top:6px;min-height:16px;}

/* ---------- medidores y listas ---------- */
.tm-meter{height:8px;border-radius:999px;background:var(--tm-blue-100);overflow:hidden;}
.tm-meter span{display:block;height:100%;border-radius:999px;background:var(--tm-blue);}
.tm-rows{display:flex;flex-direction:column;}
.tm-row{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(90px,1fr) 46px;gap:14px;align-items:center;
  padding:11px 0;border-top:1px solid var(--tm-line);}
.tm-row:first-child{border-top:none;}
.tm-row-n{font-size:13.5px;font-weight:600;color:var(--tm-ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tm-row-d{font-size:12px;color:var(--tm-muted);}
.tm-row-v{font-size:13.5px;font-weight:650;color:var(--tm-ink);text-align:right;font-variant-numeric:tabular-nums;}
.tm-item{display:flex;align-items:center;gap:12px;padding:10px 0;border-top:1px solid var(--tm-line);}
.tm-item:first-child{border-top:none;}
.tm-item-b{flex:1;min-width:0;}

/* puntaje del prospecto */
.tm-score{display:flex;align-items:baseline;gap:6px;margin:4px 0 10px;}
.tm-score b{font-size:48px;font-weight:650;letter-spacing:-.03em;color:var(--tm-ink);line-height:1;}
.tm-score span{font-size:15px;color:var(--tm-muted);font-weight:500;}
.tm-name{font-size:19px;font-weight:700;color:var(--tm-ink);line-height:1.25;margin:0 0 8px;}
.tm-chips{display:flex;flex-wrap:wrap;gap:6px;}
.tm-kv{display:flex;align-items:center;gap:8px;font-size:13.5px;color:var(--tm-ink2);padding:3px 0;word-break:break-word;}
.tm-kv .tm-i{color:var(--tm-muted);flex:none;}
.tm-crit{padding:10px 0;border-top:1px solid var(--tm-line);}
.tm-crit:first-child{border-top:none;padding-top:2px;}
.tm-crit-top{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin-bottom:6px;}
.tm-crit-n{font-size:13.5px;font-weight:600;color:var(--tm-ink);}
.tm-crit-n small{font-weight:500;color:var(--tm-muted);font-size:12px;margin-left:6px;}
.tm-crit-v{font-size:13px;font-weight:650;color:var(--tm-ink);font-variant-numeric:tabular-nums;white-space:nowrap;}
.tm-crit-v small{font-weight:500;color:var(--tm-muted);}
.tm-crit-r{font-size:12.5px;color:var(--tm-muted);margin-top:6px;}
.tm-note{background:var(--tm-blue-50);border-radius:12px;padding:12px 14px;font-size:13.5px;color:var(--tm-ink2);line-height:1.5;}
.tm-note b{color:var(--tm-ink);}

/* ---------- etapas del contacto ---------- */
.tm-steps{display:flex;align-items:flex-start;margin:6px 0 2px;}
.tm-step{flex:1;text-align:center;position:relative;font-size:12px;color:var(--tm-muted);font-weight:500;}
.tm-step::before{content:"";position:absolute;top:13px;left:-50%;width:100%;height:2px;background:var(--tm-line);}
.tm-step:first-child::before{display:none;}
.tm-step .dot{position:relative;z-index:1;width:28px;height:28px;border-radius:50%;margin:0 auto 6px;background:#fff;
  border:2px solid var(--tm-line);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:var(--tm-muted);}
.tm-step.hecho::before,.tm-step.actual::before{background:var(--tm-blue);}
.tm-step.hecho .dot{background:var(--tm-blue);border-color:var(--tm-blue);color:#fff;}
.tm-step.actual .dot{border-color:var(--tm-blue);color:var(--tm-blue-600);box-shadow:0 0 0 4px var(--tm-blue-50);}
.tm-step.actual,.tm-step.hecho{color:var(--tm-ink);font-weight:600;}

/* ---------- línea de tiempo ---------- */
.tm-time{position:relative;padding-left:22px;}
.tm-time::before{content:"";position:absolute;left:6px;top:6px;bottom:6px;width:2px;background:var(--tm-line);}
.tm-ev{position:relative;padding:0 0 16px;}
.tm-ev::before{content:"";position:absolute;left:-21px;top:4px;width:10px;height:10px;border-radius:50%;background:#fff;border:2px solid var(--tm-blue);}
.tm-ev-t{font-size:13.5px;font-weight:600;color:var(--tm-ink);}
.tm-ev-d{font-size:12.5px;color:var(--tm-ink2);margin-top:2px;}
.tm-ev-f{font-size:11.5px;color:var(--tm-muted);margin-top:2px;}

/* ---------- estado vacío ---------- */
.tm-empty{text-align:center;padding:44px 20px 8px;}
.tm-empty-ico{width:64px;height:64px;border-radius:20px;background:var(--tm-blue-50);color:var(--tm-blue-500);
  display:flex;align-items:center;justify-content:center;margin:0 auto 16px;}
.tm-empty-t{font-size:18px;font-weight:650;color:var(--tm-ink);}
.tm-empty-s{font-size:14px;color:var(--tm-muted);margin-top:4px;}

/* ---------- controles nativos ---------- */
.stButton button,.stDownloadButton button,.stLinkButton a,[data-testid="stFormSubmitButton"] button{
  font-weight:600;border-radius:10px;transition:box-shadow .15s, transform .15s, background .15s;}
.stButton button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"]{
  box-shadow:0 6px 16px -8px rgba(42,120,214,.75);}
.stButton button[kind="primary"]:hover{transform:translateY(-1px);}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:4px;border-bottom:1px solid var(--tm-line);}
[data-testid="stTabs"] [data-baseweb="tab"]{padding:8px 14px;border-radius:10px 10px 0 0;font-weight:600;}
[data-testid="stExpander"] details{background:#fff;border-radius:14px;border-color:var(--tm-line);}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden;}
[data-testid="stAlertContainer"]{border-radius:12px;}

[data-testid="stMain"] [data-testid="stPageLink"] a{background:#fff;border:1px solid var(--tm-line);border-radius:10px;
  padding:8px 14px;justify-content:center;transition:border-color .15s, background .15s;}
[data-testid="stMain"] [data-testid="stPageLink"] a:hover{border-color:var(--tm-blue);background:var(--tm-blue-50);}
[data-testid="stMain"] [data-testid="stPageLink"] a p{font-weight:600;color:var(--tm-blue-600);}
[data-testid="stMain"] [data-testid="stPageLink"] a [data-testid="stIconMaterial"]{color:var(--tm-blue-500);}

/* ---------- barra lateral ---------- */
[data-testid="stSidebar"]{border-right:none;}
[data-testid="stSidebarUserContent"]{padding-top:.4rem;}
.tm-brand{display:flex;align-items:center;gap:12px;padding:2px 2px 18px;}
.tm-brand-m{width:42px;height:42px;border-radius:13px;background:linear-gradient(135deg,#3987e5,#184f95);
  display:flex;align-items:center;justify-content:center;color:#fff;box-shadow:0 8px 18px -8px rgba(57,135,229,.9);flex:none;}
.tm-brand-n{font-size:17px;font-weight:700;color:#fff;line-height:1.1;letter-spacing:-.01em;}
.tm-brand-s{font-size:12px;color:#9fb4d3;margin-top:3px;}
.tm-side-l{font-size:11px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:#8ba3c7;margin:14px 4px 4px;}
[data-testid="stSidebar"] [data-testid="stPageLink"] a{border-radius:11px;padding:9px 12px;gap:11px;color:#c9d6ea;
  transition:background .15s,color .15s;}
[data-testid="stSidebar"] [data-testid="stPageLink"] a p{font-size:14.5px;font-weight:500;color:#c9d6ea;}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover p{color:#fff;}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover{background:rgba(255,255,255,.07);color:#fff;}
.st-key-nav_activo [data-testid="stPageLink"] a,.st-key-nav_activo [data-testid="stPageLink"] a:hover{background:#fff;
  color:var(--tm-navy);box-shadow:0 8px 20px -10px rgba(0,0,0,.55);}
.st-key-nav_activo [data-testid="stPageLink"] a p,.st-key-nav_activo [data-testid="stPageLink"] a:hover p{font-weight:650;color:var(--tm-navy);}
[data-testid="stSidebar"] [data-testid="stPageLink"] a [data-testid="stIconMaterial"]{color:#9fb4d3;}
.st-key-nav_activo [data-testid="stPageLink"] a [data-testid="stIconMaterial"]{color:var(--tm-blue);}
.tm-ia{display:flex;align-items:center;gap:10px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.09);
  border-radius:12px;padding:10px 12px;margin-top:6px;}
.tm-ia i{width:9px;height:9px;border-radius:50%;flex:none;background:#7f8ea6;}
.tm-ia.on i{background:#3ddc84;box-shadow:0 0 0 4px rgba(61,220,132,.18);}
.tm-ia-t{font-size:13px;font-weight:600;color:#fff;line-height:1.2;}
.tm-ia-s{font-size:11.5px;color:#9fb4d3;}

/* ---------- asistente flotante ---------- */
[class*="st-key-tmfab_"]{position:fixed;right:28px;bottom:26px;z-index:1000001;width:auto !important;}
[class*="st-key-tmfab_"] button{width:62px;height:62px;min-height:62px;border-radius:50%;border:none;padding:0;color:#fff;
  background:linear-gradient(135deg,#f08a4b,#eb6834 55%,#d4521f);box-shadow:0 14px 30px -8px rgba(235,104,52,.65);
  transition:transform .15s, box-shadow .15s;}
[class*="st-key-tmfab_"] button:hover{transform:translateY(-2px) scale(1.04);color:#fff;border:none;
  box-shadow:0 18px 34px -8px rgba(235,104,52,.75);}
[class*="st-key-tmfab_"] button:active,[class*="st-key-tmfab_"] button:focus{color:#fff;border:none;}
[class*="st-key-tmfab_"] button [data-testid="stIconMaterial"]{font-size:28px;color:#fff;}
.st-key-tmfab_abierto button{background:linear-gradient(135deg,#184f95,#0c2444);box-shadow:0 14px 30px -8px rgba(12,36,68,.6);}
.st-key-tmfab_abierto button:hover{box-shadow:0 18px 34px -8px rgba(12,36,68,.7);}

@keyframes tm-pop{from{opacity:0;transform:translateY(10px) scale(.98);}to{opacity:1;transform:none;}}
.st-key-tm_chat{position:fixed;right:28px;bottom:102px;width:410px;max-width:calc(100vw - 32px);
  max-height:calc(100vh - 122px);background:#fff;border:1px solid var(--tm-line);border-radius:20px;overflow:hidden;
  box-shadow:0 28px 70px -14px rgba(12,36,68,.42);z-index:1000000;gap:0 !important;animation:tm-pop .18s ease-out;}
.st-key-tm_chat_head{background:linear-gradient(135deg,#0c2444,#184f95);padding:14px 12px 14px 16px;}
.tm-chat-h{display:flex;align-items:center;gap:11px;}
.tm-chat-a{width:38px;height:38px;border-radius:12px;background:rgba(255,255,255,.14);color:#fff;display:flex;
  align-items:center;justify-content:center;flex:none;}
.tm-chat-n{font-size:15px;font-weight:650;color:#fff;line-height:1.2;}
.tm-chat-s{font-size:12px;color:#b9cbe6;display:flex;align-items:center;gap:6px;}
.tm-chat-s i{width:7px;height:7px;border-radius:50%;background:#7f8ea6;display:inline-block;}
.tm-chat-s.on i{background:#3ddc84;}
.st-key-tm_chat_head button{background:transparent;border:none;color:#dbe6f6;min-height:34px;width:34px;padding:0;}
.st-key-tm_chat_head button:hover{background:rgba(255,255,255,.14);color:#fff;border:none;}
.st-key-tm_chat_ctx{padding:10px 14px 4px;}
.st-key-tm_chat_body{padding:4px 14px 0;}
.st-key-tm_chat_body > [data-testid="stLayoutWrapper"],
.st-key-tm_chat_body > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]{
  height:clamp(190px, calc(100vh - 340px), 370px) !important;}
.st-key-tm_chat_in{padding:8px 14px 14px;}
.st-key-tm_chat [data-stale="true"],.st-key-asistente_boton[data-stale="true"]{opacity:1 !important;}
.st-key-tm_chat [data-testid="stChatMessage"]{padding:10px 12px;border-radius:14px;gap:10px;background:#f4f6fa;font-size:14px;}
.st-key-tm_chat [data-testid="stChatMessage"] p,.st-key-tm_chat [data-testid="stChatMessage"] li{font-size:14px;line-height:1.5;}
.st-key-tm_chat [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]){background:var(--tm-blue-50);}
.st-key-tm_chat [data-testid^="stChatMessageAvatar"]{width:30px;height:30px;border-radius:10px;background:#fff;
  border:1px solid var(--tm-line);color:var(--tm-blue-500);}
.st-key-tm_chat [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) [data-testid^="stChatMessageAvatar"]{
  background:var(--tm-blue);border-color:var(--tm-blue);color:#fff;}
.st-key-tm_chat_sug{gap:8px !important;}
.tm-chat-hi{font-size:14px;color:var(--tm-ink2);line-height:1.5;background:#f4f6fa;border-radius:14px;padding:12px 14px;margin-bottom:4px;}
.tm-chat-hi b{color:var(--tm-ink);}
.st-key-tm_chat_sug button{justify-content:flex-start;text-align:left;font-weight:500;font-size:13.5px;
  border-radius:12px;border-color:var(--tm-line);color:var(--tm-ink);min-height:38px;padding:6px 12px;}
.st-key-tm_chat_sug button:hover{border-color:var(--tm-blue);color:var(--tm-blue-600);background:var(--tm-blue-50);}
.st-key-tm_chat_sug button [data-testid="stIconMaterial"]{color:var(--tm-accent);}
.tm-dots{display:inline-flex;gap:5px;padding:6px 2px;}
.tm-dots i{width:7px;height:7px;border-radius:50%;background:#9aa7b8;animation:tm-b 1.1s infinite ease-in-out;}
.tm-dots i:nth-child(2){animation-delay:.15s;} .tm-dots i:nth-child(3){animation-delay:.3s;}
@keyframes tm-b{0%,80%,100%{opacity:.3;transform:translateY(0);}40%{opacity:1;transform:translateY(-3px);}}
@media (prefers-reduced-motion: reduce){.tm-dots i,.st-key-tm_chat{animation:none;}}
</style>
"""

# Trazos de los iconos (basados en Feather Icons, licencia MIT).
_ICONOS = {
    "empresa": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M9 21v-4h6v4"/><path d="M8 7h.01M12 7h.01M16 7h.01M8 11h.01M12 11h.01M16 11h.01"/>',
    "estrella": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "enviar": '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
    "mensaje": '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>',
    "calendario": '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "check": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "correo": '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
    "telefono": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "camion": '<rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>',
    "objetivo": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "usuario": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "usuarios": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "reloj": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "web": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "bandeja": '<polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>',
    "tendencia": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "capas": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "embudo": '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    "barras": '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    "lista": '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>',
    "ok": '<polyline points="20 6 9 17 4 12"/>',
    "x": '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    "ruta": '<circle cx="6" cy="19" r="2.5"/><circle cx="18" cy="5" r="2.5"/><path d="M6 16.5V13a3 3 0 0 1 3-3h6a3 3 0 0 0 3-3v0"/>',
    "robot": '<rect x="4" y="8" width="16" height="12" rx="3"/><path d="M12 8V5"/><circle cx="12" cy="3.5" r="1.5"/><path d="M9 13v2M15 13v2M2 13v3M22 13v3"/>',
    "cronometro": '<circle cx="12" cy="13" r="8"/><polyline points="12 9 12 13 14.5 15"/><path d="M9 2h6M12 2v3"/>',
}


def _css_iconos():
    """Los iconos se dibujan como máscaras CSS (SVG embebido): toman el color del texto y no usan internet."""
    reglas = [".tm-i{display:inline-block;flex:none;background-color:currentColor;vertical-align:-3px;"
              "-webkit-mask:center/contain no-repeat;mask:center/contain no-repeat;}"]
    for nombre, trazos in _ICONOS.items():
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" '
               f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{trazos}</svg>')
        uri = "data:image/svg+xml," + quote(svg, safe="")
        reglas.append(f'.tm-i-{nombre}{{-webkit-mask-image:url("{uri}");mask-image:url("{uri}");}}')
    return "<style>" + "".join(reglas) + "</style>"


def icono(nombre, tam=18):
    return f'<span class="tm-i tm-i-{nombre}" style="width:{tam}px;height:{tam}px" aria-hidden="true"></span>'


def aplicar():
    """Inyecta la hoja de estilos. Se llama una vez por ejecución desde app.py."""
    st.html(CSS)
    st.html(_css_iconos())


def e(texto):
    """Escapa texto de usuario antes de ponerlo dentro de HTML."""
    return escape(str(texto if texto is not None else ""))


# --------------------------------------------------------------------------- componentes

def encabezado(titulo, derecha=""):
    st.html(f'<div class="tm-head"><div><div class="tm-eyebrow">Transmillas · Prospección B2B</div>'
            f'<h1>{e(titulo)}</h1></div><div class="tm-head-r">{derecha}</div></div>')


def titulo_tarjeta(titulo, ico=None, sub=None):
    marca = icono(ico, 17) if ico else ""
    extra = f'<p class="tm-card-s">{e(sub)}</p>' if sub else ""
    st.html(f'<div class="tm-card-t">{marca}{e(titulo)}</div>{extra}')


def chip(texto, ico=None, suave=False):
    marca = icono(ico, 14) if ico else ""
    return f'<span class="tm-chip{" soft" if suave else ""}">{marca}{e(texto)}</span>'


def prioridad(p, grande=False):
    if p not in PRIORIDAD_COLOR:
        return '<span class="tm-pri" style="background:#eef1f5;color:#66758a">–</span>'
    return (f'<span class="tm-pri{" lg" if grande else ""}" style="background:{PRIORIDAD_COLOR[p]};'
            f'color:{PRIORIDAD_TEXTO[p]}" title="Prioridad {p}">{p}</span>')


def estado(nombre):
    if nombre == "Cliente":
        clase = "bien"
    elif nombre == "Descartado":
        clase = "fuera"
    elif nombre in ("Nuevo", "Aprobado para contacto"):
        clase = ""
    else:
        clase = "activo"
    return f'<span class="tm-estado {clase}"><i></i>{e(nombre)}</span>'


def kpis(tarjetas):
    """tarjetas: lista de (icono, etiqueta, valor, nota)."""
    partes = []
    for ico, etiqueta, valor, nota in tarjetas:
        partes.append(
            f'<div class="tm-kpi"><div class="tm-kpi-top"><div class="tm-kpi-ico">{icono(ico, 18)}</div>'
            f'<div class="tm-kpi-lab">{e(etiqueta)}</div></div><div class="tm-kpi-val">{e(valor)}</div>'
            f'<div class="tm-kpi-sub">{e(nota or "")}</div></div>')
    st.html(f'<div class="tm-kpis">{"".join(partes)}</div>')


def medidor(valor, maximo=100):
    ancho = 0 if not maximo else max(0, min(100, 100 * float(valor) / float(maximo)))
    return f'<div class="tm-meter" role="img" aria-label="{valor} de {maximo}"><span style="width:{ancho:.1f}%"></span></div>'


def vacio(ico, titulo, texto=""):
    st.html(f'<div class="tm-empty"><div class="tm-empty-ico">{icono(ico, 28)}</div>'
            f'<div class="tm-empty-t">{e(titulo)}</div><div class="tm-empty-s">{e(texto)}</div></div>')


def marca():
    st.html(f'<div class="tm-brand"><div class="tm-brand-m">{icono("ruta", 22)}</div><div>'
            f'<div class="tm-brand-n">Transmillas</div><div class="tm-brand-s">Prospección B2B</div></div></div>')


def etiqueta_lateral(texto):
    st.html(f'<div class="tm-side-l">{e(texto)}</div>')


def estado_ia(activa, modelo):
    if activa:
        st.html(f'<div class="tm-ia on"><i></i><div><div class="tm-ia-t">IA local activa</div>'
                f'<div class="tm-ia-s">{e(modelo)}</div></div></div>')
    else:
        st.html('<div class="tm-ia"><i></i><div><div class="tm-ia-t">IA local inactiva</div>'
                '<div class="tm-ia-s">Reglas y plantillas</div></div></div>')
