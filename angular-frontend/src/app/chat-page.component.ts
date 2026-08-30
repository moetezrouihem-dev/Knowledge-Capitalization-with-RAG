import { AfterViewChecked, Component, ElementRef, ViewChild, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { SidebarComponent } from './sidebar.component';
import { ConversationService, ConversationMessage } from './conversation.service';

interface DisplayMessage {
  role: 'USER' | 'ASSISTANT';
  content: string;
  sources: string | null;
}

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [CommonModule, FormsModule, SidebarComponent],
  templateUrl: './chat-page.component.html',
  styleUrl: './chat-page.component.css',
})
export class ChatPageComponent implements AfterViewChecked {
  @ViewChild('threadEl') threadEl!: ElementRef<HTMLElement>;

  conversationId: number | null = null;
  messages = signal<DisplayMessage[]>([]);
  question = '';
  loading = signal(false);
  error = signal<string | null>(null);

  suggestionChips = [
    "Qu'est-ce que SFM-PQ-001 ?",
    "Quels documents couvrent la clause ISO 8.2 ?",
    "Quels sont les engagements qualité de SFM Technologies ?",
  ];

  private shouldScroll = false;

  constructor(
    private conversationService: ConversationService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.route.paramMap.subscribe((params) => {
      const idParam = params.get('id');
      if (idParam) {
        this.conversationId = Number(idParam);
        this.loadConversation(this.conversationId);
      } else {
        this.conversationId = null;
        this.messages.set([]);
      }
    });
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll && this.threadEl) {
      this.threadEl.nativeElement.scrollTop = this.threadEl.nativeElement.scrollHeight;
      this.shouldScroll = false;
    }
  }

  loadConversation(id: number): void {
    this.conversationService.get(id).subscribe({
      next: (detail) => {
        this.messages.set(
          detail.messages.map((m: ConversationMessage) => ({
            role: m.role,
            content: m.content,
            sources: m.sources,
          }))
        );
        this.shouldScroll = true;
      },
      error: () => this.error.set('Conversation introuvable.'),
    });
  }

  onNewConversation(): void {
    this.router.navigate(['/chat']);
  }

  onSelectConversation(id: number): void {
    this.router.navigate(['/chat', id]);
  }

  askSuggestion(text: string): void {
    this.question = text;
    this.submit();
  }

  submit(): void {
    const trimmed = this.question.trim();
    if (!trimmed || this.loading()) return;

    this.messages.update((m) => [...m, { role: 'USER', content: trimmed, sources: null }]);
    this.question = '';
    this.loading.set(true);
    this.error.set(null);
    this.shouldScroll = true;

    this.conversationService.ask(trimmed, this.conversationId).subscribe({
      next: (res) => {
        this.messages.update((m) => [
          ...m,
          { role: 'ASSISTANT', content: res.answer, sources: res.sources.map((s) => s.source).join(', ') },
        ]);
        this.loading.set(false);
        this.shouldScroll = true;

        if (this.conversationId === null) {
          this.conversationId = res.conversationId;
          this.router.navigate(['/chat', res.conversationId], { replaceUrl: true });
        }
      },
      error: () => {
        this.loading.set(false);
        this.error.set("Impossible de contacter l'assistant.");
      },
    });
  }
}