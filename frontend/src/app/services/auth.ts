import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { User } from '../models/shop';
import { Api } from './api';
import { CartService } from './cart';

@Injectable({ providedIn: 'root' })
export class Auth {
  private readonly api = inject(Api);
  private readonly cart = inject(CartService);
  private readonly router = inject(Router);
  readonly user = signal<User | null>(null);
  readonly isLoggedIn = computed(() => !!this.user());

  restore() {
    if (!localStorage.getItem('sariwa_token')) {
      return;
    }
    this.api.me().subscribe({
      next: (user) => {
        this.user.set(user);
        this.cart.refresh();
      },
      error: () => this.logout(false),
    });
  }

  setSession(token: string, user: User) {
    localStorage.setItem('sariwa_token', token);
    this.user.set(user);
    this.cart.refresh();
  }

  logout(redirect = true) {
    localStorage.removeItem('sariwa_token');
    this.user.set(null);
    if (redirect) {
      this.router.navigateByUrl('/');
    }
  }
}
