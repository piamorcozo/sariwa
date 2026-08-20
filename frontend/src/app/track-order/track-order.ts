import { Component, inject, OnInit, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { Order } from '../models/shop';
import { Api } from '../services/api';
import { Icon } from '../shared/icon/icon';
import { peso } from '../utils/format';

@Component({
  selector: 'app-track-order',
  imports: [ReactiveFormsModule, Icon],
  templateUrl: './track-order.html',
  styleUrl: './track-order.scss',
})
export class TrackOrder implements OnInit {
  private readonly api = inject(Api);
  private readonly route = inject(ActivatedRoute);
  readonly query = new FormControl('', { nonNullable: true });
  readonly order = signal<Order | null>(null);
  readonly error = signal('');
  readonly peso = peso;

  ngOnInit() {
    const initial = this.route.snapshot.queryParamMap.get('order');
    if (initial) {
      this.query.setValue(initial);
      this.lookup();
    }
  }

  lookup() {
    const number = this.query.value.trim().toUpperCase();
    this.error.set('');
    this.order.set(null);
    if (!number) {
      this.error.set('Enter an order number, like SW-48213.');
      return;
    }
    this.api.order(number).subscribe({
      next: (order) => this.order.set(order),
      error: () => this.error.set("We couldn't find that order number."),
    });
  }
}
