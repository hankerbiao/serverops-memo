import { useState, useEffect } from 'react';
import { X, Plus, Server, Shield, Terminal, Trash2, Copy, Check, Link as LinkIcon, ArrowLeft, Key, User as UserIcon, Activity, Edit2, AlertTriangle, Sparkles, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { ServerInfo, ServerPayload, Service } from '../types';
import { cn } from '../lib/utils';
import { extractServerInfo } from '../lib/api';

interface ServerCardProps {
  server: ServerInfo;
  onDelete: (id: string) => void;
  onEdit: (server: ServerInfo) => void;
  onViewDetail: (id: string) => void;
}

export function ServerCard({ server, onDelete, onEdit, onViewDetail }: ServerCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-red-500',
    maintenance: 'bg-yellow-500',
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-3xl p-6 group hover:border-brand-accent/40 hover:shadow-xl hover:shadow-brand-accent/5 transition-all duration-300 flex flex-col h-full card-hover"
    >
      <div className="flex items-start justify-between mb-5">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-brand-accent/20 to-purple-500/10 flex items-center justify-center border border-brand-accent/20 group-hover:border-brand-accent/40 transition-colors">
            <Server className="w-6 h-6 text-brand-accent" />
          </div>
          <div>
            <h3 className="font-bold text-lg leading-tight group-hover:text-brand-accent transition-colors">{server.name}</h3>
            <div className="flex items-center gap-2 text-brand-text-secondary text-sm">
              <code className="text-xs font-mono text-brand-accent bg-brand-accent/10 px-2 py-0.5 rounded">{server.ip}</code>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleCopy(server.ip);
                }}
                className="opacity-0 group-hover:opacity-100 transition-all p-1 hover:bg-brand-accent/10 rounded"
              >
                {copied ? <Check className="w-3 h-3 text-green-500" /> : <Copy className="w-3 h-3 text-brand-text-secondary" />}
              </button>
            </div>
          </div>
        </div>
        <div className={cn(
          "flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider border",
          server.status === 'online' && "status-online",
          server.status === 'offline' && "status-offline",
          server.status === 'maintenance' && "status-maintenance"
        )}>
          <div className={cn("w-1.5 h-1.5 rounded-full animate-pulse", statusColors[server.status])} />
          {server.status}
        </div>
      </div>

      <div className="flex-1 space-y-4 mb-5">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Terminal className="w-3.5 h-3.5 text-brand-accent" />
            <span className="text-[11px] uppercase tracking-widest text-brand-text-secondary font-semibold">运行中的服务</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {server.services.map((service, idx) => (
              <span key={idx} className="px-3 py-1.5 bg-brand-accent/10 text-brand-accent text-[11px] font-bold rounded-lg border border-brand-accent/20 group-hover:border-brand-accent/40 transition-colors">
                {service.name}
              </span>
            ))}
            {server.services.length === 0 && (
              <span className="text-xs text-brand-text-secondary italic">未列出服务</span>
            )}
          </div>
        </div>

        {server.notes && (
          <p className="text-xs leading-relaxed text-brand-text-secondary line-clamp-2">
            {server.notes}
          </p>
        )}
      </div>

      <div className="flex items-center gap-2 pt-4 border-t border-brand-border/60">
        <button
          onClick={() => onViewDetail(server.id)}
          className="flex-1 bg-brand-accent/10 text-brand-accent hover:bg-brand-accent hover:text-white py-2.5 rounded-xl text-xs font-bold transition-all active:scale-[0.98]"
        >
          查看详情
        </button>
        <button
          onClick={() => onEdit(server)}
          className="btn-icon text-brand-text-secondary hover:text-brand-accent hover:bg-brand-accent/10"
          title="编辑服务器"
        >
          <Edit2 className="w-4 h-4" />
        </button>
        <button
          onClick={() => onDelete(server.id)}
          className="btn-icon text-brand-text-secondary hover:text-red-500 hover:bg-red-500/10"
          title="删除服务器"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
}

interface ServerDetailProps {
  server: ServerInfo;
  onEdit: () => void;
  onBack: () => void;
}

