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
  providedIn: 'root',
})
export class RagService {

  private readonly baseUrl = 'http://localhost:8082/api';
  constructor(private http: HttpClient) {}

  ask(question: string): Observable<AskResponse> {
    return this.http.post<AskResponse>(`${this.baseUrl}/ask`, { question });
  }
}
