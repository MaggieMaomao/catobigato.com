/**
 * Calculator page — multi-mode calculator with custom functions.
 * Modes: Basic, Scientific, Trigonometric, Algebra, Calculus, Graph
 */

import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { evaluate } from 'mathjs';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import { calculatorApi } from '../api';

type CalcMode = 'basic' | 'scientific' | 'trigonometric' | 'algebra' | 'calculus' | 'graph';

interface HistoryItem {
  expression: string;
  result: string;
  latex: string;
  timestamp: Date;
  mode: CalcMode;
}

interface FunctionItem {
  id: string;
  name: string;
  description: string;
  definition: { params: { name: string; type: string }[]; body: string };
  is_public: boolean;
}

// Built-in function reference for display
const FUNCTION_REFERENCE: Record<string, { syntax: string; description: string }> = {
  abs: { syntax: 'abs(x)', description: 'Absolute value' },
  sqrt: { syntax: 'sqrt(x)', description: 'Square root' },
  cbrt: { syntax: 'cbrt(x)', description: 'Cube root' },
  log: { syntax: 'log(x)', description: 'Natural logarithm' },
  log10: { syntax: 'log(x, 10)', description: 'Base-10 logarithm' },
  sin: { syntax: 'sin(x)', description: 'Sine (radians)' },
  cos: { syntax: 'cos(x)', description: 'Cosine (radians)' },
  tan: { syntax: 'tan(x)', description: 'Tangent (radians)' },
  exp: { syntax: 'exp(x)', description: 'e^x' },
  floor: { syntax: 'floor(x)', description: 'Round down' },
  ceil: { syntax: 'ceil(x)', description: 'Round up' },
  round: { syntax: 'round(x)', description: 'Round to nearest' },
  pow: { syntax: 'pow(x, y)', description: 'x^y' },
  mod: { syntax: 'mod(x, y)', description: 'Modulo' },
  gamma: { syntax: 'gamma(x)', description: 'Gamma function' },
};

