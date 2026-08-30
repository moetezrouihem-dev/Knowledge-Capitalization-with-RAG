import { Component, EventEmitter, Input, OnInit, Output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';
import { ConversationService, ConversationSummary } from './conversation.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css',
})
export class SidebarComponent implements OnInit {
  @Input() activeConversationId: number | null = null;
  @Output() selectConversation = new EventEmitter<number>();
  @Output() newConversation = new EventEmitter<void>();

  conversations = signal<ConversationSummary[]>([]);
  uploading = signal(false);
  uploadMessage = signal<string | null>(null);
  uploadError = signal(false);

  constructor(
    private conversationService: ConversationService,
    public auth: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.conversationService.list().subscribe({
      next: (list) => this.conversations.set(list),
      error: (err) => console.error('Failed to load conversations', err),
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.uploading.set(true);
    this.uploadMessage.set(null);
    this.uploadError.set(false);

    this.conversationService.uploadDocument(file).subscribe({
      next: (res) => {
        this.uploading.set(false);
        this.uploadError.set(false);
        this.uploadMessage.set(`"${res.filename}" ajoute (${res.chunksAdded} sections).`);
      },
      error: (err) => {
        this.uploading.set(false);
        this.uploadError.set(true);
        this.uploadMessage.set(
          err.error?.message || "Echec de l'ajout du document."
        );
      },
    });

    input.value = '';
  }

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
