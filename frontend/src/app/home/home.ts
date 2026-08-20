import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Occasion, ProductCard } from '../models/shop';
import { Api } from '../services/api';
import { Icon } from '../shared/icon/icon';
import { OccasionShowcase } from '../shared/occasion-showcase/occasion-showcase';
import { ProductCardComponent } from '../shared/product-card/product-card';

import { Testimonials } from '../shared/testimonials/testimonials';
import { Chatbot } from '../shared/chatbot/chatbot';

@Component({
  selector: 'app-home',
  imports: [RouterLink, Icon, OccasionShowcase, ProductCardComponent, Testimonials, Chatbot],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home implements OnInit {
  private readonly api = inject(Api);
  readonly occasions = signal<Occasion[]>([]);
  readonly products = signal<ProductCard[]>([]);
  readonly filter = signal('all');

  ngOnInit() {
    this.api.occasions().subscribe((rows) => this.occasions.set(rows));
    this.api.products().subscribe((rows) => this.products.set(rows));
  }

  visible() {
    const filter = this.filter();
    const list = this.products();
    if (filter === 'all') {
      return list.filter((item) => item.featured).concat(list.filter((item) => !item.featured)).slice(0, 8);
    }
    return list.filter((item) => item.occasion_slugs.includes(filter)).slice(0, 8);
  }

  setFilter(slug: string) {
    this.filter.set(slug);
  }
}
