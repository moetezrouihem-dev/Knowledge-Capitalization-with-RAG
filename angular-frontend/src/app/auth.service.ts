import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

interface AuthResponse {
  token: string;
  email: string;
}

interface MeResponse {
  email: string;
}

const TOKEN_KEY = 'sfm_token';
const EMAIL_KEY = 'sfm_email';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly baseUrl = 'http://localhost:8082/api/auth';
  private readonly backendRoot = 'http://localhost:8082';

  currentEmail = signal<string | null>(localStorage.getItem(EMAIL_KEY));

  constructor(private http: HttpClient) {}

  register(email: string, password: string): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.baseUrl}/register`, { email, password })
      .pipe(tap((res) => this.storeSession(res.token, res.email)));
  }

  login(email: string, password: string): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.baseUrl}/login`, { email, password })
      .pipe(tap((res) => this.storeSession(res.token, res.email)));
  }

  loginWithGoogle(): void {
    window.location.href = `${this.backendRoot}/oauth2/authorization/google`;
  }

  completeOAuthLogin(token: string): Observable<MeResponse> {
    localStorage.setItem(TOKEN_KEY, token);
    return this.http.get<MeResponse>(`${this.baseUrl}/me`).pipe(
      tap((res) => {
        localStorage.setItem(EMAIL_KEY, res.email);
        this.currentEmail.set(res.email);
      })
    );
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EMAIL_KEY);
    this.currentEmail.set(null);
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  isLoggedIn(): boolean {
    return this.getToken() !== null;
  }

  private storeSession(token: string, email: string): void {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(EMAIL_KEY, email);
    this.currentEmail.set(email);
  }
}
