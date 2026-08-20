import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Order } from '../models/shop';
import { Api } from '../services/api';
import { Icon } from '../shared/icon/icon';
import { peso } from '../utils/format';

@Component({
  selector: 'app-order-confirmation',
  imports: [RouterLink, Icon],
  templateUrl: './order-confirmation.html',
  styleUrl: './order-confirmation.scss',
})
export class OrderConfirmation implements OnInit {
  private readonly api = inject(Api);
  private readonly route = inject(ActivatedRoute);
  readonly order = signal<Order | null>(null);
  readonly missing = signal(false);
  readonly peso = peso;

  ngOnInit() {
    const number = this.route.snapshot.paramMap.get('orderNumber') || '';
    this.api.order(number).subscribe({
      next: (order) => this.order.set(order),
      error: () => this.missing.set(true),
    });
  }
}
