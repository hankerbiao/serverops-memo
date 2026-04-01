import { useState, useEffect } from 'react';
import { Plus, LayoutGrid, Server, Activity, Layers, Sun, Moon, Sparkles, Settings } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { ServerInfo, ServerPayload, Service } from './types';
import { ServerCard, ServerModal, ServerDetail, ServiceList, DeleteConfirmModal, QuickAddModal } from './components/ServerComponents';
import AIChat from './components/AIChat';
import { cn } from './lib/utils';
import { createServer, deleteServer, fetchServers, updateServer } from './lib/api';

type ActiveTab = 'servers' | 'services' | 'detail';

export default function App() {
  const [servers, setServers] = useState<ServerInfo[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingServer, setEditingServer] = useState<ServerInfo | null>(null);
  const [activeTab, setActiveTab] = useState<ActiveTab>('servers');
  const [selectedServerId, setSelectedServerId] = useState<string | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isQuickAddOpen, setIsQuickAddOpen] = useState(false);

  const query = searchQuery.trim().toLowerCase();
  const filteredServers = servers.filter((server) => {
    if (!query) {
      return true;
    }

    const haystacks = [
      server.name,
      server.ip,
      server.notes || '',
      ...server.aliases,
      ...server.tags.map((tag) => tag.name),
      ...server.services.flatMap((service) => [
        service.name,
        service.category || '',
        service.notes || '',
        service.healthUrl || '',
        ...service.aliases,
      ]),
    ];

    return haystacks.some((value) => value.toLowerCase().includes(query));
  });

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const loadServers = async () => {
    setIsLoading(true);
    try {
      const data = await fetchServers();
      setServers(data);
      setErrorMessage(null);
      if (selectedServerId && !data.some(server => server.id === selectedServerId)) {
        setSelectedServerId(null);
        setActiveTab('servers');
      }
    } catch (error) {
      console.error('Failed to load servers:', error);
      setErrorMessage('无法加载基础设施数据。');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadServers();
  }, []);

  const handleAddServer = async (payload: ServerPayload) => {
    setIsSaving(true);
    try {
      const savedServer = editingServer
        ? await updateServer(editingServer.id, payload)
        : await createServer(payload);

      setServers(prev => {
        if (editingServer) {
          return prev.map(server => server.id === editingServer.id ? savedServer : server);
        }
        return [savedServer, ...prev];
      });
      setErrorMessage(null);
      setIsModalOpen(false);
      setEditingServer(null);
      if (activeTab === 'detail' && editingServer) {
        setSelectedServerId(savedServer.id);
      }
    } catch (error) {
      console.error('Failed to save server:', error);
      setErrorMessage('无法保存服务器更改。');
      throw error;
    } finally {
      setIsSaving(false);
    }
  };

  const handleEditServer = (server: ServerInfo) => {
    setEditingServer(server);
    setIsModalOpen(true);
  };

  const handleDeleteServer = (id: string) => {
    setDeleteConfirmId(id);
  };

  const confirmDelete = async () => {
    if (deleteConfirmId) {
      setIsDeleting(true);
      try {
        await deleteServer(deleteConfirmId);
        setServers(prev => prev.filter(s => s.id !== deleteConfirmId));
        if (selectedServerId === deleteConfirmId) {
          setActiveTab('servers');
          setSelectedServerId(null);
        }
        setErrorMessage(null);
        setDeleteConfirmId(null);
      } catch (error) {
        console.error('Failed to delete server:', error);
        setErrorMessage('无法删除服务器。');
      } finally {
        setIsDeleting(false);
      }
    }
  };

  const handleViewDetail = (id: string) => {
    setSelectedServerId(id);
    setActiveTab('detail');
  };

  const handleRefreshServer = async (serverId: string) => {
    try {
      const updatedServers = await fetchServers();
      setServers(updatedServers);
    } catch (error) {
      console.error('Failed to refresh server:', error);
    }
  };

  const handleApplyFilter = (value: string) => {
    setSearchQuery(value);
    setActiveTab('servers');
  };

  const stats = {
    total: servers.length,
    online: servers.filter(s => s.status === 'online').length,
    offline: servers.filter(s => s.status === 'offline').length,
    maintenance: servers.filter(s => s.status === 'maintenance').length,
  };

  const selectedServer = servers.find(s => s.id === selectedServerId);

  return (
    <div className="min-h-screen pb-20">
      {/* Sidebar / Navigation Rail */}
      <div className="fixed left-0 top-0 bottom-0 w-20 border-r border-brand-border flex flex-col items-center py-6 gap-6 bg-brand-bg/80 backdrop-blur-xl z-40">
        <div className="w-12 h-12 bg-gradient-to-br from-brand-accent to-purple-500 rounded-2xl flex items-center justify-center shadow-lg shadow-brand-accent/30 pulse-glow">
          <Server className="w-6 h-6 text-white" />
        </div>

        <div className="text-[10px] font-bold text-brand-text-secondary text-center leading-tight px-1">
          Server<br/>Ops
        </div>

        <div className="flex flex-col gap-4 flex-1">
          <NavItem
            icon={<Activity className="w-5 h-5" />}
            active={activeTab === 'servers' || activeTab === 'detail'}
            onClick={() => setActiveTab('servers')}
          />
          <NavItem
            icon={<Layers className="w-5 h-5" />}
            active={activeTab === 'services'}
            onClick={() => setActiveTab('services')}
          />
          <NavItem icon={<Settings className="w-5 h-5" />} />
        </div>
        
        <div className="pb-4 flex flex-col items-center gap-4">
          <button 
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            className="w-12 h-12 rounded-xl flex items-center justify-center text-brand-text-secondary hover:text-brand-text-primary hover:bg-brand-border transition-all group relative"
            title={theme === 'light' ? '切换到深色模式' : '切换到浅色模式'}
          >
            {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
            <span className="absolute left-full ml-4 px-2 py-1 bg-brand-card border border-brand-border rounded text-[10px] font-bold opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
              {theme === 'light' ? '深色模式' : '浅色模式'}
            </span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="pl-20 max-w-[1600px] mx-auto p-8">
        <AnimatePresence mode="wait">
          {activeTab === 'servers' && (
            <motion.div
              key="servers"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
                <div>
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-2 h-8 bg-gradient-to-b from-brand-accent to-purple-500 rounded-full" />
                    <h1 className="text-4xl font-black tracking-tight">5000 信息系统开发部服务器备忘录</h1>
                  </div>
                  <p className="text-brand-text-secondary font-medium ml-5">5000信息系统开发部服务器运维管理系统，支持AI智能填充、健康检查和智能问答。</p>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="flex items-center bg-brand-card/80 backdrop-blur-sm border border-brand-border rounded-2xl px-5 py-3 gap-8 shadow-sm">
                    <StatItem label="总计" value={stats.total} />
                    <div className="w-px h-8 bg-brand-border" />
                    <StatItem label="在线" value={stats.online} color="text-green-500" />
                    <div className="w-px h-8 bg-brand-border" />
                    <StatItem label="离线" value={stats.offline} color="text-red-500" />
                  </div>
                  <button
                    onClick={() => setIsQuickAddOpen(true)}
                    className="btn-secondary shadow-lg border-brand-accent/30 text-brand-accent hover:bg-brand-accent/10"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>快速录入</span>
                  </button>
                  <button
                    onClick={() => {
                      setEditingServer(null);
                      setIsModalOpen(true);
                    }}
                    className="btn-primary shadow-lg shadow-brand-accent/20"
                  >
                    <Plus className="w-5 h-5" />
                    <span>添加服务器</span>
                  </button>
                </div>
              </header>

              <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-8">
                <div className="w-full md:w-96">
                  <input
                    type="text"
                    placeholder="搜索服务器、服务、标签..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input-modern"
                  />
                </div>
              </div>

              {errorMessage && (
                <div className="mb-6 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-500">
                  {errorMessage}
                </div>
              )}

              {isLoading ? (
                <div className="py-20 flex flex-col items-center justify-center text-brand-text-secondary">
                  <div className="relative">
                    <div className="w-16 h-16 rounded-3xl bg-brand-border/50 skeleton" />
                    <Server className="absolute inset-0 m-auto w-8 h-8 text-brand-text-secondary animate-pulse" />
                  </div>
                  <p className="text-lg font-medium mt-6">正在加载基础设施数据...</p>
                </div>
              ) : (
                <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {filteredServers.map(server => (
                    <ServerCard
                      key={server.id}
                      server={server}
                      onDelete={handleDeleteServer}
                      onEdit={handleEditServer}
                      onViewDetail={handleViewDetail}
                    />
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'services' && (
            <motion.div
              key="services"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <header className="mb-10">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-2 h-8 bg-gradient-to-b from-green-500 to-cyan-500 rounded-full" />
                  <h1 className="text-4xl font-black tracking-tight">服务目录</h1>
                </div>
                <p className="text-brand-text-secondary font-medium ml-5">运行在您基础设施上的所有服务的完整列表。</p>
              </header>
              <ServiceList servers={servers} />
            </motion.div>
          )}

          {activeTab === 'detail' && selectedServer && (
            <motion.div
              key="detail"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <ServerDetail
                server={selectedServer}
                onEdit={() => handleEditServer(selectedServer)}
                onBack={() => setActiveTab('servers')}
                onRefreshServer={handleRefreshServer}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {filteredServers.length === 0 && activeTab === 'servers' && !isLoading && (
          <div className="py-24 flex flex-col items-center justify-center text-brand-text-secondary">
            <div className="w-20 h-20 rounded-3xl bg-brand-border/30 flex items-center justify-center mb-6">
              <Server className="w-10 h-10 opacity-30" />
            </div>
            <p className="text-lg font-medium mb-2">未找到匹配的服务器</p>
            <p className="text-sm opacity-60">尝试调整搜索条件或添加新服务器</p>
          </div>
        )}
      </main>

      <ServerModal 
        isOpen={isModalOpen} 
        onClose={() => {
          setIsModalOpen(false);
          setEditingServer(null);
        }} 
        onAdd={handleAddServer}
        editingServer={editingServer}
        isSubmitting={isSaving}
      />

      <DeleteConfirmModal
        isOpen={!!deleteConfirmId}
        onClose={() => setDeleteConfirmId(null)}
        onConfirm={confirmDelete}
        serverName={servers.find(s => s.id === deleteConfirmId)?.name || ''}
        isDeleting={isDeleting}
      />

      <QuickAddModal
        isOpen={isQuickAddOpen}
        onClose={() => setIsQuickAddOpen(false)}
        onQuickAdd={handleAddServer}
      />

      <AIChat onOpenServer={handleViewDetail} onApplyFilter={handleApplyFilter} />
    </div>
  );
}

function NavItem({ icon, active = false, onClick }: { icon: React.ReactNode, active?: boolean, onClick?: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-200",
        active
          ? "bg-gradient-to-br from-brand-accent to-purple-500 text-white shadow-lg shadow-brand-accent/30"
          : "text-brand-text-secondary hover:text-brand-text-primary hover:bg-brand-border/60"
      )}
    >
      {icon}
    </button>
  );
}

function StatItem({ label, value, color = "text-brand-text-primary" }: { label: string, value: number, color?: string }) {
  return (
    <div className="flex flex-col items-center px-3">
      <span className="text-[11px] uppercase tracking-widest text-brand-text-secondary font-bold">{label}</span>
      <span className={cn("text-2xl font-black tracking-tight", color)}>{value}</span>
    </div>
  );
}
