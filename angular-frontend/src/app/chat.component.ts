import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RagService, AskResponse } from './rag.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css',
})
export class ChatComponent {
  question = '';
  // signal() is Angular's newer reactivity primitive (Angular 16+) —
  // simpler than manually managing change detection for a plain
  // property. Template auto-updates whenever these change.
  loading = signal(false);
  error = signal<string | null>(null);
  result = signal<AskResponse | null>(null);

  constructor(private ragService: RagService) {}

  submit(): void {
    const trimmed = this.question.trim();
    if (!trimmed || this.loading()) {
      return;
    }

    this.loading.set(true);
    this.error.set(null);
    this.result.set(null);

    this.ragService.ask(trimmed).subscribe({
      next: (response) => {
        this.result.set(response);
        this.loading.set(false);
      },
      error: (err) => {
        console.error(err);
        this.error.set(
          'Something went wrong reaching the assistant. Is the Spring Boot backend running on :8080?'
        );
        this.loading.set(false);
      },
    });
  }
}
