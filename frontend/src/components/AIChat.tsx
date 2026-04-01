import { useEffect, useRef, useState } from 'react';
import { ArrowRight, Bot, Loader2, Plus, Search, Send, Sparkles, Square, User, X } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { AssistantRecord, ChatMessage } from '../types';
import { cn } from '../lib/utils';
import { sendAssistantQuery } from '../lib/api';

interface AIChatProps {
  onOpenServer: (serverId: string) => void;
  onApplyFilter: (value: string) => void;
}

const SUGGESTIONS = [
  '帮我找 AI 相关服务',
  '哪台机器跑着 Ollama',
  '数据库在哪些机器上',
  'Open WebUI 一般怎么排查',
];

const INITIAL_MESSAGE: ChatMessage = {
  role: 'model',
  text: '我是 ServerOps 助手。我会优先查系统里已录入的服务器和服务，再补充本地知识说明。',
};

export default function AIChat({ onOpenServer, onApplyFilter }: AIChatProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([INITIAL_MESSAGE]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleNewChat = () => {
    setMessages([INITIAL_MESSAGE]);
    setInput('');
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (question = input) => {
    const message = question.trim();
    if (!message || isLoading) {
      return;
    }

    // Create new abort controller for this request
    abortControllerRef.current = new AbortController();

    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text: message }]);
    setIsLoading(true);

    try {
      const response = await sendAssistantQuery(message, abortControllerRef.current.signal);
      setMessages((prev) => [
        ...prev,
        {
          role: 'model',
          text: response.answer.summary || '已返回相关记录。',
          answer: response.answer,
        },
      ]);
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        // Request was cancelled
        setMessages((prev) => [
          ...prev,
          { role: 'model', text: '已停止回答。' },
        ]);
      } else {
        console.error('Assistant query failed:', error);
        setMessages((prev) => [
          ...prev,
          { role: 'model', text: '抱歉，检索助手暂时不可用。' },
        ]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="glass mb-4 flex h-[680px] w-[440px] flex-col overflow-hidden rounded-2xl shadow-2xl"
          >
            <div className="flex items-center justify-between border-b border-brand-border bg-brand-card p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-accent/20">
                  <Bot className="h-5 w-5 text-brand-accent" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold">ServerOps 助手</h3>
                  <p className="text-[10px] uppercase tracking-wider text-brand-text-secondary">
                    先查记录，再补充说明
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleNewChat}
                  className="rounded-lg p-1.5 transition-colors hover:bg-brand-border"
                  title="新建会话"
                >
                  <Plus className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="rounded-lg p-1.5 transition-colors hover:bg-brand-border"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4 custom-scrollbar">
              <div className="grid grid-cols-2 gap-2">
                {SUGGESTIONS.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => void handleSend(suggestion)}
                    className="rounded-xl border border-brand-border bg-brand-card/50 px-3 py-2 text-left text-xs font-medium text-brand-text-secondary transition-colors hover:border-brand-accent/40 hover:text-brand-text-primary"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>

              {messages.map((msg, i) => (
                <div
                  key={`${msg.role}-${i}`}
                  className={cn('flex max-w-[90%] gap-3', msg.role === 'user' ? 'ml-auto flex-row-reverse' : '')}
                >
                  <div
                    className={cn(
                      'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full',
                      msg.role === 'user' ? 'bg-brand-accent' : 'bg-brand-border',
                    )}
                  >
                    {msg.role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                  </div>
                  <div
                    className={cn(
                      'rounded-2xl p-3 text-sm leading-relaxed',
                      msg.role === 'user'
                        ? 'rounded-tr-none bg-brand-accent text-white'
                        : 'rounded-tl-none border border-brand-border bg-brand-border/50 text-brand-text-primary',
                    )}
                  >
                    <p>{msg.text}</p>
                    {msg.answer && (
                      <div className="mt-3 space-y-3">
                        {msg.answer.records.length > 0 && (
                          <section className="space-y-2">
                            <p className="text-[10px] font-bold uppercase tracking-widest text-brand-text-secondary">
                              相关记录
                            </p>
                            {msg.answer.records.map((record) => (
                              <AssistantRecordCard
                                key={`${record.serverId}-${record.serviceName || 'server'}`}
                                record={record}
                                onOpenServer={onOpenServer}
                                onApplyFilter={onApplyFilter}
                              />
                            ))}
                          </section>
                        )}

                        {msg.answer.knowledge.length > 0 && (
                          <section className="space-y-2">
                            <p className="text-[10px] font-bold uppercase tracking-widest text-brand-text-secondary">
                              补充说明
                            </p>
                            {msg.answer.knowledge.map((item) => (
                              <div key={item.title} className="rounded-xl border border-brand-border bg-brand-bg/70 p-3">
                                <p className="text-xs font-bold">{item.title}</p>
                                <p className="mt-1 text-xs text-brand-text-secondary">{item.snippet}</p>
                              </div>
                            ))}
                          </section>
                        )}

                        {msg.answer.nextActions.length > 0 && (
                          <section className="space-y-2">
                            <p className="text-[10px] font-bold uppercase tracking-widest text-brand-text-secondary">
                              下一步操作
                            </p>
                            <ul className="space-y-1 text-xs text-brand-text-secondary">
                              {msg.answer.nextActions.map((action) => (
                                <li key={action} className="flex items-start gap-2">
                                  <ArrowRight className="mt-0.5 h-3 w-3 text-brand-accent" />
                                  <span>{action}</span>
                                </li>
                              ))}
                            </ul>
                          </section>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex max-w-[85%] gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-border">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="rounded-2xl rounded-tl-none border border-brand-border bg-brand-border/50 p-3">
                    <Loader2 className="h-4 w-4 animate-spin text-brand-accent" />
                  </div>
                </div>
              )}
            </div>

            <div className="border-t border-brand-border bg-brand-card p-4">
              <div className="relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !isLoading && void handleSend()}
                  placeholder="问我服务器、服务或排障问题..."
                  disabled={isLoading}
                  className="w-full rounded-xl border border-brand-border bg-brand-bg py-3 pl-4 pr-12 text-sm transition-colors focus:border-brand-accent focus:outline-none disabled:opacity-50"
                />
                {isLoading ? (
                  <button
                    onClick={handleStop}
                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg bg-red-500 p-2 text-white transition-all hover:bg-red-600"
                    title="停止回答"
                  >
                    <Square className="h-4 w-4" />
                  </button>
                ) : (
                  <button
                    onClick={() => void handleSend()}
                    disabled={!input.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg bg-brand-accent p-2 text-white transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center justify-center shadow-2xl transition-all duration-500 ease-out',
          isOpen
            ? 'h-14 w-14 rotate-90 rounded-full border border-brand-border bg-brand-card'
            : 'group h-14 gap-3 rounded-2xl bg-brand-accent px-6 hover:scale-105 hover:shadow-brand-accent/40',
        )}
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <>
            <div className="relative">
              <Sparkles className="h-6 w-6 text-white group-hover:animate-pulse" />
              <div className="absolute -right-1 -top-1 h-2 w-2 animate-ping rounded-full bg-white" />
            </div>
            <span className="text-sm font-bold tracking-wide text-white">AI 助手</span>
          </>
        )}
      </button>
    </div>
  );
}

function AssistantRecordCard({
  record,
  onOpenServer,
  onApplyFilter,
}: {
  record: AssistantRecord;
  onOpenServer: (serverId: string) => void;
  onApplyFilter: (value: string) => void;
}) {
  return (
    <div className="rounded-xl border border-brand-border bg-brand-bg/70 p-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold">{record.serviceName || record.serverName}</p>
          <p className="mt-1 text-[11px] text-brand-text-secondary">{record.serverName}</p>
          {record.notes && <p className="mt-2 text-xs text-brand-text-secondary">{record.notes}</p>}
          {record.healthUrl && <p className="mt-1 text-[11px] font-mono text-brand-accent">{record.healthUrl}</p>}
        </div>
        <span className="rounded-full border border-brand-border px-2 py-0.5 text-[10px] font-bold uppercase text-brand-text-secondary">
          {record.status}
        </span>
      </div>
      <div className="mt-3 flex gap-2">
        <button
          type="button"
          onClick={() => onOpenServer(record.serverId)}
          className="rounded-lg bg-brand-accent/10 px-3 py-1.5 text-[11px] font-bold text-brand-accent transition-colors hover:bg-brand-accent hover:text-white"
        >
          打开服务器
        </button>
        <button
          type="button"
          onClick={() => onApplyFilter(record.serviceName || record.serverName)}
          className="flex items-center gap-1 rounded-lg border border-brand-border px-3 py-1.5 text-[11px] font-bold text-brand-text-secondary transition-colors hover:border-brand-accent/40 hover:text-brand-text-primary"
        >
          <Search className="h-3 w-3" />
          加入筛选
        </button>
      </div>
    </div>
  );
}
