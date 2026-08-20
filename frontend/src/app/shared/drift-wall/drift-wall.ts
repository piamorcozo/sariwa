import {
  AfterViewInit,
  Component,
  ElementRef,
  NgZone,
  OnDestroy,
  QueryList,
  ViewChild,
  ViewChildren,
  computed,
  inject,
  input,
  signal,
} from '@angular/core';
import { DriftTile } from './drift-wall.models';

const columnFactor = (index: number, variance: number) => {
  const pseudo = ((index * 0.6180339887 + 0.35) % 1) * 2 - 1;
  return 1 + variance * pseudo;
};

@Component({
  selector: 'app-drift-wall',
  templateUrl: './drift-wall.html',
  styleUrl: './drift-wall.scss',
})
export class DriftWall implements AfterViewInit, OnDestroy {
  readonly items = input.required<DriftTile[]>();
  readonly columns = input(5);
  readonly tileWidth = input(200);
  readonly tileHeight = input(132);
  readonly gap = input(18);
  readonly radius = input(14);
  readonly tilt = input(16);
  readonly turn = input(-14);
  readonly roll = input(0);
  readonly perspective = input(1200);
  readonly depth = input(120);
  readonly speed = input(42);
  readonly direction = input<'up' | 'down'>('up');
  readonly variance = input(0.45);
  readonly parallax = input(0.6);
  readonly pauseOnHover = input(false);
  readonly lift = input(64);
  readonly fade = input(0.6);
  readonly dim = input(0.55);
  readonly grayscale = input(false);
  readonly overlayColor = input('#2c3a2b');

  @ViewChild('wall', { static: true }) private wall?: ElementRef<HTMLElement>;
  @ViewChild('plane', { static: true }) private plane?: ElementRef<HTMLElement>;
  @ViewChildren('tracks') private tracks?: QueryList<ElementRef<HTMLElement>>;

  readonly containerHeight = signal(600);
  readonly activeId = signal<string | null>(null);
  readonly reduced = signal(false);

  readonly columnItems = computed(() => {
    const columns = Math.max(1, this.columns());
    const items = this.items();
    const cols: DriftTile[][] = Array.from({ length: columns }, () => []);
    items.forEach((item, i) => cols[i % columns].push(item));
    return cols.map((col) => (col.length ? col : items.slice(0, 1)));
  });

  readonly columnMeta = computed(() => {
    const unit = this.tileHeight() + this.gap();
    const height = this.containerHeight();
    return this.columnItems().map((col) => {
      const copyHeight = Math.max(unit, col.length * unit);
      const copies = Math.max(2, Math.ceil((height * 1.6) / copyHeight) + 1);
      return { copyHeight, copies };
    });
  });

  readonly copies = computed(() => this.columnMeta().map((meta) => Array.from({ length: meta.copies }, (_, i) => i)));

  private readonly offsets: number[] = [];
  private readonly velocities: number[] = [];
  private hoveredCol = -1;
  private wallHovered = false;
  private pointer = { x: 0, y: 0 };
  private pointerDamped = { x: 0, y: 0 };
  private lastTs: number | null = null;
  private raf: number | null = null;
  private resize?: ResizeObserver;
  private motion?: MediaQueryList;
  private readonly zone = inject(NgZone);

  ngAfterViewInit() {
    const host = this.wall?.nativeElement;
    if (host) {
      this.resize = new ResizeObserver(([entry]) => {
        this.zone.run(() => this.containerHeight.set(entry.contentRect.height || 600));
      });
      this.resize.observe(host);
      this.containerHeight.set(host.getBoundingClientRect().height || 600);
    }

    this.motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    this.reduced.set(this.motion.matches);
    this.motion.addEventListener('change', this.onMotion);

    this.resetMotionState();
    this.zone.runOutsideAngular(() => {
      this.raf = requestAnimationFrame(this.animate);
    });
  }

  ngOnDestroy() {
    this.resize?.disconnect();
    this.motion?.removeEventListener('change', this.onMotion);
    if (this.raf) {
      cancelAnimationFrame(this.raf);
    }
  }

  onPointerEnter() {
    this.wallHovered = true;
  }

  onPointerLeave() {
    this.wallHovered = false;
    this.pointer = { x: 0, y: 0 };
    this.release();
  }

