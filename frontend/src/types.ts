export interface Tag {
  id: string;
  name: string;
  color: string;
}

export interface Service {
  name: string;
  healthUrl?: string;
  status: 'online' | 'offline' | 'checking';
  category?: string;
  aliases: string[];
  notes?: string;
}

export interface ServerInfo {
  id: string;
  name: string;
  ip: string;
  username: string;
  password?: string;
  sshKey?: string;
  services: Service[];
  tags: Tag[];
  aliases: string[];
  notes?: string;
  status: 'online' | 'offline' | 'maintenance';
  lastChecked: string;
}

export interface ServiceInput {
  name: string;
  healthUrl?: string;
  status?: Service['status'];
  category?: string;
  aliases: string[];
  notes?: string;
}

export interface ServerPayload {
  name: string;
  ip: string;
  username: string;
  password?: string;
  sshKey?: string;
  tags: Omit<Tag, 'id'>[];
  aliases: string[];
  notes?: string;
  services: ServiceInput[];
  status: ServerInfo['status'];
}

export interface AssistantRecord {
  type: 'server' | 'service';
  serverId: string;
  serverName: string;
  serviceName?: string;
  status: string;
  healthUrl?: string;
  notes?: string;
}

export interface AssistantKnowledge {
  title: string;
  snippet: string;
}

export interface AssistantAnswer {
  summary: string;
  records: AssistantRecord[];
  knowledge: AssistantKnowledge[];
  nextActions: string[];
}

export interface ChatMessage {
  role: 'user' | 'model';
  text: string;
  answer?: AssistantAnswer;
}

export interface ExtractedService {
  name: string;
  healthUrl?: string;
  notes?: string;
}

export interface ExtractedServerInfo {
  ip?: string;
  username?: string;
  password?: string;
  aliases: string[];
  notes?: string;
  services: ExtractedService[];
}
