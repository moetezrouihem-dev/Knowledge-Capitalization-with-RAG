import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SourceDto {
  source: string;
  page: string;
}

export interface AskResponse {
  answer: string;
  sources: SourceDto[];
}

@Injectable({
  providedIn: 'root', // one shared instance for the whole app, no need to add to a module's providers array
})
export class RagService {
  // Spring Boot's address, NOT FastAPI's — Angular never talks to
  // FastAPI directly, matching the architecture diagram.
  private readonly baseUrl = 'http://localhost:8082/api';
  constructor(private http: HttpClient) {}

  ask(question: string): Observable<AskResponse> {
    return this.http.post<AskResponse>(`${this.baseUrl}/ask`, { question });
  }
}
