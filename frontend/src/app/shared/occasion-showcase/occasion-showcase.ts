import { Component, computed, OnDestroy, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon } from '../icon/icon';

interface Petal {
  x: number;
  y: number;
  size: number;
  rot: number;
  blur: number;
  opacity: number;
  tone: number;
  front: boolean;
  dx: number;
  dy: number;
  spin: number;
  dur: number;
  delay: number;
}

interface Slide {
  key: string;
  word: string;
  caption: string;
  occasion: string;
  image: string;
  petal: string;
  bg: string;
  ink: string;
  petals: Petal[];
}

// Photographed petals carry their own colour, so `tone` only varies how light or
// deep each one sits in the scatter.
const TONES = ['brightness(1)', 'brightness(1.1) saturate(0.92)', 'brightness(0.84) saturate(1.08)'];

const SLIDES: Slide[] = [
  {
    key: 'valentines',
    word: 'Valentines',
    caption: 'Roses that say it before you do.',
    occasion: 'romance',
    image: 'occasions/valentines.png',
    petal: 'occasions/petal-valentines.png',
    bg: '#fffcf7',
    ink: '#A3243A',
    petals: [
      { x: 7, y: 76, size: 210, rot: -28, blur: 9, opacity: 0.9, tone: 0, front: true, dx: 14, dy: -18, spin: 10, dur: 15, delay: 0 },
      { x: 21, y: 28, size: 118, rot: 36, blur: 2, opacity: 1, tone: 1, front: false, dx: -12, dy: 16, spin: -14, dur: 12, delay: 1.4 },
      { x: 33, y: 63, size: 76, rot: -14, blur: 0, opacity: 1, tone: 2, front: false, dx: 10, dy: 12, spin: 18, dur: 10, delay: 0.6 },
      { x: 49, y: 10, size: 92, rot: 9, blur: 1, opacity: 1, tone: 0, front: false, dx: -8, dy: -14, spin: 12, dur: 13, delay: 2.1 },
      { x: 69, y: 22, size: 128, rot: -42, blur: 0, opacity: 1, tone: 1, front: true, dx: 16, dy: 14, spin: -10, dur: 14, delay: 0.9 },
      { x: 86, y: 54, size: 176, rot: 24, blur: 7, opacity: 0.9, tone: 2, front: true, dx: -14, dy: -16, spin: 8, dur: 16, delay: 1.8 },
      { x: 93, y: 88, size: 112, rot: -18, blur: 4, opacity: 0.95, tone: 0, front: true, dx: 12, dy: -12, spin: -16, dur: 11, delay: 0.3 },
      { x: 61, y: 90, size: 82, rot: 52, blur: 3, opacity: 0.95, tone: 1, front: true, dx: -10, dy: 14, spin: 14, dur: 12, delay: 2.6 },
    ],
  },
  {
    key: 'birthday',
    word: 'Birthday',
    caption: 'Loud color, no balloons required.',
    occasion: 'birthday',
    image: 'occasions/birthday.png',
    petal: 'occasions/petal-birthday.png',
    bg: '#fffcf7',
    ink: '#5D3585',
    petals: [
      { x: 12, y: 30, size: 194, rot: 44, blur: 8, opacity: 0.9, tone: 1, front: true, dx: -12, dy: 18, spin: -12, dur: 14, delay: 0.5 },
      { x: 27, y: 79, size: 104, rot: -22, blur: 1, opacity: 1, tone: 0, front: false, dx: 14, dy: -12, spin: 16, dur: 11, delay: 1.9 },
      { x: 39, y: 20, size: 72, rot: 16, blur: 0, opacity: 1, tone: 2, front: false, dx: -9, dy: 13, spin: -18, dur: 10, delay: 0.2 },
      { x: 58, y: 8, size: 90, rot: -36, blur: 2, opacity: 1, tone: 1, front: true, dx: 11, dy: 15, spin: 10, dur: 13, delay: 2.4 },
      { x: 74, y: 71, size: 138, rot: 26, blur: 0, opacity: 1, tone: 0, front: false, dx: -15, dy: -14, spin: 14, dur: 15, delay: 1.1 },
      { x: 91, y: 31, size: 172, rot: -12, blur: 7, opacity: 0.9, tone: 2, front: true, dx: 13, dy: 17, spin: -8, dur: 16, delay: 0.8 },
      { x: 5, y: 89, size: 122, rot: 31, blur: 5, opacity: 0.95, tone: 0, front: true, dx: -11, dy: -15, spin: 15, dur: 12, delay: 2.7 },
      { x: 67, y: 92, size: 78, rot: -50, blur: 3, opacity: 0.95, tone: 1, front: true, dx: 9, dy: 12, spin: -14, dur: 11, delay: 1.5 },
    ],
  },
  {
    key: 'justbecause',
    word: 'Just Because',
    caption: 'For the Tuesday that needed flowers.',
    occasion: 'justbecause',
    image: 'occasions/just-because.png',
    petal: 'occasions/petal-just-because.png',
    bg: '#fffcf7',
    ink: '#9A6A11',
    petals: [
      { x: 16, y: 57, size: 156, rot: -52, blur: 6, opacity: 0.9, tone: 2, front: true, dx: 15, dy: 14, spin: 12, dur: 15, delay: 1.2 },
      { x: 30, y: 13, size: 96, rot: 23, blur: 0, opacity: 1, tone: 0, front: false, dx: -10, dy: -16, spin: -15, dur: 12, delay: 0.4 },
      { x: 45, y: 85, size: 80, rot: -19, blur: 3, opacity: 0.95, tone: 1, front: true, dx: 12, dy: 11, spin: 18, dur: 10, delay: 2.2 },
      { x: 62, y: 29, size: 112, rot: 39, blur: 1, opacity: 1, tone: 2, front: false, dx: -13, dy: 15, spin: -10, dur: 13, delay: 0.9 },
      { x: 80, y: 11, size: 132, rot: -29, blur: 4, opacity: 1, tone: 0, front: true, dx: 10, dy: -13, spin: 14, dur: 14, delay: 1.7 },
      { x: 95, y: 65, size: 188, rot: 17, blur: 9, opacity: 0.9, tone: 1, front: true, dx: -14, dy: 16, spin: -9, dur: 16, delay: 0.1 },
      { x: 4, y: 19, size: 118, rot: 46, blur: 5, opacity: 0.95, tone: 2, front: true, dx: 13, dy: 12, spin: 16, dur: 12, delay: 2.9 },
      { x: 72, y: 89, size: 88, rot: -9, blur: 2, opacity: 0.95, tone: 0, front: true, dx: -9, dy: -14, spin: -13, dur: 11, delay: 2.0 },
    ],
  },
];

