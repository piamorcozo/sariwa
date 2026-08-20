import { Component, inject, input, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ProductCard } from '../../models/shop';
import { Auth } from '../../services/auth';
import { Api } from '../../services/api';
import { CartService } from '../../services/cart';
import { Toast } from '../../services/toast';
import { peso } from '../../utils/format';
import { Icon } from '../icon/icon';

@Component({
  selector: 'app-product-card',
  imports: [RouterLink, Icon],
  templateUrl: './product-card.html',
  styleUrl: './product-card.scss',
})
export class ProductCardComponent {
  readonly product = input.required<ProductCard>();
  private readonly cart = inject(CartService);
  private readonly auth = inject(Auth);
  private readonly api = inject(Api);
  private readonly toast = inject(Toast);
  readonly peso = peso;
  readonly heartBurst = signal(false);

  add(event: Event) {
    event.preventDefault();
    event.stopPropagation();
    this.cart.add(this.product().id, this.product().default_size_id, 1, this.product().name);
  }

  favorite(event: Event) {
    event.preventDefault();
    event.stopPropagation();
    if (!this.auth.isLoggedIn()) {
      this.toast.show('Sign in to save favorites.', 'error');
      return;
    }
    this.api.toggleFavorite(this.product().id).subscribe((res) => {
      this.product().favorited = res.favorited;
      this.heartBurst.set(res.favorited);
    });
  }
}
