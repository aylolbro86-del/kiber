"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import gsap from "gsap";
import {
  Bot,
  Book,
  ArrowRight,
  Radio,
  Activity,
  ShieldAlert,
  Terminal,
  Cpu,
  X,
  Send,
  Search,
  TrendingUp,
  Users,
  AlertTriangle,
} from "lucide-react";
import axios from "axios";

// ─────────────────────────────────────────────────────────────
//  ТИПЫ ДАННЫХ
// ─────────────────────────────────────────────────────────────
interface AnalysisResult {
  threat_level_ru: string;
  threat_emoji: string;
  explanation: string;
  red_flags: string[];
  recommendations?: string[];
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

// ─────────────────────────────────────────────────────────────
//  КОМПОНЕНТ: СТРОКА СТАТИСТИКИ
// ─────────────────────────────────────────────────────────────
function StatRow({
  label,
  value,
  color,
  pulse = false,
}: {
  label: string;
  value: string;
  color: string;
  pulse?: boolean;
}) {
  return (
    <div className="flex justify-between items-center py-5 border-b border-white/10 group transform-gpu">
      <span className="text-[11px] font-black uppercase tracking-[0.3em] text-zinc-400 group-hover:text-white transition-colors duration-500 mono">
        {label}
      </span>
      <div className="flex items-center gap-3">
        {pulse && (
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_15px_#10b981]" />
        )}
        <span
          className={`text-[12px] font-black uppercase tracking-widest mono ${color}`}
        >
          {value}
        </span>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
//  КОМПОНЕНТ: УЗЕЛ ДОРОЖНОЙ КАРТЫ
//  Исправление #4: классический чередующийся таймлайн.
//  Левый блок: w-1/2 + pr-16 + text-right, точка на right-[-13px].
//  Правый блок: w-1/2 + ml-auto + pl-16 + text-left, точка на left-[-13px].
// ─────────────────────────────────────────────────────────────
function RoadmapNode({
  step,
  title,
  desc,
  status,
  side,
  active,
}: {
  step: string;
  title: string;
  desc: string;
  status: string;
  side: "left" | "right";
  active?: boolean;
}) {
  return (
    <div
      className={`relative mb-28 last:mb-0 group ${
        side === "right"
          ? "w-1/2 ml-auto pl-16 text-left"
          : "w-1/2 pr-16 text-right"
      }`}
    >
      {/* Кружок строго на центральной линии */}
      <div
        className={`absolute top-3 z-10 ${
          side === "right" ? "left-[-13px]" : "right-[-13px]"
        }`}
      >
        <div
          className={`w-[26px] h-[26px] rounded-full border-[3px] border-black transition-all duration-500 ${
            active
              ? "bg-white shadow-[0_0_0_5px_rgba(255,255,255,0.12),0_0_28px_rgba(255,255,255,0.85)]"
              : "bg-zinc-700 border-zinc-900 group-hover:bg-white group-hover:shadow-[0_0_0_4px_rgba(255,255,255,0.08),0_0_18px_rgba(255,255,255,0.6)]"
          }`}
        />
      </div>

      <p
        className={`mono text-[10px] font-black uppercase tracking-[0.5em] mb-3 transition-colors duration-500 ${
          active
            ? "text-emerald-400"
            : "text-zinc-600 group-hover:text-zinc-400"
        }`}
      >
        {step} <span className="text-zinc-700">//</span> {status}
      </p>

      <h4
        className={`font-black italic uppercase leading-none mb-4 tracking-tighter transition-colors duration-500 ${
          active ? "text-white" : "text-zinc-500 group-hover:text-white"
        }`}
        style={{
          fontFamily: "'Unbounded', sans-serif",
          fontSize: "clamp(2rem, 4vw, 5rem)",
        }}
      >
        {title}
      </h4>

      <p className="mono text-[11px] text-zinc-500 font-bold uppercase leading-relaxed tracking-wider group-hover:text-zinc-300 transition-colors duration-500">
        {desc}
      </p>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
//  КОМПОНЕНТ: ЗНАЧОК УГРОЗЫ
// ─────────────────────────────────────────────────────────────
function ThreatBadge({ level }: { level: string }) {
  const map: Record<string, string> = {
    ВЫСОКИЙ:
      "bg-red-600 text-white border-red-400 shadow-[0_0_30px_rgba(239,68,68,0.5)]",
    КРИТИЧЕСКИЙ:
      "bg-red-800 text-white border-red-500 shadow-[0_0_40px_rgba(239,68,68,0.7)]",
    СРЕДНИЙ:
      "bg-amber-500 text-black border-amber-300 shadow-[0_0_30px_rgba(245,158,11,0.4)]",
    НИЗКИЙ:
      "bg-emerald-600 text-white border-emerald-400 shadow-[0_0_30px_rgba(16,185,129,0.4)]",
  };
  const currentStyle =
    map[level.toUpperCase()] || "bg-zinc-700 text-white border-zinc-500";

  return (
    <div
      className={`inline-block px-8 py-3 rounded-full border mono text-[12px] font-black uppercase tracking-[0.2em] ${currentStyle}`}
    >
      {level} риск
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
//  ГЛАВНАЯ СТРАНИЦА
// ─────────────────────────────────────────────────────────────
export default function Home() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysisCount, setAnalysisCount] = useState(3192);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "ЯДРО АКТИВИРОВАНО. Я КИБЕРДРУГ. ЖДУ ВАШИХ ВОПРОСОВ ПО ЦИФРОВОЙ ЗАЩИТЕ И ПРАВУ БЕЛАРУСИ.",
    },
  ]);
  const [chatLoading, setChatLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isChatOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatHistory, isChatOpen]);

  useEffect(() => {
    gsap.ticker.fps(60);
    const tl = gsap.timeline({ defaults: { ease: "expo.out" } });
    tl.from(".reveal-nav", { opacity: 0, y: -30, duration: 1.2, stagger: 0.1 })
      .from(
        ".reveal-hero",
        { opacity: 0, y: 60, duration: 1.5, stagger: 0.15 },
        "-=0.8",
      )
      .from(
        ".reveal-card",
        { opacity: 0, scale: 0.98, duration: 1.2, stagger: 0.1 },
        "-=1",
      );

    gsap.to(".bg-glow-main", {
      opacity: 0.6,
      scale: 1.1,
      duration: 4,
      yoyo: true,
      repeat: -1,
      ease: "sine.inOut",
    });
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!text.trim() || loading) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await axios.post<AnalysisResult>(
        "http://localhost:8000/api/analyze",
        { text },
      );
      setResult(res.data);
      setAnalysisCount((prev) => prev + 1);
      setTimeout(() => {
        gsap.fromTo(
          ".result-card-anim",
          { opacity: 0, y: 50, scale: 0.95 },
          { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: "power4.out" },
        );
      }, 50);
    } catch {
      alert("СБОЙ ЯДРА: Соединение с API потеряно.");
    } finally {
      setLoading(false);
    }
  }, [text, loading]);

  const handleSendMessage = useCallback(async () => {
    if (!chatInput.trim() || chatLoading) return;
    const userMsg: ChatMessage = { role: "user", content: chatInput };
    const updated = [...chatHistory, userMsg];
    setChatHistory(updated);
    setChatInput("");
    setChatLoading(true);
    try {
      const res = await axios.post<{ content: string }>(
        "http://localhost:8000/api/chat",
        { messages: updated },
      );
      setChatHistory([
        ...updated,
        { role: "assistant", content: res.data.content },
      ]);
    } catch {
      setChatHistory([
        ...updated,
        { role: "assistant", content: "ОБРЫВ СВЯЗИ С ЯДРОМ." },
      ]);
    } finally {
      setChatLoading(false);
    }
  }, [chatInput, chatLoading, chatHistory]);

  return (
    <main className="min-h-screen bg-black text-white selection:bg-white selection:text-black antialiased overflow-x-hidden relative font-sans">
      {/* ══════════════════════════════════════════════════════
          ГЛОБАЛЬНЫЕ СТИЛИ
      ══════════════════════════════════════════════════════ */}
      <style jsx global>{`
        @import url("https://fonts.googleapis.com/css2?family=Unbounded:wght@400;900&family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap");

        /* 
           ИСПРАВЛЕНИЕ #1: ГИГАНТСКИЙ ЗАГОЛОВОК (ОТРЯД ЩИТ)
           - Увеличен padding-bottom до 0.25em, чтобы ножки "Д" и "Щ" никогда не резались.
           - Оптимизирован градиент для максимального блеска.
           - Убраны точки в логике (задается в JSX), здесь только визуальный стиль.
        */
        .chrome-text {
          font-family: "Unbounded", sans-serif;
          font-weight: 900;
          text-transform: uppercase;
          font-style: italic;

          /* Многослойный хром-эффект */
          background: linear-gradient(
            180deg,
            #ffffff 0%,
            #ffffff 35%,
            #444444 50%,
            #ffffff 65%,
            #ffffff 100%
          );

          /* Эффект сканирующих полос внутри букв */
          background-image:
            repeating-linear-gradient(
              0deg,
              transparent 0px,
              transparent 2px,
              rgba(0, 0, 0, 0.2) 2px,
              rgba(0, 0, 0, 0.2) 4px
            ),
            linear-gradient(180deg, #ffffff 15%, #666666 50%, #ffffff 85%);

          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;

          display: inline-block;
          line-height: 1.1;

          /* КРИТИЧЕСКИЕ ПРАВКИ ДЛЯ ОБРЕЗКИ */
          padding-bottom: 0.25em; /* Запас для букв Д, Щ */
          padding-right: 0.2em; /* Запас для наклона буквы Т */
          padding-left: 0.1em;
          overflow: visible !important;

          /* Свечение (Bloom) */
          filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.2));
        }

        .mono {
          font-family: "Space Mono", monospace;
        }

        /* 
           ИСПРАВЛЕНИЕ #2: ВИДИМОСТЬ БЛОКОВ (BENTO GRID)
           - Границы теперь всегда видны (opacity 0.2).
           - При наведении текст НЕ пропадает, а становится ярче.
        */
        .cyber-card {
          background: rgba(12, 12, 14, 0.98) !important;
          border: 1px solid rgba(255, 255, 255, 0.2) !important; /* Яркая видимая граница */
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
          border-radius: 4rem;
          transition: all 0.5s cubic-bezier(0.2, 1, 0.3, 1);
          position: relative;
          overflow: hidden;
        }

        .cyber-card:hover {
          border-color: rgba(255, 255, 255, 0.6) !important;
          background: rgba(20, 20, 25, 1) !important;
          transform: translateY(-8px) scale(1.01);
        }

        /* Текст внутри карточек: делаем светлым, чтобы был виден на черном */
        .cyber-card p,
        .cyber-card span {
          color: #a1a1aa !important; /* Светло-серый zinc-400 */
          transition: color 0.4s ease;
        }

        .cyber-card:hover p,
        .cyber-card:hover span {
          color: #ffffff !important; /* Белый при наведении */
        }

        /* 
           ИСПРАВЛЕНИЕ #3: ДОРОЖНАЯ КАРТА (ROADMAP)
           - Создаем класс для центральной линии, которая идет за точками.
        */
        .roadmap-line {
          position: absolute;
          left: 50%;
          top: 0;
          bottom: 0;
          width: 2px;
          background: linear-gradient(
            to bottom,
            transparent,
            rgba(255, 255, 255, 0.1) 10%,
            rgba(255, 255, 255, 0.1) 90%,
            transparent
          );
          transform: translateX(-50%);
          z-index: 1;
        }

        /* Эффект свечения для Roadmap Node */
        .roadmap-glow {
          box-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
          background: white !important;
        }

        /* 
           ИСПРАВЛЕНИЕ #4: БЛОК 77% (ПРОГРЕСС-БАРЫ)
        */
        .threat-bar {
          height: 6px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
          overflow: hidden;
          width: 100%;
          border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .threat-bar-fill {
          height: 100%;
          background: linear-gradient(90deg, #555 0%, #fff 100%);
          box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
          border-radius: 10px;
        }

        /* Скан-линии (Scanlines) */
        .scanlines {
          position: fixed;
          inset: 0;
          background:
            linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.2) 50%),
            linear-gradient(
              90deg,
              rgba(255, 255, 255, 0.02),
              transparent,
              rgba(255, 255, 255, 0.02)
            );
          background-size:
            100% 4px,
            4px 100%;
          z-index: 90;
          pointer-events: none;
          opacity: 0.4;
        }

        /* Футерный текст (уменьшение) */
        .footer-logo {
          font-family: "Unbounded", sans-serif;
          font-size: clamp(3rem, 8vw, 8rem) !important;
          color: #27272a !important;
          transition: color 1s ease;
        }
        .footer-logo:hover {
          color: #ffffff !important;
        }
      `}</style>

      <div className="scanlines" />

      {/* Фоновое свечение */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div
          className="bg-glow-main absolute top-[-15%] left-[-15%] w-[90vw] h-[80vw] rounded-full opacity-22"
          style={{
            background:
              "radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 68%)",
          }}
        />
      </div>

      {/* ══════════════════════════════════════════════════════
          НАВИГАЦИЯ
      ══════════════════════════════════════════════════════ */}
      <nav className="sticky top-0 z-[100] flex justify-between items-center px-8 md:px-16 py-6 border-b border-white/8 bg-black/96 backdrop-blur-xl">
        <div className="reveal-nav w-1/3 flex items-center">
          <div
            className="font-black text-2xl md:text-3xl tracking-tighter italic uppercase"
            style={{ fontFamily: "'Unbounded', sans-serif" }}
          >
            КИБЕРЩИТ
          </div>
        </div>

        <div className="reveal-nav hidden lg:flex absolute left-1/2 -translate-x-1/2 gap-14 mono text-[10px] uppercase tracking-[0.5em] text-zinc-400 font-black">
          <a
            href="#scanner"
            className="hover:text-white transition-colors duration-300"
          >
            Сканнер
          </a>
          <a
            href="#modules"
            className="hover:text-white transition-colors duration-300"
          >
            Модули
          </a>
          <a
            href="#roadmap"
            className="hover:text-white transition-colors duration-300"
          >
            Протокол
          </a>
        </div>

        <div className="reveal-nav w-1/3 flex items-center justify-end gap-6">
          <div className="hidden sm:flex items-center gap-3 mono text-[10px] text-emerald-400 uppercase tracking-widest font-black">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_12px_#10b981]" />
            System_Live
          </div>
          <button className="px-7 py-3 bg-white text-black rounded-full mono text-[10px] uppercase tracking-[0.2em] font-black hover:bg-zinc-200 transition-all duration-300">
            Доступ
          </button>
        </div>
      </nav>

      <div className="max-w-[1500px] mx-auto px-6 md:px-10 relative z-10">
        {/* ══════════════════════════════════════════════════════
            HERO SECTION
            Исправление #1:
            – Слова плотно прижаты: line-height 0.88 + marginTop -0.08em
            – Богатый многоточечный металл с резкими dark-переходами
        ══════════════════════════════════════════════════════ */}
        <section className="pt-28 pb-36 md:pt-44 md:pb-52 text-center flex flex-col items-center relative">
          <div className="reveal-hero inline-flex items-center justify-center px-8 py-3 border border-zinc-700 rounded-full mono text-[10px] uppercase tracking-[0.5em] text-zinc-300 mb-14 bg-white/5">
            #КИБЕРПРАВО // ПРОТОКОЛ_2026 // БЕЛАРУСЬ
          </div>

          {/* overflow:visible на обёртке — градиент chrome-text не clip'ается */}
          <div
            className="flex flex-col items-center w-full mb-14"
            style={{ overflow: "visible" }}
          >
            <div
              className="reveal-hero w-full text-center"
              style={{ overflow: "visible" }}
            >
              <span
                className="chrome-text"
                style={{ fontSize: "clamp(5rem, 17vw, 15.5rem)" }}
              >
                Отряд
              </span>
            </div>
            {/* Отрицательный margin-top убирает разрыв между строками */}
            <div
              className="reveal-hero w-full text-center"
              style={{ overflow: "visible", marginTop: "-3.00em" }}
            >
              <span
                className="chrome-text"
                style={{ fontSize: "clamp(5rem, 17vw, 15.5rem)" }}
              >
                Щит
              </span>
            </div>
          </div>

          <p className="reveal-hero mono max-w-2xl text-zinc-400 text-[11px] md:text-[13px] leading-[2.6] uppercase tracking-[0.4em] font-black mb-14 text-center">
            Автономная система детекции угроз <br className="hidden md:block" />
            и социальной инженерии. На базе DeepSeek V4.0.
          </p>

          <div className="reveal-hero">
            <div className="p-5 border-2 border-white/20 rounded-full animate-bounce bg-white/5">
              <ArrowRight className="rotate-90 text-white" size={28} />
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════════════════════
            СКАНЕР
        ══════════════════════════════════════════════════════ */}
        <section id="scanner" className="reveal-card mb-52">
          <div className="flex items-center gap-6 mb-10 text-zinc-600">
            <Terminal size={18} strokeWidth={3} />
            <span className="mono text-[10px] uppercase tracking-[0.8em] font-black">
              Core_Analyzer // Master_Feed
            </span>
            <div className="flex-1 h-px bg-zinc-800" />
          </div>

          <div className="cyber-card rounded-[3.5rem] p-3 shadow-2xl">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-2 bg-white/[0.025] rounded-[3.2rem]">
              {/* Панель ввода */}
              <div className="lg:col-span-8 bg-black rounded-[3rem] p-10 md:p-20 relative overflow-hidden min-h-[500px]">
                <div className="mono text-[10px] text-emerald-400 uppercase tracking-[0.6em] mb-10 font-black">
                  {loading
                    ? ">_ ИДЕТ ОБРАБОТКА ДАННЫХ..."
                    : ">_ СИСТЕМА ГОТОВА К ВВОДУ"}
                </div>

                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="ВСТАВЬТЕ СООБЩЕНИЕ ДЛЯ ЭКСПЕРТИЗЫ..."
                  className="w-full h-64 bg-transparent font-black italic uppercase tracking-tighter outline-none placeholder:text-zinc-800 resize-none border-none text-white leading-tight"
                  style={{
                    fontFamily: "'Unbounded', sans-serif",
                    fontSize: "clamp(1.5rem, 3.5vw, 3rem)",
                  }}
                />

                <div className="flex flex-wrap gap-8 items-center justify-between border-t border-white/12 pt-12 mt-8">
                  <button
                    onClick={handleAnalyze}
                    disabled={loading}
                    className="flex items-center gap-8 font-black italic uppercase hover:tracking-[0.04em] transition-all duration-700 disabled:opacity-20 cursor-pointer text-white"
                    style={{
                      fontFamily: "'Unbounded', sans-serif",
                      fontSize: "clamp(1.8rem, 4.5vw, 3.8rem)",
                    }}
                  >
                    {loading ? "SCAN..." : "ЗАПУСК"}
                    <Activity
                      className={`${loading ? "animate-spin" : ""} text-white`}
                      size={52}
                      strokeWidth={3}
                    />
                  </button>
                </div>
              </div>

              {/* Панель статистики */}
              <div className="lg:col-span-4 bg-[#080808] rounded-[3rem] p-10 md:p-14 flex flex-col justify-between border-l border-white/6">
                <div className="space-y-10">
                  <StatRow
                    label="Состояние"
                    value="АКТИВНО"
                    color="text-emerald-400"
                    pulse
                  />
                  <StatRow
                    label="СКАНЕР"
                    value="ПРЕМИУМ"
                    color="text-emerald-400"
                  />
                  <StatRow
                    label="Версия"
                    value="V4.0.1_BY"
                    color="text-white"
                  />
                  <StatRow
                    label="Анализы"
                    value={analysisCount + "+"}
                    color="text-white"
                  />
                </div>

                <div className="mt-14 p-7 border border-white/12 rounded-[2rem] bg-white/[0.025]">
                  <p className="mono text-[10px] text-zinc-400 font-black leading-[2] uppercase tracking-[0.15em]">
                    Периметр блокирует 99.9% фишинговых атак и попыток взлома.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Карточка результата */}
          {result && (
            <div className="result-card-anim mt-12 p-10 md:p-20 bg-white text-black rounded-[3.5rem] shadow-[0_0_80px_rgba(255,255,255,0.16)] relative overflow-hidden">
              <div className="flex flex-col md:flex-row justify-between items-start gap-10 mb-16">
                <div>
                  <div className="mono text-[11px] font-black uppercase tracking-[0.6em] mb-8 text-zinc-500">
                    Системный вердикт
                  </div>
                  <ThreatBadge level={result.threat_level_ru} />
                  <h2
                    className="font-black italic tracking-tighter uppercase leading-[0.85] mt-10"
                    style={{
                      fontFamily: "'Unbounded', sans-serif",
                      fontSize: "clamp(3rem, 8vw, 9.5rem)",
                    }}
                  >
                    {result.threat_level_ru} <br />
                    <span className="text-zinc-400">РИСК.</span>
                  </h2>
                </div>
                <div className="text-[6rem] md:text-[11rem] leading-none select-none">
                  {result.threat_emoji}
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 border-t-4 border-black/10 pt-16">
                <div>
                  <h5 className="mono text-[12px] font-black uppercase tracking-[0.5em] mb-8 flex items-center gap-3 text-zinc-600">
                    <Activity size={18} strokeWidth={3} /> Анализ_Ядра
                  </h5>
                  <p
                    className="font-black leading-tight tracking-tight uppercase italic text-black"
                    style={{
                      fontFamily: "'Unbounded', sans-serif",
                      fontSize: "clamp(1.2rem, 2.8vw, 2.8rem)",
                    }}
                  >
                    {result.explanation}
                  </p>
                </div>

                <div>
                  <h5 className="mono text-[12px] font-black uppercase tracking-[0.5em] mb-8 flex items-center gap-3 text-zinc-600">
                    <ShieldAlert size={18} strokeWidth={3} /> Индикаторы
                  </h5>
                  <div className="space-y-5">
                    {result.red_flags.map((flag: string, idx: number) => (
                      <div
                        key={idx}
                        className="flex items-center gap-5 group cursor-default"
                      >
                        <div className="w-10 h-[3px] bg-black/20 group-hover:w-16 group-hover:bg-black transition-all duration-500 flex-shrink-0" />
                        <span
                          className="font-black uppercase italic tracking-tighter text-zinc-900 break-words"
                          style={{
                            fontFamily: "'Unbounded', sans-serif",
                            fontSize: "clamp(0.85rem, 1.8vw, 1.7rem)",
                          }}
                        >
                          {flag}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {result.recommendations && (
                <div className="mt-14 flex flex-wrap gap-4 border-t-2 border-black/5 pt-12">
                  {result.recommendations.map((rec, i) => (
                    <div
                      key={i}
                      className="px-6 py-4 bg-black text-white rounded-full text-[10px] font-black uppercase italic tracking-[0.2em] shadow-lg"
                    >
                      🛡️ {rec}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </section>

        {/* ══════════════════════════════════════════════════════
            BENTO GRID (Модули)
            Исправление #2: КИБЕРДРУГ — whitespace-nowrap + clamp(2.5rem,8vw,8rem)
            Исправление #3: 77% — col-span-12, flex-layout, пустой блок удалён
        ══════════════════════════════════════════════════════ */}
        <section id="modules" className="mb-72">
          <div className="flex items-center gap-6 mb-12 text-zinc-600">
            <Cpu size={18} strokeWidth={3} />
            <span className="mono text-[10px] uppercase tracking-[1em] font-black">
              Система_Модулей
            </span>
            <div className="flex-1 h-px bg-zinc-800" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-5 reveal-card">
            {/* ── КиберДруг (col-span-8) ── */}
            <div
              onClick={() => setIsChatOpen(true)}
              className="md:col-span-8 cyber-card rounded-[3.5rem] p-10 md:p-16 flex flex-col justify-between group cursor-pointer min-h-[420px] relative"
            >
              <Radio
                className="text-zinc-600 group-hover:text-white transition-colors duration-500"
                size={68}
                strokeWidth={1.5}
              />
              <div>
                {/*
                  Исправление #2:
                  whitespace-nowrap — запрет переноса строки.
                  clamp(2.5rem, 8vw, 8rem) — на col-span-8 ~66% ширины
                  экрана, 8vw ≈ 120px на 1500px, что вписывается в одну строку.
                */}
                <h3
                  className="font-black italic uppercase mb-5 leading-none tracking-tighter text-white whitespace-nowrap"
                  style={{
                    fontFamily: "'Unbounded', sans-serif",
                    fontSize: "clamp(2.5rem, 5vw, 8rem)",
                  }}
                >
                  КиберДруг
                </h3>
                <p className="mono max-w-md text-zinc-400 text-[11px] font-bold uppercase tracking-[0.2em] leading-[2.4] mb-8">
                  Обучен на правовой базе Беларуси 2026. Консультации в реальном
                  времени.
                </p>
                <div className="flex items-center gap-4 mono text-[11px] font-black uppercase tracking-[0.4em] text-white">
                  <span>Открыть_Чат</span>
                  <ArrowRight
                    size={18}
                    className="group-hover:translate-x-3 transition-transform duration-500"
                  />
                </div>
              </div>
            </div>

            {/* ── Sec Check (col-span-4) ── */}
            <div className="md:col-span-4 cyber-card rounded-[3.5rem] p-10 md:p-14 flex flex-col justify-between group cursor-pointer min-h-[360px]">
              <Bot
                className="text-zinc-600 group-hover:text-white transition-colors duration-500"
                size={68}
                strokeWidth={1.5}
              />
              <div>
                <h3
                  className="font-black uppercase leading-[0.9] mb-5 italic tracking-tight text-white"
                  style={{
                    fontFamily: "'Unbounded', sans-serif",
                    fontSize: "clamp(3.8rem, 3.8vw, 10.2rem)",
                  }}
                >
                  Sec <br /> Check
                </h3>
                <p className="mono text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-bold leading-loose">
                  Экспресс-аудит <br /> безопасности.
                </p>
              </div>
            </div>

            {/*
              ══════════════════════════════════════════
              Исправление #3 — БЛОК 77% (ПОЛНАЯ ШИРИНА)
              Пустой блок полностью удалён.
              col-span-12 — блок занимает всю строку.
              Flex-layout: цифра слева | разделитель | описание+бары справа.
              ══════════════════════════════════════════
            */}
            <div className="md:col-span-12 cyber-card rounded-[3.5rem] p-10 md:p-16">
              <div className="flex flex-col md:flex-row items-center md:items-stretch gap-10 md:gap-16 h-full">
                {/* Левая часть: гигантский процент */}
                <div className="flex items-center justify-center flex-shrink-0">
                  <span
                    className="font-black italic text-white tracking-tighter leading-none"
                    style={{
                      fontFamily: "'Unbounded', sans-serif",
                      /*
                        clamp гарантирует, что при col-span-12
                        цифра НЕ выходит за карточку:
                        min 5rem, vw 13vw, max 13rem
                      */
                      fontSize: "clamp(5rem, 13vw, 13rem)",
                    }}
                  >
                    77%
                  </span>
                </div>

                {/* Вертикальный разделитель */}
                <div className="hidden md:block w-px bg-white/8 self-stretch flex-shrink-0" />

                {/* Правая часть: заголовок + прогресс-бары */}
                <div className="flex flex-col justify-center flex-1 gap-8">
                  <div>
                    <p className="mono text-[9px] uppercase text-zinc-600 font-black tracking-[0.5em] mb-3">
                      Статистика угроз // 2026
                    </p>
                    <p
                      className="font-black italic uppercase text-white leading-tight tracking-tighter"
                      style={{
                        fontFamily: "'Unbounded', sans-serif",
                        fontSize: "clamp(1.3rem, 2.8vw, 2.6rem)",
                      }}
                    >
                      Угроз за год связаны
                      <br />с манипуляцией.
                    </p>
                  </div>

                  {/* Декоративные прогресс-бары */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                    {/* Фишинг */}
                    <div className="flex flex-col gap-3">
                      <div className="flex justify-between items-center">
                        <span className="mono text-[9px] font-black uppercase tracking-[0.3em] text-zinc-500 flex items-center gap-2">
                          <AlertTriangle size={9} /> Фишинг
                        </span>
                        <span className="mono text-[9px] font-black text-zinc-300">
                          77%
                        </span>
                      </div>
                      <div className="threat-bar">
                        <div
                          className="threat-bar-fill"
                          style={
                            { "--bar-width": "77%" } as React.CSSProperties
                          }
                        />
                      </div>
                    </div>

                    {/* Социальная инженерия */}
                    <div className="flex flex-col gap-3">
                      <div className="flex justify-between items-center">
                        <span className="mono text-[9px] font-black uppercase tracking-[0.3em] text-zinc-500 flex items-center gap-2">
                          <Users size={9} /> Соц. инж.
                        </span>
                        <span className="mono text-[9px] font-black text-zinc-300">
                          61%
                        </span>
                      </div>
                      <div className="threat-bar">
                        <div
                          className="threat-bar-fill"
                          style={
                            { "--bar-width": "61%" } as React.CSSProperties
                          }
                        />
                      </div>
                    </div>

                    {/* Взломы */}
                    <div className="flex flex-col gap-3">
                      <div className="flex justify-between items-center">
                        <span className="mono text-[9px] font-black uppercase tracking-[0.3em] text-zinc-500 flex items-center gap-2">
                          <TrendingUp size={9} /> Взломы
                        </span>
                        <span className="mono text-[9px] font-black text-zinc-300">
                          43%
                        </span>
                      </div>
                      <div className="threat-bar">
                        <div
                          className="threat-bar-fill"
                          style={
                            { "--bar-width": "43%" } as React.CSSProperties
                          }
                        />
                      </div>
                    </div>
                  </div>

                  <p className="mono text-[8px] text-zinc-800 font-bold uppercase tracking-[0.3em]">
                    Источник: МВД РБ // Отчёт о киберпреступности 2026
                  </p>
                </div>
              </div>
            </div>

            {/* ── Кодекс (col-span-12) ── */}
            <div className="md:col-span-12 cyber-card rounded-[3.5rem] p-10 md:p-16 flex flex-col justify-between group cursor-pointer min-h-[260px]">
              <Book
                className="text-zinc-600 group-hover:text-white transition-colors duration-500"
                size={68}
                strokeWidth={1.5}
              />
              <div className="flex justify-between items-end flex-wrap gap-6">
                <h3
                  className="font-black uppercase leading-[0.9] italic tracking-tighter text-white"
                  style={{
                    fontFamily: "'Unbounded', sans-serif",
                    fontSize: "clamp(3rem, 7vw, 9rem)",
                  }}
                >
                  Кодекс
                </h3>
                <ArrowRight
                  size={42}
                  className="text-zinc-700 group-hover:text-white transition-colors duration-500 flex-shrink-0"
                />
              </div>
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════════════════════
            ROADMAP
            Исправление #4: классический чередующийся таймлайн.
            Центральная линия: absolute top-0 bottom-0 left-1/2.
            Узлы: w-1/2, кружки на right-[-13px] / left-[-13px].
            Текст НИКОГДА не наезжает на линию.
        ══════════════════════════════════════════════════════ */}
        <section
          id="roadmap"
          className="py-36 border-t border-white/8 relative"
        >
          {/* Центральная вертикальная линия */}
          <div className="absolute top-0 bottom-0 left-1/2 -translate-x-1/2 w-px bg-zinc-800 pointer-events-none" />

          <div className="text-center mb-36 relative z-10">
            <h2 className="mono text-[12px] font-black uppercase tracking-[1em] text-zinc-700 mb-8">
              Roadmap
            </h2>
            <div
              className="font-black italic text-white uppercase leading-none tracking-tighter"
              style={{
                fontFamily: "'Unbounded', sans-serif",
                fontSize: "clamp(3rem, 9vw, 10.5rem)",
              }}
            >
              Протокол
            </div>
          </div>

          <div className="max-w-4xl mx-auto relative z-10">
            <RoadmapNode
              step="01"
              title="ИСТОКИ"
              desc="Разработка нейро-ядра для анализа текстов."
              status="COMPLETED"
              side="left"
            />
            <RoadmapNode
              step="02"
              title="ОТРЯД"
              desc="Запуск модуля КиберДруг и публичного сканера."
              status="ACTIVE_PHASE"
              side="right"
              active
            />
            <RoadmapNode
              step="03"
              title="ГЛОБАЛ"
              desc="Интеграция с реестрами МВД Беларуси."
              status="RELEASE_2026"
              side="left"
            />
          </div>
        </section>
      </div>

      {/* ══════════════════════════════════════════════════════
          FOOTER
          Исправление #5: clamp(3rem, 8.5vw, 10rem) — без горизонт. скролла.
      ══════════════════════════════════════════════════════ */}
      <footer className="text-center py-32 bg-black border-t border-white/8 relative z-20 overflow-hidden">
        <div
          className="font-black italic mb-12 tracking-tighter uppercase text-zinc-800 hover:text-zinc-200 transition-all duration-1000 cursor-pointer leading-none select-none"
          style={{
            fontFamily: "'Unbounded', sans-serif",
            /*
              Исправление #5: было 14vw / 16rem — слишком широко.
              8.5vw / 10rem — мощно, но не ломает горизонтальный layout.
            */
            fontSize: "clamp(3rem, 8.5vw, 10rem)",
          }}
        >
          КИБЕРЩИТ
        </div>
        <div className="mono text-[10px] font-black uppercase tracking-[0.5em] text-zinc-700 leading-[3] px-8">
          Специально для конкурса #КИБЕРПРАВО // 2026 <br />
          МВД РЕСПУБЛИКИ БЕЛАРУСЬ // V3.4.5 <br />
          <span className="text-zinc-800 mt-8 block font-bold text-[11px] tracking-[0.8em]">
            DIGITAL PROTECTION CORE
          </span>
        </div>
      </footer>

      {/* ══════════════════════════════════════════════════════
          CHAT MODAL
      ══════════════════════════════════════════════════════ */}
      {isChatOpen && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 md:p-6">
          <div
            className="absolute inset-0 bg-black/96 backdrop-blur-md"
            onClick={() => setIsChatOpen(false)}
          />

          <div className="relative w-full max-w-5xl h-[92vh] bg-[#050505] border border-white/12 rounded-[3.5rem] shadow-[0_0_120px_rgba(0,0,0,0.9)] flex flex-col overflow-hidden">
            {/* Шапка */}
            <div className="p-8 md:p-12 border-b border-white/8 flex justify-between items-center bg-black flex-shrink-0">
              <div className="flex items-center gap-6">
                <div className="w-13 h-13 w-[52px] h-[52px] bg-white text-black rounded-[1.5rem] flex items-center justify-center shadow-[0_0_20px_rgba(255,255,255,0.2)] flex-shrink-0">
                  <Bot size={26} />
                </div>
                <div>
                  <h3
                    className="font-black italic uppercase tracking-tighter text-white"
                    style={{
                      fontFamily: "'Unbounded', sans-serif",
                      fontSize: "clamp(1.4rem, 3.5vw, 2.3rem)",
                    }}
                  >
                    КиберДруг
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_#10b981]" />
                    <span className="mono text-[9px] text-emerald-400 font-bold tracking-[0.2em] uppercase">
                      SYSTEM_ONLINE
                    </span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setIsChatOpen(false)}
                className="p-4 bg-zinc-900 rounded-full text-zinc-500 hover:text-white transition-all active:scale-90 flex-shrink-0"
              >
                <X size={22} />
              </button>
            </div>

            {/* Сообщения */}
            <div className="flex-1 overflow-y-auto p-8 md:p-14 space-y-8 scrollbar-hide">
              {chatHistory.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col ${
                    msg.role === "user" ? "items-end" : "items-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] md:max-w-[72%] p-7 rounded-[2.5rem] font-black leading-relaxed uppercase italic tracking-tight break-words text-base md:text-lg ${
                      msg.role === "user"
                        ? "bg-white text-black rounded-tr-lg shadow-xl"
                        : "bg-zinc-950 text-white border border-white/8 rounded-tl-lg shadow-xl"
                    }`}
                  >
                    {msg.content}
                  </div>
                  <span className="mono text-[8px] font-black uppercase text-zinc-700 mt-3 mx-7 tracking-[0.4em]">
                    {msg.role === "user" ? "USER_01" : "DRUG_AI"}
                  </span>
                </div>
              ))}

              {chatLoading && (
                <div className="flex items-center gap-4 mono text-[11px] font-black text-white animate-pulse uppercase px-7">
                  <Search size={16} className="animate-spin" />
                  АНАЛИЗ...
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Поле ввода */}
            <div className="p-6 md:p-8 bg-black border-t border-white/8 flex-shrink-0">
              <div className="flex gap-4 bg-[#0b0b0b] border border-white/8 rounded-[2.5rem] p-3 pl-8 focus-within:border-white/22 transition-all duration-400">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) =>
                    e.key === "Enter" && !e.shiftKey && handleSendMessage()
                  }
                  placeholder="ВВОД ДАННЫХ..."
                  className="flex-1 bg-transparent border-none outline-none mono text-[13px] font-black text-white uppercase tracking-[0.15em] placeholder:text-zinc-800"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!chatInput.trim() || chatLoading}
                  className="bg-white text-black p-5 rounded-[2rem] hover:scale-105 active:scale-95 transition-all duration-300 disabled:opacity-20 flex-shrink-0"
                >
                  <Send size={22} strokeWidth={3} />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
