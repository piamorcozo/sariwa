import { Component, ElementRef, inject, OnInit, signal, viewChild } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { DeliverySlot, ProductCard, ProductDetail, ProductSize, SameDay } from '../models/shop';
import { Api } from '../services/api';
import { CartService } from '../services/cart';
import { Icon } from '../shared/icon/icon';
import { ProductCardComponent } from '../shared/product-card/product-card';
import {
  addIsoDays,
  isoDayNum,
  isoMonth,
  isoWeekday,
  loadDeliveryPref,
  manilaTodayIso,
  num,
  peso,
  saveDeliveryPref,
} from '../utils/format';

export interface DateChip {
  iso: string;
  month: string;
  day: number;
  caption: string;
  disabled: boolean;
}

@Component({
  selector: 'app-product-details',
  imports: [RouterLink, Icon, ProductCardComponent],
  templateUrl: './product-details.html',
  styleUrl: './product-details.scss',
})
export class ProductDetails implements OnInit {
  private readonly api = inject(Api);
  private readonly route = inject(ActivatedRoute);
  private readonly cart = inject(CartService);
  private readonly calendarInput = viewChild<ElementRef<HTMLInputElement>>('calendarInput');

  readonly product = signal<ProductDetail | null>(null);
  readonly similar = signal<ProductCard[]>([]);
  readonly sameDay = signal<SameDay | null>(null);
  readonly slots = signal<DeliverySlot[]>([]);
  readonly dates = signal<DateChip[]>([]);
  readonly size = signal<ProductSize | null>(null);
  readonly qty = signal(1);
  readonly imageIndex = signal(0);
  readonly openPanel = signal('included');
  readonly reviewsOpen = signal(true);
  readonly added = signal(false);
  readonly selectedDate = signal('');
  readonly selectedSlot = signal<number | null>(null);
  readonly customDate = signal(false);
  readonly peso = peso;
  readonly num = num;

  ngOnInit() {
    this.buildDates(true);
    this.api.sameDay().subscribe((info) => {
      this.sameDay.set(info);
      this.buildDates(info.eligible);
    });
    this.api.slots().subscribe((rows) => {
      this.slots.set(rows);
      const saved = loadDeliveryPref();
      const match = saved && rows.some((row) => row.id === saved.slotId);
      this.selectedSlot.set(match ? saved!.slotId : rows[0]?.id ?? null);
    });
    this.route.paramMap.subscribe((params) => {
      const slug = params.get('slug') || '';
      this.api.product(slug).subscribe((product) => {
        this.product.set(product);
        this.size.set(product.sizes.find((item) => item.is_default) || product.sizes[0]);
        this.qty.set(1);
        this.imageIndex.set(0);
        this.added.set(false);
      });
      this.api.similar(slug).subscribe((rows) => this.similar.set(rows));
    });
  }

  buildDates(todayOk: boolean) {
    const today = manilaTodayIso();
    const saved = loadDeliveryPref();
    const chips: DateChip[] = [0, 1, 2].map((offset) => {
      const iso = addIsoDays(today, offset);
      const caption =
        offset === 0 ? 'TODAY' : offset === 1 ? 'TOMORROW' : isoWeekday(iso).toUpperCase();
      return {
        iso,
        month: isoMonth(iso),
        day: isoDayNum(iso),
        caption,
        disabled: offset === 0 && !todayOk,
      };
    });
    this.dates.set(chips);

    if (saved?.date && saved.date >= (todayOk ? today : addIsoDays(today, 1))) {
      this.selectedDate.set(saved.date);
      this.customDate.set(!chips.some((chip) => chip.iso === saved.date));
      return;
    }
    const first = chips.find((chip) => !chip.disabled);
    this.selectedDate.set(first?.iso || addIsoDays(today, 1));
    this.customDate.set(false);
  }

  pickDate(chip: DateChip) {
    if (chip.disabled) {
      return;
    }
    this.selectedDate.set(chip.iso);
    this.customDate.set(false);
    this.persist();
  }

  openCalendar() {
    const input = this.calendarInput()?.nativeElement;
    if (!input) {
      return;
    }
    if (typeof input.showPicker === 'function') {
      input.showPicker();
    } else {
      input.click();
    }
  }

  onCalendar(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    if (!value) {
      return;
    }
    const today = manilaTodayIso();
    const min = this.sameDay()?.eligible ? today : addIsoDays(today, 1);
    if (value < min) {
      return;
    }
    this.selectedDate.set(value);
    this.customDate.set(!this.dates().some((chip) => chip.iso === value));
    this.persist();
  }

  pickSlot(id: number) {
    this.selectedSlot.set(id);
    this.persist();
  }

  persist() {
    const slot = this.selectedSlot();
    if (this.selectedDate() && slot) {
      saveDeliveryPref(this.selectedDate(), slot);
    }
  }

  calendarMin() {
    const today = manilaTodayIso();
    return this.sameDay()?.eligible ? today : addIsoDays(today, 1);
  }

  calendarCaption() {
    if (!this.customDate()) {
      return 'CALENDAR';
    }
    return isoWeekday(this.selectedDate()).toUpperCase();
  }

  calendarMonth() {
    if (!this.customDate()) {
      return '';
    }
    return `${isoMonth(this.selectedDate())} ${isoDayNum(this.selectedDate())}`;
  }

  selectedSlotName() {
    return this.slots().find((slot) => slot.id === this.selectedSlot())?.name || '';
  }

  selectedDateLabel() {
    const iso = this.selectedDate();
    if (!iso) {
      return '';
    }
    const chip = this.dates().find((item) => item.iso === iso);
    if (chip?.caption === 'TODAY' || chip?.caption === 'TOMORROW') {
      return chip.caption.charAt(0) + chip.caption.slice(1).toLowerCase();
    }
    return `${isoMonth(iso)} ${isoDayNum(iso)}`;
  }

  pickSize(size: ProductSize) {
    this.size.set(size);
  }

  inc() {
    this.qty.update((value) => value + 1);
  }

  dec() {
    this.qty.update((value) => Math.max(1, value - 1));
  }

  add() {
    const product = this.product();
    const size = this.size();
    if (!product || !size) {
      return;
    }
    this.persist();
    this.cart.add(product.id, size.id, this.qty(), product.name);
    this.added.set(true);
    setTimeout(() => this.added.set(false), 1400);
  }

  savePercent() {
    const size = this.size();
    if (!size?.compare_at_price) {
      return 0;
    }
    return Math.round((1 - num(size.price) / num(size.compare_at_price)) * 100);
  }

  reviewDate(value: string) {
    return new Date(value).toLocaleDateString('en-PH', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }

  showReviews() {
    this.reviewsOpen.set(true);
    setTimeout(() => {
      document.getElementById('reviews')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 0);
  }

  toggleReviews() {
    this.reviewsOpen.update((open) => !open);
  }
}
