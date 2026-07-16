const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("z1_token");
}

export function setToken(token: string): void {
  localStorage.setItem("z1_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("z1_token");
}

export function isAuthenticated(): boolean {
  return Boolean(getToken());
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: ["Bearer", token].join(" ") } : {}),
    ...(init.headers ?? {}),
  };

  const res = await fetch(API_BASE + path, { ...init, headers });

  if (res.status === 401) {
    clearToken();
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || `HTTP ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function login(username: string, password: string): Promise<string> {
  const data = await request<{ access_token: string }>("/auth/token", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  return data.access_token;
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export async function getDashboardSummary(): Promise<Record<string, unknown>> {
  return request("/dashboard/summary");
}

// ---------------------------------------------------------------------------
// Electra
// ---------------------------------------------------------------------------

export interface WindFarm {
  id: number;
  name: string;
  location: string;
  capacity_kw: number;
  status: string;
  latitude?: number;
  longitude?: number;
  created_at: string;
}

export interface ElectraSummary {
  total_farms: number;
  active_farms: number;
  total_capacity_kw: number;
  total_production_kwh: number;
  active_contracts: number;
  estimated_revenue_eur: number;
}

export const electra = {
  listFarms: () => request<WindFarm[]>("/electra/wind-farms"),
  createFarm: (data: Partial<WindFarm>) =>
    request<WindFarm>("/electra/wind-farms", { method: "POST", body: JSON.stringify(data) }),
  updateFarm: (id: number, data: Partial<WindFarm>) =>
    request<WindFarm>(`/electra/wind-farms/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteFarm: (id: number) =>
    request<void>(`/electra/wind-farms/${id}`, { method: "DELETE" }),
  summary: () => request<ElectraSummary>("/electra/summary"),
};

// ---------------------------------------------------------------------------
// Gaia
// ---------------------------------------------------------------------------

export interface Property {
  id: number;
  name: string;
  address: string;
  city: string;
  property_type: string;
  area_sqm: number;
  purchase_price?: number;
  monthly_rent?: number;
  status: string;
  latitude?: number;
  longitude?: number;
  created_at: string;
}

export interface GaiaSummary {
  total_properties: number;
  rented_properties: number;
  available_properties: number;
  total_rent_income: number;
  open_maintenance_requests: number;
}