export default function CalculatorPage() {
  const { t } = useTranslation();
  const [mode, setMode] = useState<CalcMode>('basic');
  const [expression, setExpression] = useState('');
  const [result, setResult] = useState('');
  const [resultLatex, setResultLatex] = useState('');
  const [error, setError] = useState('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [customFunctions, setCustomFunctions] = useState<FunctionItem[]>([]);
  const [showFunctionCreator, setShowFunctionCreator] = useState(false);
  const [newFuncName, setNewFuncName] = useState('');
  const [newFuncDesc, setNewFuncDesc] = useState('');
  const [newFuncParams, setNewFuncParams] = useState<{ name: string; type: string }[]>([]);
  const [newFuncBody, setNewFuncBody] = useState('');
  const [plotData, setPlotData] = useState<{ x: number[]; y: number[] } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const modes: { key: CalcMode; label: string }[] = [
    { key: 'basic', label: t('calculator.basic') },
    { key: 'scientific', label: t('calculator.scientific') },
    { key: 'trigonometric', label: t('calculator.trigonometric') },
    { key: 'algebra', label: t('calculator.algebra') },
    { key: 'calculus', label: t('calculator.calculus') },
    { key: 'graph', label: t('calculator.graph') },
  ];

  // Keyboard shortcuts
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && expression.trim()) {
        handleEvaluate();
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [expression, mode]);

  // Load custom functions on mount
  useEffect(() => {
    loadCustomFunctions();
  }, []);

  const loadCustomFunctions = async () => {
    try {
      const res = await calculatorApi.listFunctions();
      setCustomFunctions(res.data.results || res.data || []);
    } catch {
      // Not logged in — that's fine
    }
  };

  const handleEvaluate = async () => {
    if (!expression.trim()) return;
    setError('');

    try {
      let res;
      if (mode === 'algebra') {
        res = await calculatorApi.simplify(expression);
        const simplified = res.data.simplified || res.data;
        setResult(typeof simplified === 'string' ? simplified : JSON.stringify(simplified));
        setResultLatex(res.data.simplified_latex || '');
      } else if (mode === 'calculus') {
        res = await calculatorApi.derivative(expression);
        setResult(res.data.derivative || res.data.error || JSON.stringify(res.data));
        setResultLatex(res.data.derivative_latex || '');
      } else if (mode === 'graph') {
        res = await calculatorApi.plot(expression);
        if (res.data.success) {
          setPlotData(res.data.points);
          setResult('');
        } else {
          setError(res.data.error || 'Plot failed');
        }
        return;
      } else {
        // Basic/scientific/trig — use mathjs client-side
        const evaluated = evaluate(expression);
        setResult(String(evaluated));
        try {
          const katexSrc = katex.renderToString(expression, { throwOnError: false, displayMode: true });
          setResultLatex(katexSrc);
        } catch {
          setResultLatex('');
        }
      }

      // Add to local history
      const latex = mode === 'algebra' ? resultLatex : '';
      setHistory((prev) => [
        { expression, result: String(result || ''), latex, timestamp: new Date(), mode },
        ...prev.slice(0, 49),
      ]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Calculation error';
      setError(msg);
      setResult('');
    }
  };

  const renderLatex = (latexStr: string) => {
    if (!latexStr) return null;
    return <div dangerouslySetInnerHTML={{ __html: latexStr }} />;
  };

  const renderPlot = (data: { x: number[]; y: number[] }) => {
    if (!data.x.length) return null;
    const minX = Math.min(...data.x);
    const maxX = Math.max(...data.x);
    const minY = Math.min(...data.y);
    const maxY = Math.max(...data.y);
    const rangeX = maxX - minX || 1;
    const rangeY = maxY - minY || 1;
    const w = 600;
    const h = 400;
    const pad = 40;

    // Normalize to SVG coordinates
    const toX = (vx: number) => pad + ((vx - minX) / rangeX) * (w - pad * 2);
    const toY = (vy: number) => h - pad - ((vy - minY) / rangeY) * (h - pad * 2);

    // Build polyline
    const points = data.x.map((xVal, i) => `${toX(xVal).toFixed(2)},${toY(data.y[i]).toFixed(2)}`).join(' ');

    // Grid lines
    const gridLines = [];
    for (let gx = Math.ceil(minX); gx <= maxX; gx++) {
      const sx = toX(gx);
      gridLines.push(<line key={`gx-${gx}`} x1={sx} y1={pad} x2={sx} y2={h - pad} stroke="var(--color-border)" strokeWidth="1" />);
    }
    for (let gy = Math.ceil(minY); gy <= maxY; gy++) {
      const sy = toY(gy);
      gridLines.push(<line key={`gy-${gy}`} x1={pad} y1={sy} x2={w - pad} y2={sy} stroke="var(--color-border)" strokeWidth="1" />);
    }

    return (
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full max-w-2xl border border-border rounded-lg bg-bg">
        {/* Grid */}
        {gridLines}
        {/* X axis */}
        <line x1={pad} y1={toY(0)} x2={w - pad} y2={toY(0)} stroke="var(--color-secondary)" strokeWidth="1.5" />
        {/* Y axis */}
        <line x1={toX(0)} y1={pad} x2={toX(0)} y2={h - pad} stroke="var(--color-secondary)" strokeWidth="1.5" />
        {/* Function curve */}
        <polyline
          points={points}
          fill="none"
          stroke="var(--color-primary)"
          strokeWidth="2"
          strokeLinejoin="round"
        />
        {/* Axis labels */}
        <text x={w - pad} y={toY(0) - 5} fontSize="12" fill="var(--color-secondary)">x</text>
        <text x={toX(0) + 5} y={pad - 5} fontSize="12" fill="var(--color-secondary)">y</text>
      </svg>
    );
  };

  const insertSymbol = (sym: string) => {
    if (inputRef.current) {
      const start = inputRef.current.selectionStart || expression.length;
      setExpression((prev) => prev.slice(0, start) + sym + prev.slice(start));
      inputRef.current.focus();
    } else {
      setExpression((prev) => prev + sym);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 p-6 max-w-7xl mx-auto">
      {/* Main calculator */}
      <div className="flex-1 min-w-0">
        {/* Mode tabs */}
        <div className="flex gap-1 mb-4 overflow-x-auto">
          {modes.map((m) => (
            <button
              key={m.key}
              onClick={() => { setMode(m.key); setResult(''); setError(''); setPlotData(null); }}
              className={`px-4 py-2 text-sm rounded-lg whitespace-nowrap transition-colors ${
                mode === m.key
                  ? 'bg-primary text-white'
                  : 'bg-[--color-bg-secondary] text-secondary hover:bg-[--color-border]'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>

        {/* Expression input */}
        <div className="relative mb-3">
          <input
            ref={inputRef}
            type="text"
            value={expression}
            onChange={(e) => setExpression(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleEvaluate()}
            placeholder={
              mode === 'calculus'
                ? 'e.g., x^2 + 3*x + 1'
                : mode === 'graph'
                ? 'e.g., sin(x) or x^2 - 4'
                : 'e.g., 2+2, sqrt(16), sin(pi/4)'
            }
            className="w-full px-4 py-3 text-xl font-mono border border-border rounded-lg bg-bg focus:outline-none focus:border-primary"
          />
          <button
            onClick={() => setExpression('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary hover:text-[--color-text-heading]"
          >
            ✕
          </button>
        </div>

        {/* Result / Error */}
        {error && (
          <div className="mb-3 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}
        {result && (
          <div className="mb-4 p-4 rounded-lg bg-[--color-bg-secondary] border border-border">
            <div className="text-xs text-secondary mb-1">{t('calculator.result')}</div>
            <div className="text-2xl font-mono text-[--color-text-heading]">{result}</div>
            {resultLatex && <div className="mt-2">{renderLatex(resultLatex)}</div>}
          </div>
        )}

        {/* Graph output */}
        {plotData && (
          <div className="mb-4">
            <div className="text-xs text-secondary mb-2">{expression}</div>
            {renderPlot(plotData)}
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-3 mb-6">
          <button
            onClick={handleEvaluate}
            className="px-6 py-2 bg-primary text-white rounded-lg font-semibold hover:bg-[--color-primary-hover] transition-colors"
          >
            {t('calculator.evaluate')}
          </button>
          <button
            onClick={() => { setExpression(''); setResult(''); setError(''); setPlotData(null); }}
            className="px-6 py-2 border border-border rounded-lg hover:bg-[--color-bg-secondary] transition-colors"
          >
            {t('calculator.clear')}
          </button>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="px-4 py-2 text-sm text-secondary border border-border rounded-lg hover:bg-[--color-bg-secondary]"
          >
            {t('calculator.history')} ({history.length})
          </button>
        </div>

        {/* Mode-specific buttons */}
        <div className="flex flex-wrap gap-2 mb-6">
          {mode === 'basic' || mode === 'scientific' ? (
            <>
              {['7', '8', '9', '/', '4', '5', '6', '*', '1', '2', '3', '-', '0', '.', '=', '+'].map((btn) => (
                <CalcButton key={btn} label={btn} onClick={() => insertSymbol(btn === '=' ? '' : btn)} />
              ))}
              {['sqrt(', 'abs(', 'pow(', 'log(', 'exp('].map((fn) => (
                <CalcButton key={fn} label={fn} onClick={() => insertSymbol(fn)} small />
              ))}
            </>
          ) : mode === 'trigonometric' ? (
            <>
              {['sin(', 'cos(', 'tan(', 'asin(', 'acos(', 'atan('].map((fn) => (
                <CalcButton key={fn} label={fn} onClick={() => insertSymbol(fn)} />
              ))}
              <CalcButton label="π" onClick={() => insertSymbol('pi')} />
              <CalcButton label="e" onClick={() => insertSymbol('e')} />
            </>
          ) : mode === 'algebra' ? (
            <>
              {['x', 'y', 'z', '^', 'sqrt(', 'factor(', 'expand('].map((s) => (
                <CalcButton key={s} label={s} onClick={() => insertSymbol(s)} small />
              ))}
              <button
                onClick={async () => {
                  if (!expression) return;
                  try {
                    const r = await calculatorApi.factor(expression);
                    setResult(r.data.factored || JSON.stringify(r.data));
                  } catch { setError('Server error'); }
                }}
                className="px-3 py-1.5 text-xs border border-border rounded hover:bg-[--color-bg-secondary]"
              >
                Factor
              </button>
            </>
          ) : mode === 'calculus' ? (
            <>
              <div className="text-xs text-secondary mb-2">Expression → derivative with respect to x</div>
              {['d/dx', '∫', 'solve'].map((s) => (
                <CalcButton key={s} label={s} onClick={() => insertSymbol(s)} small />
              ))}
            </>
          ) : null}
        </div>

        {/* Function reference */}
        <div className="text-xs text-secondary">
          <div className="font-semibold mb-2">Available functions:</div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-1">
            {Object.entries(FUNCTION_REFERENCE).map(([name, info]) => (
              <button
                key={name}
                onClick={() => insertSymbol(info.syntax)}
                className="text-left px-2 py-1 rounded hover:bg-[--color-bg-secondary]"
                title={info.description}
              >
                <code className="text-[--color-primary]">{info.syntax}</code>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Right sidebar */}
      <div className="w-full lg:w-80 flex flex-col gap-4">
        {/* Custom functions */}
        <div className="border border-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-sm">{t('calculator.myFunctions')}</h3>
            <button
              onClick={() => setShowFunctionCreator(!showFunctionCreator)}
              className="text-xs px-3 py-1 bg-primary text-white rounded hover:bg-[--color-primary-hover]"
            >
              {showFunctionCreator ? '−' : '+'} {t('calculator.createFunction')}
            </button>
          </div>

          {/* Function creator */}
          {showFunctionCreator && (
            <div className="mb-4 p-3 bg-[--color-bg-secondary] rounded-lg">
              <input
                type="text"
                value={newFuncName}
                onChange={(e) => setNewFuncName(e.target.value)}
                placeholder={t('calculator.functionName')}
                className="w-full px-2 py-1 mb-2 text-sm border border-border rounded"
              />
              <input
                type="text"
                value={newFuncDesc}
                onChange={(e) => setNewFuncDesc(e.target.value)}
                placeholder="Description"
                className="w-full px-2 py-1 mb-2 text-sm border border-border rounded"
              />
              <div className="flex gap-1 mb-2">
                <input
                  type="text"
                  value={newFuncParams.map((p) => p.name).join(', ')}
                  placeholder="x, y (comma-separated)"
                  className="flex-1 px-2 py-1 text-xs border border-border rounded"
                  onChange={(e) =>
                    setNewFuncParams(
                      e.target.value.split(',').map((n) => ({ name: n.trim(), type: 'number' })).filter((p) => p.name)
                    )
                  }
                />
              </div>
              <textarea
                value={newFuncBody}
                onChange={(e) => setNewFuncBody(e.target.value)}
                placeholder="e.g., x^2 + sin(y)"
                className="w-full px-2 py-1 mb-2 text-xs border border-border rounded font-mono"
                rows={2}
              />
              <button
                onClick={async () => {
                  if (!newFuncName || !newFuncBody) return;
                  try {
                    await calculatorApi.createFunction({
                      name: newFuncName,
                      description: newFuncDesc,
                      definition: { params: newFuncParams, body: newFuncBody },
                      is_public: false,
                    });
                    setNewFuncName('');
                    setNewFuncDesc('');
                    setNewFuncParams([]);
                    setNewFuncBody('');
                    setShowFunctionCreator(false);
                    loadCustomFunctions();
                  } catch { setError('Failed to save function'); }
                }}
                className="w-full px-3 py-1.5 bg-primary text-white text-xs rounded"
              >
                {t('calculator.saveFunction')}
              </button>
            </div>
          )}

          {/* Function list */}
          {customFunctions.length === 0 ? (
            <p className="text-xs text-secondary">{t('common.noData')}</p>
          ) : (
            <div className="space-y-2">
              {customFunctions.map((fn) => (
                <div key={fn.id} className="p-2 border border-border rounded text-xs">
                  <div className="font-semibold text-[--color-primary]">{fn.name}</div>
                  <div className="text-secondary">{fn.description || 'No description'}</div>
                  <div className="font-mono text-secondary mt-1">
                    ({fn.definition.params.map((p) => p.name).join(', ')}) = {fn.definition.body}
                  </div>
                  <button
                    onClick={() => insertSymbol(`${fn.name}(`) }
                    className="mt-1 text-xs text-primary hover:underline"
                  >
                    Use →
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* History panel */}
        {showHistory && (
          <div className="border border-border rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-sm">{t('calculator.history')}</h3>
              <button
                onClick={() => { setHistory([]); calculatorApi.clearHistory(); }}
                className="text-xs text-secondary hover:text-error"
              >
                Clear
              </button>
            </div>
            {history.length === 0 ? (
              <p className="text-xs text-secondary">No history yet</p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {history.map((item, i) => (
                  <button
                    key={i}
                    onClick={() => setExpression(item.expression)}
                    className="w-full text-left p-2 rounded hover:bg-[--color-bg-secondary] text-xs"
                  >
                    <div className="font-mono text-[--color-text-heading]">{item.expression}</div>
                    <div className="text-secondary">= {item.result}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function CalcButton({ label, onClick, small }: { label: string; onClick: () => void; small?: boolean }) {
  return (
    <button
      onClick={onClick}
      className={`${small ? 'px-2 py-1 text-xs' : 'px-4 py-2 text-sm'} border border-border rounded hover:bg-[--color-bg-secondary] font-mono transition-colors`}
    >
      {label}
    </button>
  );
}