@Component({
  selector: 'app-occasion-showcase',
  imports: [RouterLink, Icon],
  templateUrl: './occasion-showcase.html',
  styleUrl: './occasion-showcase.scss',
})
export class OccasionShowcase implements OnInit, OnDestroy {
  readonly slides = SLIDES;
  readonly index = signal(0);
  readonly leaving = signal(-1);
  readonly forward = signal(true);
  readonly paused = signal(false);

  private timer?: ReturnType<typeof setInterval>;
  private settle?: ReturnType<typeof setTimeout>;

  readonly current = computed(() => this.slides[this.index()]);

  ngOnInit() {
    this.restart();
  }

  ngOnDestroy() {
    clearInterval(this.timer);
    clearTimeout(this.settle);
  }

  go(step: number) {
    const total = this.slides.length;
    this.goTo((this.index() + step + total) % total, step > 0);
  }

  select(next: number) {
    this.goTo(next, next > this.index());
  }

  private goTo(next: number, forward: boolean) {
    if (next === this.index()) {
      return;
    }
    this.forward.set(forward);
    this.leaving.set(this.index());
    this.index.set(next);
    clearTimeout(this.settle);
    this.settle = setTimeout(() => this.leaving.set(-1), 800);
    this.restart();
  }

  private restart() {
    clearInterval(this.timer);
    this.timer = setInterval(() => {
      if (!this.paused()) {
        this.go(1);
      }
    }, 6000);
  }

  petalFilter(petal: Petal) {
    return `blur(${petal.blur}px) ${TONES[petal.tone]}`;
  }
}
