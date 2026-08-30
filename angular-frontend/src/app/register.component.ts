import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from './auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './auth-page.css',
})
export class RegisterComponent {
  email = '';
  password = '';
  error = signal<string | null>(null);
  loading = signal(false);

  constructor(private auth: AuthService, private router: Router) {}

  submit(): void {
    if (!this.email.trim() || this.password.length < 8) return;
    this.loading.set(true);
    this.error.set(null);

    this.auth.register(this.email.trim(), this.password).subscribe({
      next: () => {
        this.loading.set(false);
        this.router.navigate(['/chat']);
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err.status === 409 ? 'Un compte existe déjà avec cet email.' : 'Une erreur est survenue.');
      },
    });
  }
}
