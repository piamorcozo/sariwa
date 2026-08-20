import { Injectable, computed, inject, signal } from '@angular/core';
import { Cart } from '../models/shop';
import { Api } from './api';
import { Toast } from './toast';

const emptyCart: Cart = {
  id: 0,
  items: [],
  subtotal: 0,
  delivery_fee: 0,
  discount: 0,
  total: 0,
  promo_code: null,
  promo_message: null,
};

@Injectable({ providedIn: 'root' })
export class CartService {
  private readonly api = inject(Api);
  private readonly toast = inject(Toast);
  readonly cart = signal<Cart>(emptyCart);
  readonly count = computed(() => this.cart().items.reduce((sum, item) => sum + item.quantity, 0));

  refresh() {
    this.api.cart().subscribe((cart) => this.cart.set(cart));
  }

  add(productId: number, sizeId: number, quantity = 1, name?: string) {
    this.api.addToCart(productId, sizeId, quantity).subscribe({
      next: (cart) => {
        this.cart.set(cart);
        this.toast.show(name ? `${name} is in your cart.` : 'Added to cart.');
      },
      error: () => this.toast.show('Could not add that just now. Try again.', 'error'),
    });
  }

  update(itemId: number, quantity: number) {
    this.api.updateCartItem(itemId, quantity).subscribe((cart) => this.cart.set(cart));
  }

  remove(itemId: number) {
    this.api.removeCartItem(itemId).subscribe((cart) => this.cart.set(cart));
  }

  applyPromo(code: string, onError?: (message: string) => void) {
    this.api.applyPromo(code).subscribe({
      next: (cart) => this.cart.set(cart),
      error: (err) => onError?.(err.error?.detail || 'That code does not look right.'),
    });
  }
}
