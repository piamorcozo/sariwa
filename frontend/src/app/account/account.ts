import { Component, inject, OnInit, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { Order, ProductCard } from '../models/shop';
import { Api } from '../services/api';
import { Auth } from '../services/auth';
import { Icon } from '../shared/icon/icon';
import { ProductCardComponent } from '../shared/product-card/product-card';
import { peso } from '../utils/format';

@Component({
  selector: 'app-account',
  imports: [RouterLink, Icon, ProductCardComponent],
  templateUrl: './account.html',
  styleUrl: './account.scss',
})
export class Account implements OnInit {
  readonly auth = inject(Auth);
  private readonly api = inject(Api);
  private readonly router = inject(Router);
  readonly orders = signal<Order[]>([]);
  readonly favorites = signal<ProductCard[]>([]);
  readonly peso = peso;

  ngOnInit() {
    if (!localStorage.getItem('sariwa_token')) {
      this.router.navigateByUrl('/login');
      return;
    }
    this.api.myOrders().subscribe((rows) => this.orders.set(rows));
    this.api.favorites().subscribe((rows) => this.favorites.set(rows));
  }

  logout() {
    this.auth.logout();
  }
}
