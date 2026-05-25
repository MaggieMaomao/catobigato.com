/**
 * VisualMath page — GeoGebra sketches + Math Animations.
 * Modes: LaTeX (static render), GeoGebra (interactive sketch), Animation (video)
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import { visualMathApi } from '../api';

type VisualMode = 'latex' | 'geogebra' | 'animate';
type AnimationStatus = 'idle' | 'pending' | 'analysis' | 'design' | 'coding' | 'rendering' | 'done' | 'failed';

interface VisualMathResult {
  type: VisualMode;
  success: boolean;
  latex?: string;
  result?: unknown;
  commands?: string[];
  warnings?: string[];
  project_id?: string;
  polling_url?: string;
  status?: AnimationStatus;
  message?: string;
  sketch_id?: string;
  error?: string;
}

// GeoGebra applet loader
declare global {
  interface Window {
    GGBApplet?: new (config: Record<string, unknown>, material_id?: unknown) => { setHTMLString: (s: string) => void; inject: (id: string) => void };
    onGGBInit?: () => void;
  }
}

function loadGGBApplet(): Promise<void> {
  return new Promise((resolve) => {
    if (window.GGBApplet) { resolve(); return; }
    const script = document.createElement('script');
    script.src = 'https://cdn.geogebra.org/apps/deployggb.js';
    script.onload = () => {
      // GGBApplet loads asynchronously, poll until ready
      const check = setInterval(() => {
        if (window.GGBApplet) { clearInterval(check); resolve(); }
      }, 100);
    };
    document.head.appendChild(script);
  });
}

export default function VisualMathPage() {
  const { t } = useTranslation();
  const [mode, setMode] = useState<VisualMode>('latex');
  const [input, setInput] = useState('');
  const [result, setResult] = useState<VisualMathResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [animationStatus, setAnimationStatus] = useState<AnimationStatus>('idle');
  const [ggbAppletLoaded, setGgbAppletLoaded] = useState(false);
  const ggbContainerRef = useRef<HTMLDivElement>(null);
  const ggbAppletRef = useRef<unknown>(null);
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const modes: { key: VisualMode; label: string }[] = [
    { key: 'latex', label: t('visual_math.latex') ?? 'LaTeX' },
    { key: 'geogebra', label: t('visual_math.geogebra') ?? 'GeoGebra' },
    { key: 'animate', label: t('visual_math.animate') ?? 'Animation' },
  ];

  // Load GeoGebra applet when switching to geogebra mode
  useEffect(() => {
    if (mode === 'geogebra') {
      loadGGBApplet().then(() => setGgbAppletLoaded(true)).catch(() => {
        setError('Failed to load GeoGebra. Check your internet connection.');
      });
    }
  }, [mode]);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => { if (pollIntervalRef.current) clearInterval(pollIntervalRef.current); };
  }, []);

  const initGGBApplet = useCallback((commands: string[]) => {
    if (!ggbContainerRef.current || !window.GGBApplet) return;
    ggbContainerRef.current.innerHTML = '';

    const applet = new window.GGBApplet({
      width: 600,
      height: 450,
      showToolBar: true,
      showMenuBar: true,
      showAlgebraInput: true,
      enableLabelDrags: true,
      enableRightClick: true,
      errorDialogsActive: true,
      showResetIcon: true,
      enableCAS: true,
    }, true);

    applet.setHTMLString(''); // start blank
    applet.inject(ggbContainerRef.current.id);
    ggbAppletRef.current = applet;

    // Wait for applet to init, then eval commands
    const waitForInit = setInterval(() => {
      try {
        const appletObj = (window as unknown as Record<string, { evalCommand: (cmd: string) => boolean }>)[`ggbApplet_${ggbContainerRef.current?.id}`];
        if (appletObj && typeof appletObj.evalCommand === 'function') {
          clearInterval(waitForInit);
          commands.forEach((cmd) => {
            try { appletObj.evalCommand(cmd); } catch { /* skip bad commands */ }
          });
        }
      } catch { /* not ready yet */ }
    }, 300);
  }, []);

  const handleSubmit = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await visualMathApi.solve({
        user_input: input,
        mode: mode === 'animate' ? 'animate' : mode,
        output_mode: 'video',
        quality: 'medium',
      });
      setResult(response.data);

      if (response.data.type === 'geogebra' && response.data.commands?.length) {
        // Small delay to let the div mount
        setTimeout(() => initGGBApplet(response.data.commands), 500);
      }
      if (response.data.type === 'animate') {
        // Start polling for animation status
        const projectId = response.data.project_id;
        if (projectId) startPolling(projectId);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const startPolling = (projectId: string) => {
    setAnimationStatus('pending');
    pollIntervalRef.current = setInterval(async () => {
      try {
        const resp = await visualMathApi.getAnimationStatus(projectId);
        const data = resp.data;
        setAnimationStatus(data.status as AnimationStatus);
        if (data.status === 'done' || data.status === 'failed') {
          if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
          if (data.status === 'done') setResult((r) => r ? { ...r, rendered_output_url: data.rendered_output_url } : null);
          if (data.status === 'failed') setError(data.error_message || 'Animation failed');
        }
      } catch { /* keep polling */ }
    }, 3000);
  };

  const renderLatex = (latex: string) => {
    try {
      return <div className="text-2xl font-mono overflow-x-auto"
        dangerouslySetInnerHTML={{ __html: katex.renderToString(latex, { throwOnError: false, displayMode: true }) }}
      />;
    } catch {
      return <code className="text-secondary">{latex}</code>;
    }
  };

  const statusLabel: Record<AnimationStatus, string> = {
    idle: t('visual_math.status_idle') ?? '—',
    pending: t('visual_math.status_pending') ?? 'Queued',
    analysis: t('visual_math.status_analysis') ?? 'Analyzing concept...',
    design: t('visual_math.status_design') ?? 'Designing scene...',
    coding: t('visual_math.status_coding') ?? 'Generating code...',
    rendering: t('visual_math.status_rendering') ?? 'Rendering animation...',
    done: t('visual_math.status_done') ?? 'Done!',
    failed: t('visual_math.status_failed') ?? 'Failed',
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-[--ink] mb-1">
          {t('nav.visual_math') ?? 'Visual Math'}
        </h1>
        <p className="text-secondary text-sm">
          {t('visual_math.subtitle') ?? 'Interactive geometry, animations, and LaTeX rendering.'}
        </p>
      </div>

      {/* Mode tabs */}
      <div className="flex gap-2 mb-6 border-b border-border pb-2">
        {modes.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => { setMode(key); setResult(null); setError(''); }}
            className={`px-4 py-2 rounded-t text-sm font-medium transition-colors ${
              mode === key
                ? 'bg-primary text-white'
                : 'bg-transparent text-secondary hover:text-[--ink]'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Input area */}
      <div className="flex gap-3 mb-6">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            mode === 'latex' ? t('visual_math.latex_placeholder') ?? 'e.g. x^2 + y^2 = 1' :
            mode === 'geogebra' ? t('visual_math.geogebra_placeholder') ?? 'e.g. triangle with circumcircle' :
            t('visual_math.animate_placeholder') ?? 'e.g. show how a circle area formula is derived'
          }
          rows={2}
          className="flex-1 border border-border rounded px-3 py-2 text-sm font-mono resize-none focus:border-primary focus:outline-none"
          onKeyDown={(e) => { if (e.key === 'Enter' && e.ctrlKey) handleSubmit(); }}
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !input.trim()}
          className="px-6 py-2 bg-primary text-white rounded font-medium text-sm hover:opacity-90 disabled:opacity-50"
        >
          {loading ? '...' : t('visual_math.render') ?? 'Render'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Result area */}
      {result && (
        <div className="border border-border rounded-lg overflow-hidden">
          {/* Result header */}
          <div className="bg-[--color-surface] px-4 py-2 border-b border-border flex items-center justify-between">
            <span className="text-xs font-medium text-secondary uppercase tracking-wide">
              {result.type === 'latex' ? 'LaTeX' : result.type === 'geogebra' ? 'GeoGebra' : 'Animation'}
            </span>
            {result.success === false && (
              <span className="text-xs text-red-500">⚠ {result.error}</span>
            )}
          </div>

          {/* LaTeX output */}
          {result.type === 'latex' && result.latex && (
            <div className="p-6 flex justify-center">
              {renderLatex(result.latex)}
            </div>
          )}

          {/* GeoGebra output */}
          {result.type === 'geogebra' && (
            <div className="p-4">
              {/* Command list */}
              {result.commands && result.commands.length > 0 && (
                <div className="mb-3">
                  <p className="text-xs text-secondary mb-1">
                    {t('visual_math.ggb_commands') ?? 'Commands:'}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {result.commands.map((cmd, i) => (
                      <code key={i} className="bg-surface px-2 py-1 rounded text-xs font-mono">
                        {cmd}
                      </code>
                    ))}
                  </div>
                </div>
              )}
              {/* GeoGebra applet container */}
              <div
                id="ggb-container"
                ref={ggbContainerRef}
                className="w-full rounded overflow-hidden border border-border"
                style={{ minHeight: 400 }}
              />
              {!ggbAppletLoaded && (
                <p className="text-xs text-secondary mt-2">
                  {t('visual_math.loading_geogebra') ?? 'Loading GeoGebra...'}
                </p>
              )}
            </div>
          )}

          {/* Animation output */}
          {result.type === 'animate' && (
            <div className="p-6">
              {/* Status */}
              <div className="flex items-center gap-3 mb-4">
                <div className={`w-3 h-3 rounded-full ${
                  animationStatus === 'done' ? 'bg-green-500' :
                  animationStatus === 'failed' ? 'bg-red-500' :
                  animationStatus === 'pending' ? 'bg-yellow-400 animate-pulse' :
                  'bg-blue-400 animate-pulse'
                }`} />
                <span className="text-sm font-medium">
                  {statusLabel[animationStatus]}
                </span>
              </div>

              {result.message && (
                <p className="text-sm text-secondary mb-2">{result.message}</p>
              )}

              {/* Video player */}
              {(result as unknown as { rendered_output_url?: string }).rendered_output_url && (
                <video
                  src={(result as unknown as { rendered_output_url: string }).rendered_output_url}
                  controls
                  className="w-full rounded"
                />
              )}
            </div>
          )}
        </div>
      )}

      {/* Mode-specific tips */}
      <div className="mt-6 text-xs text-secondary">
        {mode === 'latex' && (
          <p>{t('visual_math.tip_latex') ?? 'Tip: Type any math expression. Press Ctrl+Enter to render.'}</p>
        )}
        {mode === 'geogebra' && (
          <p>{t('visual_math.tip_geogebra') ?? 'Tip: Use geometry keywords like triangle, circle, angle, bisector.'}</p>
        )}
        {mode === 'animate' && (
          <p>{t('visual_math.tip_animate') ?? 'Tip: Describe a process or transformation: "show how sin(x) changes as x goes from 0 to pi".'}</p>
        )}
      </div>
    </div>
  );
}