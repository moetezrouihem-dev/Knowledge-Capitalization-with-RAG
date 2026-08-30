// app.component.ts — replace your generated one with this (or just add
// ChatComponent to the imports array and <app-chat /> to the template
// if you'd rather keep the rest of the generated boilerplate).

import { Component } from '@angular/core';
import { ChatComponent } from './chat.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ChatComponent],
  template: `<app-chat />`,
})
export class AppComponent {}
