import { Component, NgZone, OnDestroy, computed, effect, inject, input, signal } from '@angular/core';

const DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

@Component({
  selector: 'app-counter',
  templateUrl: './counter.html',
  styleUrl: './counter.scss',
})
export class RollingCounter implements OnDestroy {
  readonly value = input.required<number>();
  readonly fontSize = input(100);
  readonly padding = input(5);
  readonly places = input<Array<number | '.'>>([100, 10, 1]);
  readonly gap = input(10);
  readonly borderRadius = input(4);
  readonly horizontalPadding = input(8);
  readonly textColor = input('white');
  readonly fontWeight = input<string | number>(900);
  readonly gradientHeight = input(16);
  readonly gradientFrom = input('black');
  readonly gradientTo = input('transparent');

  readonly digits = DIGITS;
  readonly displayed = signal(0);
  readonly height = computed(() => this.fontSize() + this.padding());

  private readonly zone = inject(NgZone);
  private raf: number | null = null;
  private startTs: number | null = null;
  private from = 0;
  private target = 0;

  constructor() {
    effect(() => {
      this.target = this.value();
      this.startTs = null;
      this.from = this.displayed();
      if (!this.raf) {
        this.zone.runOutsideAngular(() => {
          this.raf = requestAnimationFrame(this.tick);
        });
      }
    });
  }

  ngOnDestroy() {
    if (this.raf) {
      cancelAnimationFrame(this.raf);
    }
  }

  offset(place: number | '.', number: number) {
    if (place === '.') {
      return 0;
    }
    const latest = this.placeValue(this.displayed(), place);
    const placeValue = ((latest % 10) + 10) % 10;
    let offset = (10 + number - placeValue) % 10;
    let memo = offset * this.height();
    if (offset > 5) {
      memo -= 10 * this.height();
    }
    return memo;
  }

  private placeValue(value: number, place: number) {
    const scaled = value / place;
    const nearest = Math.round(scaled);
    const tolerance = 1e-9 * Math.max(1, Math.abs(scaled));
    const normalized = Math.abs(scaled - nearest) < tolerance ? nearest : scaled;
    return Math.floor(normalized);
  }

  private tick = (ts: number) => {
    if (this.startTs === null) {
      this.startTs = ts;
      this.from = this.displayed();
    }
    const target = this.target;
    const duration = 2600;
    const t = Math.min(1, (ts - this.startTs) / duration);
    const eased = 1 - Math.pow(1 - t, 5);
    const next = this.from + (target - this.from) * eased;
    if (Math.abs(next - this.displayed()) > 0.01) {
      this.zone.run(() => this.displayed.set(next));
    } else if (t >= 1 && this.displayed() !== target) {
      this.zone.run(() => this.displayed.set(target));
    }
    if (t < 1) {
      this.raf = requestAnimationFrame(this.tick);
    } else {
      this.raf = null;
      this.startTs = null;
    }
  };
}