export function ServerDetail({ server, onEdit, onBack }: ServerDetailProps) {
  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-red-500',
    maintenance: 'bg-yellow-500',
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="space-y-8 page-enter"
    >
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-brand-text-secondary hover:text-brand-text-primary transition-colors group"
      >
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
        <span className="text-sm font-bold">返回服务器列表</span>
      </button>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Left Column: Info & Credentials */}
        <div className="flex-1 space-y-6">
          <div className="glass rounded-3xl p-8 shadow-xl shadow-black/5">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-6">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-accent/20 to-purple-500/10 flex items-center justify-center border border-brand-accent/20 shadow-lg shadow-brand-accent/10">
                  <Server className="w-8 h-8 text-brand-accent" />
                </div>
                <div>
                  <h2 className="text-3xl font-black tracking-tight">{server.name}</h2>
                  <code className="text-brand-accent font-mono bg-brand-accent/10 px-3 py-1 rounded-lg">{server.ip}</code>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={onEdit}
                  className="flex items-center gap-2 bg-brand-accent/10 text-brand-accent px-5 py-2.5 rounded-2xl border border-brand-accent/20 hover:bg-brand-accent hover:text-white hover:shadow-lg hover:shadow-brand-accent/20 transition-all font-bold text-sm"
                >
                  <Edit2 className="w-4 h-4" />
                  编辑
                </button>
                <div className={cn(
                  "flex items-center gap-3 px-5 py-2.5 rounded-2xl border font-bold text-sm uppercase tracking-wider",
                  server.status === 'online' && "status-online",
                  server.status === 'offline' && "status-offline",
                  server.status === 'maintenance' && "status-maintenance"
                )}>
                  <div className={cn("w-2 h-2 rounded-full animate-pulse", statusColors[server.status])} />
                  {server.status}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-widest text-brand-text-secondary flex items-center gap-2">
                  <Shield className="w-3 h-3" />
                  访问凭证
                </h3>
                <div className="space-y-4 bg-brand-bg/50 p-6 rounded-2xl border border-brand-border">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <UserIcon className="w-4 h-4 text-brand-text-secondary" />
                      <span className="text-sm text-brand-text-secondary">用户名</span>
                    </div>
                    <span className="font-mono text-sm font-bold">{server.username}</span>
                  </div>
                  <div className="h-px bg-brand-border" />
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Key className="w-4 h-4 text-brand-text-secondary" />
                      <span className="text-sm text-brand-text-secondary">密码</span>
                    </div>
                    <span className="font-mono text-sm font-bold text-brand-accent">{server.password || '不适用'}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-widest text-brand-text-secondary flex items-center gap-2">
                  <Activity className="w-3 h-3" />
                  系统信息
                </h3>
                <div className="space-y-4 bg-brand-bg/50 p-6 rounded-2xl border border-brand-border">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-brand-text-secondary">最后检查</span>
                    <span className="text-sm font-medium">{server.lastChecked}</span>
                  </div>
                  <div className="h-px bg-brand-border" />
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-brand-text-secondary">标识符</span>
                    <span className="text-xs font-mono text-brand-text-secondary">{server.id}</span>
                  </div>
                </div>
              </div>

              {/* Notes Section */}
              {server.notes && (
                <div className="space-y-4">
                  <h3 className="text-xs font-bold uppercase tracking-widest text-brand-text-secondary flex items-center gap-2">
                    <FileText className="w-3 h-3" />
                    备注
                  </h3>
                  <div className="bg-brand-bg/50 p-6 rounded-2xl border border-brand-border">
                    <p className="text-sm text-brand-text-secondary whitespace-pre-wrap">{server.notes}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Services */}
        <div className="w-full md:w-96 space-y-6">
          <div className="glass rounded-3xl p-8">
            <h3 className="text-xs font-bold uppercase tracking-widest text-brand-text-secondary mb-6 flex items-center gap-2">
              <Terminal className="w-3 h-3" />
              服务健康状态
            </h3>
            <div className="space-y-3">
              {server.services.map((service, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-brand-bg border border-brand-border space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm">{service.name}</span>
                    <span className={cn(
                      "text-[9px] font-bold uppercase px-2 py-0.5 rounded border",
                      service.status === 'online' ? "text-green-500 border-green-500/20 bg-green-500/10" : "text-red-500 border-red-500/20 bg-red-500/10"
                    )}>
                      {service.status}
                    </span>
                  </div>
                  {service.notes && (
                    <p className="text-xs text-brand-text-secondary">{service.notes}</p>
                  )}
                  {service.healthUrl && (
                    <a 
                      href={service.healthUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-[10px] text-brand-accent hover:underline flex items-center gap-1 truncate"
                    >
                      <LinkIcon className="w-2 h-2" />
                      {service.healthUrl}
                    </a>
                  )}
                </div>
              ))}
              {server.services.length === 0 && (
                <div className="text-center py-8 text-brand-text-secondary text-sm italic">
                  未配置服务
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

interface ServiceListProps {
  servers: ServerInfo[];
}

export function ServiceList({ servers }: ServiceListProps) {
  const allServices = servers.flatMap(server => 
    server.services.map(service => ({ ...service, serverName: server.name, serverIp: server.ip }))
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="glass rounded-3xl overflow-hidden border border-brand-border">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-brand-card border-b border-brand-border">
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-brand-text-secondary">服务名称</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-brand-text-secondary">主机服务器</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-brand-text-secondary">健康检查端点</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-brand-text-secondary">状态</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-border">
            {allServices.map((item, idx) => (
              <tr key={idx} className="hover:bg-brand-card/50 transition-colors group">
                <td className="px-6 py-4">
                  <span className="font-bold text-sm">{item.name}</span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">{item.serverName}</span>
                    <span className="text-[10px] font-mono text-brand-text-secondary">{item.serverIp}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  {item.healthUrl ? (
                    <a 
                      href={item.healthUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-xs text-brand-accent hover:underline flex items-center gap-1"
                    >
                      <LinkIcon className="w-3 h-3" />
                      {item.healthUrl}
                    </a>
                  ) : (
                    <span className="text-xs text-brand-text-secondary italic">不适用</span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className={cn(
                    "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border",
                    item.status === 'online' ? "text-green-500 border-green-500/20 bg-green-500/10" : "text-red-500 border-red-500/20 bg-red-500/10"
                  )}>
                    <div className={cn("w-1.5 h-1.5 rounded-full", item.status === 'online' ? "bg-green-500" : "bg-red-500")} />
                    {item.status}
                  </span>
                </td>
              </tr>
            ))}
            {allServices.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-brand-text-secondary italic">
                  所有服务器上未找到服务
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}

interface ServerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (server: ServerPayload) => Promise<void>;
  editingServer?: ServerInfo | null;
  isSubmitting?: boolean;
}

export function ServerModal({ isOpen, onClose, onAdd, editingServer, isSubmitting = false }: ServerModalProps) {
  const isEditing = !!editingServer;
  const [formData, setFormData] = useState({
    name: '',
    ip: '',
    username: 'root',
    password: '',
    status: 'online' as 'online' | 'offline' | 'maintenance',
    aliases: '',
    tags: '',
    notes: '',
  });

  const [services, setServices] = useState<Omit<Service, 'status' | 'category' | 'aliases'>[]>([
    { name: '', healthUrl: '', notes: '' }
  ]);

  const [aiDescription, setAiDescription] = useState('');
  const [isExtracting, setIsExtracting] = useState(false);

  useEffect(() => {
    if (editingServer) {
      setFormData({
        name: editingServer.name,
        ip: editingServer.ip,
        username: editingServer.username,
        password: editingServer.password || '',
        status: editingServer.status,
        aliases: editingServer.aliases.join(', '),
        tags: editingServer.tags.map((tag) => tag.name).join(', '),
        notes: editingServer.notes || '',
      });
      setServices(editingServer.services.map(({ status, ...rest }) => rest));
    } else {
      setFormData({
        name: '',
        ip: '',
        username: 'root',
        password: '',
        status: 'online',
        aliases: '',
        tags: '',
        notes: '',
      });
      setServices([{ name: '', healthUrl: '', notes: '' }]);
    }
  }, [editingServer, isOpen]);

  const handleAddServiceField = () => {
    setServices([...services, { name: '', healthUrl: '', notes: '' }]);
  };

  const handleRemoveServiceField = (index: number) => {
    setServices(services.filter((_, i) => i !== index));
  };

  const handleServiceChange = (index: number, field: keyof Omit<Service, 'status' | 'category' | 'aliases'>, value: string) => {
    const newServices = [...services];
    newServices[index] = { ...newServices[index], [field]: value };
    setServices(newServices);
  };

  const handleAiExtract = async () => {
    if (!aiDescription.trim()) return;
    setIsExtracting(true);
    try {
      const response = await extractServerInfo(aiDescription);
      if (response.success && response.data) {
        const data = response.data;
        setFormData(prev => ({
          ...prev,
          ip: data.ip || prev.ip,
          username: data.username || prev.username,
          password: data.password || prev.password,
          aliases: data.aliases?.join(', ') || prev.aliases,
          notes: data.notes || prev.notes,
        }));
        if (data.services && data.services.length > 0) {
          setServices(data.services.map(s => ({
            name: s.name,
            healthUrl: s.healthUrl || '',
            notes: s.notes || '',
          })));
        }
      }
    } catch (error) {
      console.error('AI extraction failed:', error);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await onAdd({
        ...formData,
        name: isEditing ? formData.name : formData.ip.trim(),
        password: formData.password || undefined,
        status: isEditing ? formData.status : 'online',
        aliases: splitCommaValues(formData.aliases),
        tags: isEditing ? splitCommaValues(formData.tags).map((tag) => ({ name: tag, color: '#3b82f6' })) : [],
        notes: isEditing ? formData.notes || undefined : undefined,
        services: services
          .filter(s => s.name.trim())
          .map(s => ({
            name: s.name,
            healthUrl: s.healthUrl || undefined,
            notes: s.notes || undefined,
            status: 'online' as const,
          })),
      });
      setFormData({
        name: '',
        ip: '',
        username: 'root',
        password: '',
        status: 'online',
        aliases: '',
        tags: '',
        notes: '',
      });
      setServices([{ name: '', healthUrl: '', notes: '' }]);
    } catch (error) {
      console.error('Submit failed:', error);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/50 backdrop-blur-md"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="glass w-full max-w-2xl rounded-3xl overflow-hidden relative shadow-2xl max-h-[85vh] flex flex-col"
          >
            {/* Header */}
            <div className="p-6 border-b border-brand-border flex items-center justify-between bg-gradient-to-r from-brand-card to-brand-card/80 shrink-0">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-accent to-purple-500 flex items-center justify-center shadow-lg shadow-brand-accent/20">
                  <Server className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold">{editingServer ? '编辑服务器' : '添加新服务器'}</h2>
                  <p className="text-xs text-brand-text-secondary">
                    {editingServer ? '修改服务器信息和配置' : '填写服务器基本信息'}
                  </p>
                </div>
              </div>
              <button onClick={onClose} className="btn-icon text-brand-text-secondary hover:text-brand-text-primary">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-8 space-y-7 overflow-y-auto custom-scrollbar flex-1">
              {/* AI Smart Fill Section */}
              {!isEditing && (
                <div className="space-y-5">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-1 h-4 bg-gradient-to-r from-pink-500 to-rose-500 rounded-full" />
                    <h3 className="text-sm font-bold uppercase tracking-wider text-brand-text-secondary">AI 智能填充</h3>
                  </div>
                  <div className="space-y-3">
                    <textarea
                      value={aiDescription}
                      onChange={e => setAiDescription(e.target.value)}
                      className="input-modern min-h-24 resize-none"
                      placeholder="描述这台服务器的信息，例如：192.168.1.100，用户名 admin，密码 123456，运行 Nginx 和 Docker 服务..."
                    />
                    <button
                      type="button"
                      onClick={handleAiExtract}
                      disabled={isExtracting || !aiDescription.trim()}
                      className="w-full btn-primary flex items-center justify-center gap-2"
                    >
                      {isExtracting ? (
                        <>
                          <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          AI 提取中...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4" />
                          使用 AI 填充
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}

              {/* Basic Info Section */}
              <div className="space-y-5">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-1 h-4 bg-brand-accent rounded-full" />
                  <h3 className="text-sm font-bold uppercase tracking-wider text-brand-text-secondary">基本信息</h3>
                </div>
                <div className="grid grid-cols-2 gap-5">
                  <div className="space-y-2.5">
                    <label className="text-xs font-semibold text-brand-text-secondary uppercase flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-brand-accent" />
                      IP 地址
                    </label>
                    <input
                      required
                      value={formData.ip}
                      onChange={e => setFormData({ ...formData, ip: e.target.value })}
                      className="input-modern"
                      placeholder="192.168.1.100"
                    />
                  </div>
                  {isEditing && (
                    <>
                      <div className="space-y-2.5">
                        <label className="text-xs font-semibold text-brand-text-secondary uppercase flex items-center gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                          服务器名称
                        </label>
                        <input
                          required
                          value={formData.name}
                          onChange={e => setFormData({ ...formData, name: e.target.value })}
                          className="input-modern"
                          placeholder="Production-DB-01"
                        />
                      </div>
                      <div className="space-y-2.5">
                        <label className="text-xs font-semibold text-brand-text-secondary uppercase flex items-center gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-yellow-500" />
                          状态
                        </label>
                        <select
                          value={formData.status}
                          onChange={e => setFormData({ ...formData, status: e.target.value as any })}
                          className="input-modern cursor-pointer"
                        >
                          <option value="online">🟢 在线</option>
                          <option value="offline">🔴 离线</option>
                          <option value="maintenance">🟡 维护中</option>
                        </select>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Credentials Section */}
              <div className="space-y-5">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-1 h-4 bg-green-500 rounded-full" />
                  <h3 className="text-sm font-bold uppercase tracking-wider text-brand-text-secondary">访问凭证</h3>
                </div>
                <div className="grid grid-cols-2 gap-5">
                  <div className="space-y-2.5">
                    <label className="text-xs font-semibold text-brand-text-secondary uppercase flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                      用户名
                    </label>
                    <input
                      required
                      value={formData.username}
                      onChange={e => setFormData({ ...formData, username: e.target.value })}
                      className="input-modern"
                      placeholder="root"
                    />
                  </div>
                  <div className="space-y-2.5">
                    <label className="text-xs font-semibold text-brand-text-secondary uppercase flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
                      密码
                      <span className="text-[10px] normal-case opacity-50">(可选)</span>
                    </label>
                    <input
                      type="text"
                      value={formData.password}
                      onChange={e => setFormData({ ...formData, password: e.target.value })}
                      className="input-modern"
                      placeholder="明文存储，仅供内部使用"
                    />
                  </div>
                </div>
              </div>

              {isEditing && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-1 h-4 bg-yellow-500 rounded-full" />
                    <h3 className="text-sm font-bold uppercase tracking-wider text-brand-text-secondary">备注</h3>
                  </div>
                  <textarea
                    value={formData.notes}
                    onChange={e => setFormData({ ...formData, notes: e.target.value })}
                    className="input-modern min-h-24 resize-none"
                    placeholder="写下这台机器的用途、访问说明或 AI 相关备注..."
                  />
                </div>
              )}

              {/* Services Section */}
              <div className="space-y-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-1 h-4 bg-cyan-500 rounded-full" />
                    <label className="text-sm font-bold uppercase tracking-wider text-brand-text-secondary">服务与健康检查</label>
                  </div>
                  <button
                    type="button"
                    onClick={handleAddServiceField}
                    className="btn-ghost text-brand-accent text-xs flex items-center gap-1.5 hover:bg-brand-accent/10"
                  >
                    <Plus className="w-3.5 h-3.5" /> 添加服务
                  </button>
                </div>

                <div className="space-y-4">
                  {services.map((service, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="glass rounded-2xl p-4 space-y-3"
                    >
                      <div className="flex gap-3 items-start">
                        <div className="flex-1 grid grid-cols-2 gap-3">
                          <div className="space-y-1.5">
                            <span className="text-[10px] font-semibold text-brand-text-secondary uppercase">服务名称</span>
                            <input
                              placeholder="Nginx, Docker, API..."
                              value={service.name}
                              onChange={e => handleServiceChange(index, 'name', e.target.value)}
                              className="input-modern text-sm"
                            />
                          </div>
                          <div className="space-y-1.5">
                            <span className="text-[10px] font-semibold text-brand-text-secondary uppercase">健康检查 URL</span>
                            <input
                              placeholder="https://..."
                              value={service.healthUrl}
                              onChange={e => handleServiceChange(index, 'healthUrl', e.target.value)}
                              className="input-modern text-sm"
                            />
                          </div>
                        </div>
                        {services.length > 1 && (
                          <button
                            type="button"
                            onClick={() => handleRemoveServiceField(index)}
                            className="btn-icon text-brand-text-secondary hover:text-red-500 hover:bg-red-500/10 mt-6"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                      <div className="space-y-1.5">
                        <span className="text-[10px] font-semibold text-brand-text-secondary uppercase">备注（可选）</span>
                        <textarea
                          placeholder="服务用途、端口、配置说明..."
                          value={service.notes || ''}
                          onChange={e => handleServiceChange(index, 'notes', e.target.value)}
                          className="input-modern text-sm min-h-16 resize-none"
                        />
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end gap-3 pt-6 border-t border-brand-border">
                <button
                  type="button"
                  onClick={onClose}
                  disabled={isSubmitting}
                  className="btn-secondary"
                >
                  取消
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn-primary"
                >
                  {isSubmitting ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      保存中...
                    </>
                  ) : editingServer ? '更新服务器' : '添加服务器'}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

function splitCommaValues(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

export function DeleteConfirmModal({ isOpen, onClose, onConfirm, serverName, isDeleting = false }: { isOpen: boolean, onClose: () => void, onConfirm: () => void | Promise<void>, serverName: string, isDeleting?: boolean }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/50 backdrop-blur-md"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="glass w-full max-w-md rounded-3xl overflow-hidden relative shadow-2xl p-8 text-center"
          >
            <div className="w-16 h-16 bg-gradient-to-br from-red-500/20 to-orange-500/10 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-red-500/20 shadow-lg shadow-red-500/10">
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
            <h2 className="text-2xl font-black mb-2">删除服务器？</h2>
            <p className="text-brand-text-secondary mb-8">
              确定要删除 <span className="text-brand-text-primary font-bold">{serverName}</span> 吗？此操作无法撤销。
            </p>
            <div className="flex gap-3">
              <button
                onClick={onClose}
                disabled={isDeleting}
                className="flex-1 btn-secondary"
              >
                取消
              </button>
              <button
                onClick={() => {
                  void onConfirm();
                }}
                disabled={isDeleting}
                className="flex-1 px-6 py-3 bg-red-500 text-white rounded-2xl hover:bg-red-600 hover:shadow-lg hover:shadow-red-500/20 active:scale-[0.98] transition-all text-sm font-bold disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {isDeleting ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin inline-block mr-2" />
                    删除中...
                  </>
                ) : '删除服务器'}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

interface QuickAddModalProps {
  isOpen: boolean;
  onClose: () => void;
  onQuickAdd: (server: ServerPayload) => Promise<void>;
}

export function QuickAddModal({ isOpen, onClose, onQuickAdd }: QuickAddModalProps) {
  const [description, setDescription] = useState('');
  const [isExtracting, setIsExtracting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleExtractAndSave = async () => {
    if (!description.trim() || isExtracting || isSaving) return;

    setIsExtracting(true);
    try {
      const response = await extractServerInfo(description);
      if (response.success && response.data) {
        const data = response.data;

        const payload: ServerPayload = {
          name: data.ip?.trim() || '未命名服务器',
          ip: data.ip || '',
          username: data.username || 'root',
          password: data.password,
          status: 'online',
          aliases: data.aliases || [],
          tags: [],
          notes: data.notes,
          services: (data.services || []).map(s => ({
            name: s.name,
            healthUrl: s.healthUrl,
            status: 'online' as const,
            aliases: [],
            notes: s.notes,
          })),
        };

        setIsExtracting(false);
        setIsSaving(true);

        try {
          await onQuickAdd(payload);
          setDescription('');
          onClose();
        } finally {
          setIsSaving(false);
        }
      }
    } catch (error) {
      console.error('Quick add failed:', error);
    } finally {
      setIsExtracting(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/50 backdrop-blur-md"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="glass w-full max-w-lg rounded-3xl overflow-hidden relative shadow-2xl"
          >
            <div className="p-6 border-b border-brand-border flex items-center justify-between bg-gradient-to-r from-brand-card to-brand-card/80">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-accent to-purple-500 flex items-center justify-center shadow-lg shadow-brand-accent/20">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold">快速录入</h2>
                  <p className="text-xs text-brand-text-secondary">
                    描述服务器信息，AI 自动提取并保存
                  </p>
                </div>
              </div>
              <button onClick={onClose} className="btn-icon text-brand-text-secondary hover:text-brand-text-primary">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div className="space-y-3">
                <label className="text-sm font-bold text-brand-text-secondary uppercase tracking-wider">
                  服务器描述
                </label>
                <textarea
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  className="input-modern min-h-32 resize-none"
                  placeholder="例如：192.168.1.100，用户名 root，密码 password123，运行 Nginx 和 Docker 服务..."
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 btn-secondary"
                >
                  取消
                </button>
                <button
                  type="button"
                  onClick={handleExtractAndSave}
                  disabled={isExtracting || isSaving || !description.trim()}
                  className="flex-1 btn-primary flex items-center justify-center gap-2"
                >
                  {isExtracting ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      AI 提取中...
                    </>
                  ) : isSaving ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      保存中...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      提取并保存
                    </>
                  )}
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
