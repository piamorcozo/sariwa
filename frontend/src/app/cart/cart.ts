import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CartService } from '../services/cart';
import { Icon } from '../shared/icon/icon';
import { peso } from '../utils/format';

@Component({
  selector: 'app-cart',
  imports: [RouterLink, Icon],
  templateUrl: './cart.html',
  styleUrl: './cart.scss',
})
export class Cart {
  readonly cart = inject(CartService);
  readonly peso = peso;

  dec(id: number, quantity: number) {
    this.cart.update(id, Math.max(1, quantity - 1));
  }
}
