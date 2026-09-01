import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from './auth.service';

@Component({
  selector: 'app-oauth-callback',
  standalone: true,
  template: `<p class="oauth-message">Connexion en cours...</p>`,
  styles: [`.oauth-message { text-align: center; margin-top: 3rem; font-family: 'Inter', sans-serif; color: #6b7280; }`],
})
export class OAuthCallbackComponent implements OnInit {
  constructor(private route: ActivatedRoute, private router: Router, private auth: AuthService) {}

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('token');

    if (!token) {
      this.router.navigate(['/login']);
      return;
    }

    this.auth.completeOAuthLogin(token).subscribe({
      next: () => this.router.navigate(['/chat']),
      error: () => this.router.navigate(['/login']),
    });
  }
}