  onPointerMove(event: PointerEvent) {
    const rect = this.wall?.nativeElement.getBoundingClientRect();
    if (!rect) {
      return;
    }
    if (this.parallax() > 0 && !this.reduced()) {
      this.pointer = {
        x: (event.clientX - rect.left) / rect.width - 0.5,
        y: (event.clientY - rect.top) / rect.height - 0.5,
      };
    }
    const hit = document.elementFromPoint(event.clientX, event.clientY);
    const tile = hit?.closest?.('[data-tile-id]') as HTMLElement | null;
    if (!tile) {
      return;
    }
    const id = tile.dataset['tileId'] ?? null;
    if (id === this.activeId()) {
      return;
    }
    this.hoveredCol = Number(tile.dataset['col']);
    this.activeId.set(id);
  }

  activate(id: string, index: number) {
    this.hoveredCol = index;
    this.activeId.set(id);
  }

  release() {
    this.hoveredCol = -1;
    this.activeId.set(null);
  }

  private onMotion = (event: MediaQueryListEvent) => {
    this.reduced.set(event.matches);
  };

  private resetMotionState() {
    const meta = this.columnMeta();
    this.offsets.length = 0;
    this.velocities.length = 0;
    meta.forEach((item, c) => {
      this.offsets[c] = item.copyHeight * ((c * 0.37) % 1);
      this.velocities[c] = 0;
    });
  }

  private baseVelocity(index: number) {
    const dirSign = this.direction() === 'up' ? 1 : -1;
    const altSign = index % 2 === 0 ? 1 : -1;
    return this.speed() * columnFactor(index, this.variance()) * dirSign * altSign;
  }

  private applyPlaneTransform(px: number, py: number) {
    const plane = this.plane?.nativeElement;
    if (!plane) {
      return;
    }
    plane.style.transform =
      `translate(-50%, -50%) scale(1.18) ` +
      `rotateX(${this.tilt() + py}deg) rotateY(${this.turn() + px}deg) rotateZ(${this.roll()}deg) ` +
      `translateZ(${-this.depth()}px)`;
  }

  private animate = (ts: number) => {
    if (this.lastTs === null) {
      this.lastTs = ts;
    }
    const dt = Math.min(0.05, Math.max(0, ts - this.lastTs) / 1000);
    this.lastTs = ts;

    const meta = this.columnMeta();
    if (this.offsets.length !== meta.length) {
      this.resetMotionState();
    }

    const maxTilt = this.parallax() * 8;
    const targetX = this.pointer.x * maxTilt;
    const targetY = -this.pointer.y * maxTilt;
    const damp = 1 - Math.exp(-dt / 0.12);
    this.pointerDamped.x += (targetX - this.pointerDamped.x) * damp;
    this.pointerDamped.y += (targetY - this.pointerDamped.y) * damp;
    this.applyPlaneTransform(this.pointerDamped.x, this.pointerDamped.y);

    const els = this.tracks?.toArray() ?? [];
    if (!this.reduced()) {
      for (let c = 0; c < els.length; c++) {
        const colMeta = meta[c];
        if (!colMeta) {
          continue;
        }
        const paused = this.wallHovered && this.pauseOnHover();
        const factor = paused || this.hoveredCol === c ? 0 : 1;
        const target = this.baseVelocity(c) * factor;
        const ease = 1 - Math.exp(-dt / (target === 0 ? 0.16 : 0.28));
        this.velocities[c] += (target - (this.velocities[c] ?? 0)) * ease;
        let next = (this.offsets[c] ?? 0) + this.velocities[c] * dt;
        next = ((next % colMeta.copyHeight) + colMeta.copyHeight) % colMeta.copyHeight;
        this.offsets[c] = next;
        els[c].nativeElement.style.transform = `translate3d(0, ${-next}px, 0)`;
      }
    } else {
      for (let c = 0; c < els.length; c++) {
        const colMeta = meta[c];
        if (colMeta) {
          els[c].nativeElement.style.transform = `translate3d(0, ${-(this.offsets[c] ?? 0)}px, 0)`;
        }
      }
    }

    this.raf = requestAnimationFrame(this.animate);
  };
}
