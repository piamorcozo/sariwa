import { Component, HostListener, inject, OnInit, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { NavigationEnd, Router, RouterLink, RouterLinkActive } from '@angular/router';
import { filter } from 'rxjs/operators';
import { Occasion, ProductCard } from '../../models/shop';
import { Api } from '../../services/api';
import { Auth } from '../../services/auth';
import { CartService } from '../../services/cart';
import { Icon } from '../icon/icon';

@Component({
  selector: 'app-navbar',
  imports: [RouterLink, RouterLinkActive, ReactiveFormsModule, Icon],
  templateUrl: './navbar.html',
  styleUrl: './navbar.scss',
})
export class Navbar implements OnInit {
  private readonly api = inject(Api);
  private readonly router = inject(Router);
  readonly auth = inject(Auth);
  readonly cart = inject(CartService);

  readonly menuOpen = signal(false);
  readonly searchOpen = signal(false);
  readonly query = new FormControl('', { nonNullable: true });
  readonly results = signal<ProductCard[]>([]);
  readonly occasions = signal<Occasion[]>([]);

  ngOnInit() {
    this.api.occasions().subscribe((rows) => this.occasions.set(rows));
    this.router.events.pipe(filter((event) => event instanceof NavigationEnd)).subscribe(() => {
      this.menuOpen.set(false);
      this.searchOpen.set(false);
    });
    this.query.valueChanges.subscribe((value) => {
      const q = value.trim();
      if (q.length < 2) {
        this.results.set([]);
        return;
      }
      this.api.products({ q }).subscribe((rows) => this.results.set(rows.slice(0, 6)));
    });
  }

  toggleMenu() {
    this.menuOpen.update((open) => !open);
    this.searchOpen.set(false);
  }

  toggleSearch() {
    this.searchOpen.update((open) => !open);
    this.menuOpen.set(false);
    if (this.searchOpen()) {
      setTimeout(() => document.getElementById('nav-search')?.focus(), 50);
    }
  }

  goSearch(event: Event) {
    event.preventDefault();
    const q = this.query.value.trim();
    if (!q) {
      return;
    }
    this.router.navigate(['/shop'], { queryParams: { q } });
    this.searchOpen.set(false);
  }

  @HostListener('document:keydown.escape')
  onEscape() {
    this.searchOpen.set(false);
    this.menuOpen.set(false);
  }
}
