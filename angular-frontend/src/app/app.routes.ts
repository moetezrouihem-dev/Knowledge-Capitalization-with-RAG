import { Routes } from '@angular/router';
import { LoginComponent } from './login.component';
import { RegisterComponent } from './register.component';
import { ChatPageComponent } from './chat-page.component';
import { OAuthCallbackComponent } from './oauth-callback.component';
import { authGuard } from './auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'oauth-callback', component: OAuthCallbackComponent },
  { path: 'chat', component: ChatPageComponent, canActivate: [authGuard] },
  { path: 'chat/:id', component: ChatPageComponent, canActivate: [authGuard] },
  { path: '', redirectTo: '/chat', pathMatch: 'full' },
  { path: '**', redirectTo: '/chat' },
];
