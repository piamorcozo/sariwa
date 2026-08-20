import { Component, inject, OnInit, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { FlowerType, Occasion, ProductCard } from '../models/shop';
import { Api } from '../services/api';
import { Icon } from '../shared/icon/icon';
import { ProductCardComponent } from '../shared/product-card/product-card';

@Component({
  selector: 'app-shop',
  imports: [ReactiveFormsModule, Icon, ProductCardComponent],
  templateUrl: './shop.html',
  styleUrl: './shop.scss',
})
export class Shop implements OnInit {
  private readonly api = inject(Api);
  private readonly route = inject(ActivatedRoute);

  readonly occasions = signal<Occasion[]>([]);
  readonly types = signal<FlowerType[]>([]);
  readonly products = signal<ProductCard[]>([]);
  readonly occasion = signal('all');
  readonly visibleCount = signal(6);
  readonly query = new FormControl('', { nonNullable: true });
  readonly type = new FormControl('all', { nonNullable: true });
  readonly price = new FormControl('all', { nonNullable: true });
  readonly sort = new FormControl('featured', { nonNullable: true });

  ngOnInit() {
    this.api.occasions().subscribe((rows) => this.occasions.set(rows));
    this.api.flowerTypes().subscribe((rows) => this.types.set(rows));
    this.route.queryParamMap.subscribe((params) => {
      const q = params.get('q') || '';
      const occasion = params.get('occasion') || 'all';
      this.query.setValue(q, { emitEvent: false });
      this.occasion.set(occasion);
      this.load();
    });
    this.query.valueChanges.subscribe(() => this.reload());
    this.type.valueChanges.subscribe(() => this.reload());
    this.price.valueChanges.subscribe(() => this.reload());
    this.sort.valueChanges.subscribe(() => this.reload());
  }

  load() {
    const price = this.price.value;
    const filters: Record<string, string> = {
      occasion: this.occasion(),
      type: this.type.value,
      q: this.query.value,
      sort: this.sort.value,
    };
    if (price === '0-1200') {
      filters['price_max'] = '1200';
    } else if (price === '1200-1700') {
      filters['price_min'] = '1200';
      filters['price_max'] = '1700';
    } else if (price === '1700-999999') {
      filters['price_min'] = '1700';
    }
    this.api.products(filters).subscribe((rows) => this.products.set(rows));
  }

  reload() {
    this.visibleCount.set(6);
    this.load();
  }

  setOccasion(slug: string) {
    this.occasion.set(slug);
    this.reload();
  }

  shown() {
    return this.products().slice(0, this.visibleCount());
  }

  clear() {
    this.occasion.set('all');
    this.query.setValue('');
    this.type.setValue('all');
    this.price.setValue('all');
    this.sort.setValue('featured');
    this.reload();
  }
}
