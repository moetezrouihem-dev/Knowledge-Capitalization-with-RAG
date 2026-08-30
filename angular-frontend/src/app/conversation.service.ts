import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SourceDto {
  source: string;
  page: string;
}

export interface AskResponse {
  conversationId: number;
  answer: string;
  sources: SourceDto[];
}

export interface ConversationSummary {
  id: number;
  title: string;
  createdAt: string;
}

export interface ConversationMessage {
  role: 'USER' | 'ASSISTANT';
  content: string;
  sources: string | null;
  createdAt: string;
}

export interface ConversationDetail {
  id: number;
  title: string;
  messages: ConversationMessage[];
}

export interface UploadResponse {
  filename: string;
  chunksAdded: number;
  status: string;
}

@Injectable({ providedIn: 'root' })
export class ConversationService {
  private readonly baseUrl = 'http://localhost:8082/api';

  constructor(private http: HttpClient) {}

  ask(question: string, conversationId: number | null): Observable<AskResponse> {
    return this.http.post<AskResponse>(`${this.baseUrl}/ask`, { question, conversationId });
  }

  list(): Observable<ConversationSummary[]> {
    return this.http.get<ConversationSummary[]>(`${this.baseUrl}/conversations`);
  }

  get(id: number): Observable<ConversationDetail> {
    return this.http.get<ConversationDetail>(`${this.baseUrl}/conversations/${id}`);
  }

  uploadDocument(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<UploadResponse>(`${this.baseUrl}/documents/upload`, formData);
  }
}