export const gaia = {
  listProperties: () => request<Property[]>("/gaia/properties"),
  createProperty: (data: Partial<Property>) =>
    request<Property>("/gaia/properties", { method: "POST", body: JSON.stringify(data) }),
  updateProperty: (id: number, data: Partial<Property>) =>
    request<Property>(`/gaia/properties/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteProperty: (id: number) =>
    request<void>(`/gaia/properties/${id}`, { method: "DELETE" }),
  summary: () => request<GaiaSummary>("/gaia/summary"),
};

// ---------------------------------------------------------------------------
// Fortuna
// ---------------------------------------------------------------------------

export interface Transaction {
  id: number;
  transaction_date: string;
  description: string;
  amount: number;
  transaction_type: "income" | "expense";
  category_id?: number;
  created_at: string;
}

export interface FortunaMonthlyBreakdown {
  year: number;
  month: number;
  income: number;
  expenses: number;
  profit: number;
}

export interface FortunaSummary {
  total_income: number;
  total_expenses: number;
  net_profit: number;
  transaction_count: number;
  monthly: FortunaMonthlyBreakdown[];
}

export const fortuna = {
  listTransactions: () => request<Transaction[]>("/fortuna/transactions"),
  createTransaction: (data: Partial<Transaction>) =>
    request<Transaction>("/fortuna/transactions", { method: "POST", body: JSON.stringify(data) }),
  deleteTransaction: (id: number) =>
    request<void>(`/fortuna/transactions/${id}`, { method: "DELETE" }),
  summary: () => request<FortunaSummary>("/fortuna/summary"),
};

// ---------------------------------------------------------------------------
// Themis
// ---------------------------------------------------------------------------

export interface LegalContract {
  id: number;
  title: string;
  counterparty: string;
  contract_type: string;
  status: string;
  start_date?: string;
  end_date?: string;
  value?: number;
  notes?: string;
  created_at: string;
}

export interface ThemisSummary {
  total_contracts: number;
  active_contracts: number;
  expiring_soon: number;
  pending_deadlines: number;
  overdue_deadlines: number;
  total_contract_value: number;
}

export const themis = {
  listContracts: () => request<LegalContract[]>("/themis/contracts"),
  createContract: (data: Partial<LegalContract>) =>
    request<LegalContract>("/themis/contracts", { method: "POST", body: JSON.stringify(data) }),
  deleteContract: (id: number) =>
    request<void>(`/themis/contracts/${id}`, { method: "DELETE" }),
  summary: () => request<ThemisSummary>("/themis/summary"),
};

// ---------------------------------------------------------------------------
// Diplomatia
// ---------------------------------------------------------------------------

export interface DiplomaticDocument {
  id: number;
  title: string;
  language: string;
  document_type: string;
  content: string;
  tags?: string;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface DiplomatiaSummary {
  total_documents: number;
  archived_documents: number;
  active_documents: number;
  languages: string[];
  total_correspondence: number;
  pending_correspondence: number;
}

export const diplomatia = {
  listDocuments: (archived?: boolean) => {
    const q = archived !== undefined ? `?archived=${archived}` : "";
    return request<DiplomaticDocument[]>(`/diplomatia/documents${q}`);
  },
  createDocument: (data: Partial<DiplomaticDocument>) =>
    request<DiplomaticDocument>("/diplomatia/documents", { method: "POST", body: JSON.stringify(data) }),
  deleteDocument: (id: number) =>
    request<void>(`/diplomatia/documents/${id}`, { method: "DELETE" }),
  archiveDocument: (id: number) =>
    request<DiplomaticDocument>(`/diplomatia/documents/${id}/archive`, { method: "POST" }),
  summary: () => request<DiplomatiaSummary>("/diplomatia/summary"),
};

// ---------------------------------------------------------------------------
// Astraea
// ---------------------------------------------------------------------------

export interface AuditLog {
  id: number;
  timestamp: string;
  user: string;
  action: string;
  resource: string;
  resource_id?: string;
  details?: string;
  ip_address?: string;
  success: boolean;
}

export interface AstraeaSummary {
  total_audit_entries: number;
  failed_actions: number;
  active_permissions: number;
  total_backups: number;
  last_backup_at?: string;
}

export const astraea = {
  listAuditLogs: () => request<AuditLog[]>("/astraea/audit-logs"),
  summary: () => request<AstraeaSummary>("/astraea/summary"),
  triggerBackup: (filename: string) =>
    request("/astraea/backups", { method: "POST", body: JSON.stringify({ filename }) }),
};

// ---------------------------------------------------------------------------
// Zoe
// ---------------------------------------------------------------------------

export interface AgentTask {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  assigned_module?: string;
  due_date?: string;
  created_at: string;
  completed_at?: string;
}

export interface ZoeDispatchResponse {
  run_id: number;
  routed_to: string;
  response: string;
  duration_ms: number;
}

export interface ZoeSummary {
  total_tasks: number;
  open_tasks: number;
  completed_tasks: number;
  total_runs: number;
  memory_entries: number;
}

export const zoe = {
  listTasks: () => request<AgentTask[]>("/zoe/tasks"),
  createTask: (data: Partial<AgentTask>) =>
    request<AgentTask>("/zoe/tasks", { method: "POST", body: JSON.stringify(data) }),
  dispatch: (prompt: string) =>
    request<ZoeDispatchResponse>("/zoe/dispatch", {
      method: "POST",
      body: JSON.stringify({ prompt }),
    }),
  summary: () => request<ZoeSummary>("/zoe/summary"),
};
