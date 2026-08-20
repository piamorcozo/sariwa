import { Injectable, signal } from '@angular/core';

export type ToastKind = 'ok' | 'error';

@Injectable({ providedIn: 'root' })
export class Toast {
  readonly message = signal('');
  readonly kind = signal<ToastKind>('ok');
  readonly visible = signal(false);
  private timer?: number;

  show(message: string, kind: ToastKind = 'ok') {
    this.message.set(message);
    this.kind.set(kind);
    this.visible.set(true);
    window.clearTimeout(this.timer);
    this.timer = window.setTimeout(() => this.visible.set(false), 2800);
  }
}
